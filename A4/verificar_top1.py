"""Pruebas locales de la ablación Top-1 y del paquete diagnóstico ciego."""
import ast
import inspect
import json
import shutil
import unittest
import uuid
from pathlib import Path
import numpy as np
import pandas as pd
import nbformat
from transformers import BertTokenizerFast
from revision_manual_runtime import create_manual_review

ROOT = Path(__file__).resolve().parent
LABELS = ["Background", "Gap", "Basis", "Comparison", "Application", "Improvement/Modification",
          "Evidence", "Identification of the Originator", "Further Reading"]


class Top1Tests(unittest.TestCase):
    def test_one_variant_and_original_training_arguments(self):
        baseline = nbformat.read(ROOT / "A4_SciBERT_G15_Colab_A100.ipynb", as_version=4)
        top1 = nbformat.read(ROOT / "A4_SciBERT_G15_Top1_Colab_A100.ipynb", as_version=4)
        nbformat.validate(top1)
        self.assertEqual(len(top1.cells), 36)
        for i, cell in enumerate(top1.cells):
            self.assertEqual(cell.cell_type, "markdown" if i % 2 == 0 else "code")
            if cell.cell_type == "code":
                ast.parse(cell.source)
                self.assertEqual(cell.outputs, [])
        def arguments(nb):
            source = next(c.source for c in nb.cells if c.cell_type == "code" and "INFERENCE_TEMPLATE =" in c.source)
            return ast.dump(next(node for node in ast.walk(ast.parse(source)) if isinstance(node, ast.Call)
                and isinstance(node.func, ast.Name) and node.func.id == "TrainingArguments"))
        self.assertEqual(arguments(baseline), arguments(top1))
        setup = next(c.source for c in top1.cells if c.cell_type == "code" and "RUN_ID =" in c.source)
        values = {}
        for node in ast.parse(setup).body:
            if isinstance(node, ast.Assign) and isinstance(node.targets[0], ast.Name):
                try:
                    values[node.targets[0].id] = ast.literal_eval(node.value)
                except (ValueError, TypeError):
                    pass
        self.assertEqual(values["CONFIGS"], ["fragmentos_top1"])
        self.assertFalse(values["RUN_TEST"])
        self.assertEqual(values["RUN_ID"], "g15_a4_v0_seed42_top1_01")

    def test_top1_ignores_other_passages_and_preserves_context(self):
        temp = ROOT / ".test_tmp" / ("top1_" + uuid.uuid4().hex)
        temp.mkdir(parents=True)
        try:
            vocab = ["[PAD]", "[UNK]", "[CLS]", "[SEP]", "[MASK]", "word", "a", "b", "c", "methods", "section", "passage", ":"]
            (temp / "vocab.txt").write_text("\n".join(vocab), encoding="utf-8")
            keyword = "vocab_file" if "vocab_file" in inspect.signature(BertTokenizerFast.__init__).parameters else "vocab"
            tok = BertTokenizerFast(**{keyword: str(temp / "vocab.txt")})
            tok.add_special_tokens({"additional_special_tokens": ["[[TARGET]]"]})
            nb = nbformat.read(ROOT / "A4_SciBERT_G15_Top1_Colab_A100.ipynb", as_version=4)
            source = next(c.source for c in nb.cells if c.cell_type == "code" and "def encode_example(" in c.source)
            tree = ast.parse(source)
            tree.body = [node for node in tree.body if isinstance(node, ast.FunctionDef) and node.name in {"encode_example", "fair_caps"}]
            ns = {}
            exec(compile(tree, "<top1-encoder>", "exec"), ns)
            example = {"context": "word " * 300 + "[[TARGET]] " + "word " * 300,
                       "chunks": [{"text": token * 600, "section": "Methods"} for token in ["a ", "b ", "c "]]}
            encode = ns["encode_example"]
            top, stats = encode(example, "fragmentos_top1", tok)
            three, old_stats = encode(example, "fragmentos", tok)
            changed = {**example, "chunks": [example["chunks"][0]] + [{"text": "word " * 800, "section": "Methods"}] * 2}
            top_changed, _ = encode(changed, "fragmentos_top1", tok)
            self.assertEqual(top, top_changed)
            self.assertNotEqual(top, three)
            self.assertLessEqual(len(top["input_ids"]), 512)
            self.assertEqual(top["input_ids"].count(tok.convert_tokens_to_ids("[[TARGET]]")), 1)
            self.assertEqual(stats["context_kept"], old_stats["context_kept"])
            self.assertGreater(stats["chunk1_kept"], old_stats["chunk1_kept"])
            self.assertNotIn("chunk2_kept", stats)
        finally:
            assert temp.resolve().is_relative_to((ROOT / ".test_tmp").resolve())
            shutil.rmtree(temp)

    def test_manual_review_is_blind_reproducible_and_has_twenty_cases(self):
        temp = ROOT / ".test_tmp" / ("review_" + uuid.uuid4().hex)
        temp.mkdir(parents=True)
        try:
            source = temp / "baseline"
            for config in ["base", "fragmentos"]:
                (source / config).mkdir(parents=True)
            rows, predictions, texts = [], [], {}
            for focus in ["Evidence", "Improvement/Modification"]:
                for i in range(10):
                    key = f"{focus}_{i}"
                    label = "Background" if 5 <= i < 8 else focus
                    pred = "Background" if i < 5 else focus
                    rows.append({"inst_key": key, "label": label})
                    predictions.append({"inst_key": key, "gold_or_prelabel": label, "predicted_label": pred})
                    texts[key] = {"context": "Claim [[TARGET]] <script>x</script>", "title": "Title", "abstract": "Abstract",
                                  "chunks": [{"text": "Passage", "section": "Methods"}] * 3}
            for config in ["base", "fragmentos"]:
                pd.DataFrame(predictions).to_csv(source / config / "validation_predictions.csv", index=False)
            first = create_manual_review(temp / "first", source, rows, texts, LABELS)
            second = create_manual_review(temp / "second", source, rows, texts, LABELS)
            blind = pd.read_csv(first / "revision_manual.csv")
            self.assertEqual(len(blind), 20)
            self.assertTrue(blind.primary_label.isna().all())
            self.assertFalse(any("predicted" in name or "prelabel" in name or "focus" in name for name in blind.columns))
            self.assertEqual((first / "_analisis/clave_modelos.csv").read_bytes(), (second / "_analisis/clave_modelos.csv").read_bytes())
            key = pd.read_csv(first / "_analisis/clave_modelos.csv")
            self.assertEqual(key.groupby("focus").size().tolist(), [10, 10])
            self.assertNotIn("<script>", (first / "casos_revision.html").read_text(encoding="utf-8"))
            self.assertTrue(json.loads((first / "manifest.json").read_text())["not_final_gold"])
        finally:
            assert temp.resolve().is_relative_to((ROOT / ".test_tmp").resolve())
            shutil.rmtree(temp)


if __name__ == "__main__":
    unittest.main(verbosity=2)
