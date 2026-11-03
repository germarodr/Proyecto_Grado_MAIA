"""Verificación local: contratos reales, aislamiento y pipeline con BERT diminuto aleatorio.

No descarga modelos ni evalúa la calidad de SciBERT. Ejecutar desde la raíz:
    python A4/verificar_notebook.py
Requiere pandas, numpy, nbformat, torch y transformers para la prueba de humo.
"""
import ast
import collections
import hashlib
import importlib.util
import inspect
import json
import linecache
import unittest
import shutil
import uuid
from contextlib import contextmanager
from pathlib import Path

import numpy as np
import pandas as pd
import nbformat

ROOT = Path(__file__).resolve().parents[1]
NB_PATH = Path(__file__).with_name("A4_SciBERT_G15_Colab_A100.ipynb")
NB = json.loads(NB_PATH.read_text(encoding="utf-8"))
CODES = [cell["source"] for cell in NB["cells"] if cell["cell_type"] == "code"]
LABELS = ["Background", "Gap", "Basis", "Comparison", "Application",
          "Improvement/Modification", "Evidence", "Identification of the Originator", "Further Reading"]


@contextmanager
def workspace_temp():
    temp_root = (ROOT / "A4/.test_tmp").resolve()
    temp_root.mkdir(exist_ok=True)
    directory = temp_root / uuid.uuid4().hex
    directory.mkdir()
    if not directory.resolve().is_relative_to(temp_root):
        raise ValueError("Directorio temporal fuera del workspace")
    try:
        yield str(directory)
    finally:
        if not directory.resolve().is_relative_to(temp_root):
            raise ValueError("Limpieza fuera del workspace")
        shutil.rmtree(directory)


def functions_namespace():
    ns = dict(Path=Path, json=json, hashlib=hashlib, collections=collections,
              np=np, pd=pd, LABELS=LABELS, LABEL2ID={x: i for i, x in enumerate(LABELS)},
              ID2LABEL=dict(enumerate(LABELS)))
    for i, code in enumerate(CODES):
        filename = f"<a4-cell-{i}>"
        linecache.cache[filename] = (len(code), None, code.splitlines(keepends=True), filename)
        tree = ast.parse(code)
        tree.body = [node for node in tree.body if isinstance(node, ast.FunctionDef)]
        exec(compile(tree, filename, "exec"), ns)
    return ns


class NotebookTests(unittest.TestCase):
    def test_schema_and_description_code_alternation(self):
        nbformat.validate(nbformat.read(NB_PATH, as_version=4))
        self.assertEqual(len(NB["cells"]), 32)
        for i, cell in enumerate(NB["cells"]):
            self.assertEqual(cell["cell_type"], "markdown" if i % 2 == 0 else "code")
            if cell["cell_type"] == "code":
                ast.parse(cell["source"])
                self.assertEqual(cell["outputs"], [])

    def test_real_g15_contract_and_all_isolation_variants(self):
        for variant, expected in [("V0", 31265), ("V1", 16564), ("V2", 15349)]:
            with self.subTest(variant=variant), workspace_temp() as tmp:
                ns = functions_namespace()
                ns.update(IDS_DIR=ROOT / "Folder_trabajo_Equipos_14_y_15/TrainingData_Grupo15",
                          POOL_PATH=Path(tmp) / "absent_pool", OUTPUT_ROOT=Path(tmp),
                          VARIANT=variant, GOLD_FILES=[], GOLD_FINAL=False, RUN_TEST=False,
                          SPLIT_SEED="G15-A4-split-v1", VAL_FRAC=.1, display=lambda x: None)
                for i in range(3, 7):
                    exec(compile(CODES[i], f"<integration-{i}>", "exec"), ns)
                self.assertEqual(len(ns["eligible"]), expected)
                self.assertEqual(set(ns["counts"].index), set(LABELS))
                self.assertTrue((ns["counts"] > 0).all().all())
                self.assertEqual(len(ns["train_rows"]) + len(ns["val_rows"]) +
                                 len(ns["tr_before_purge"]) - len(ns["train_rows"]), expected)
                summary = {"variant": variant, "eligible": expected,
                           "train": len(ns["train_rows"]), "validation": len(ns["val_rows"]),
                           "purged_train_for_validation": len(ns["tr_before_purge"]) - len(ns["train_rows"])}
                print("VERIFIED_SPLIT", json.dumps(summary))

    def test_gold_changes_labels_but_never_adds_own_test(self):
        ns = functions_namespace()
        with workspace_temp() as tmp:
            root = Path(tmp)
            a, b, own = "c1|0|1-2|d1", "c2|0|1-2|d2", "c3|0|1-2|d3"
            gold_file = root / "gold.jsonl"
            gold_file.write_text("\n".join(json.dumps({"inst_key": k, "gold_primary": label})
                                           for k, label in [(a, "Basis"), (b, "unclear"), (own, "Evidence")] ))
            ns.update(GOLD_FILES=[gold_file], OUTPUT_ROOT=root, input_hashes={}, RUN_TEST=False,
                      eligible=[{"inst_key": a, "primary_pre_label": "Application"},
                                {"inst_key": b, "primary_pre_label": "Background"}])
            exec(CODES[5], ns)
            self.assertEqual([r["inst_key"] for r in ns["labeled"]], [a])
            self.assertEqual(ns["labeled"][0]["label"], "Basis")
            self.assertEqual(ns["labeled"][0]["label_source"], "human_gold")
            self.assertEqual(ns["removed_unclear"], [b])
            with gold_file.open("a") as f:
                f.write("\n" + json.dumps({"inst_key": a, "gold_primary": "Gap"}))
            with self.assertRaisesRegex(ValueError, "conflictivo"):
                exec(CODES[5], ns)

    def test_missing_text_stops_and_adapter_is_strict(self):
        ns = functions_namespace()
        ns.update(BATCH_FIELDS={"inst_key": "inst_key", "context": "citation_context",
                                "title": "cited_title", "abstract": "cited_abstract", "chunks": "top3_chunks"},
                  CHUNK_FIELDS={"text": "text", "section": "section"})
        row = {"inst_key": "c|0|1-2|d", "citation_context": "We use [[TARGET]] here.",
               "cited_title": "A title", "cited_abstract": "An abstract",
               "top3_chunks": [{"text": "A passage", "section": "Methods"} for _ in range(3)]}
        normalized = ns["normalize_batch"](row)
        self.assertEqual(len(normalized["chunks"]), 3)
        missing_sections = {**row, "top3_chunks": [{"text": "A passage", "section": ""} for _ in range(3)]}
        self.assertTrue(all(ch["section_missing"] and ch["section"] == "Unknown"
                            for ch in ns["normalize_batch"](missing_sections)["chunks"]))
        for invalid in [{**row, "top3_chunks": []}, {**row, "cited_abstract": ""},
                        {**row, "citation_context": "No target"}]:
            with self.assertRaises(ValueError):
                ns["normalize_batch"](invalid)
        with self.assertRaises(KeyError):
            ns["field_at"]({"cited": {}}, "cited.title")
        with workspace_temp() as tmp:
            ns.update(BATCH_DIR=Path(tmp), splits={"train": [{"source_batch": "missing"}]})
            with self.assertRaisesRegex(FileNotFoundError, "Faltan lotes"):
                exec(CODES[7], ns)

    def test_real_batches_reconstruct_training_and_all_test_ids(self):
        batches = ROOT / "A4/a2/batches_norw"
        if not batches.exists():
            self.skipTest("Lotes privados no disponibles en este checkout")
        ns = functions_namespace()
        ns.update(BATCH_FIELDS={"inst_key": "inst_key", "context": "context",
                                "title": "cited_title", "abstract": "cited_abstract", "chunks": "top3"},
                  CHUNK_FIELDS={"text": "text", "section": "section"})
        ids = ROOT / "Folder_trabajo_Equipos_14_y_15/TrainingData_Grupo15"
        rows = list(ns["read_jsonl"](ids / "training_v1_G15.jsonl"))
        rows += list(ns["read_jsonl"](ids / "test_set_ids_G15.jsonl"))
        required = {r["inst_key"]: r["source_batch"] for r in rows}
        found = set()
        missing_sections = 0
        for batch in sorted(set(required.values())):
            seen = set()
            for raw in ns["read_jsonl"](batches / f"{batch}.jsonl"):
                key = raw["inst_key"]
                self.assertNotIn(key, seen)
                seen.add(key)
                if required.get(key) == batch:
                    example = ns["normalize_batch"](raw)
                    missing_sections += int(any(ch["section_missing"] for ch in example["chunks"]))
                    found.add(key)
        self.assertEqual(found, set(required))
        self.assertEqual(len(found), 34775)
        print("VERIFIED_TEXTS", {"reconstructed": len(found), "rows_with_missing_section": missing_sections})

    def test_real_tokenizer_gradient_and_export_roundtrip(self):
        import torch
        from transformers import BertTokenizerFast, BertConfig, BertForSequenceClassification
        ns = functions_namespace()
        with workspace_temp() as tmp:
            root = Path(tmp)
            vocab = ["[PAD]", "[UNK]", "[CLS]", "[SEP]", "[MASK]", "word", "title", "abstract",
                     "section", "passage", "methods", ":", "."]
            (root / "vocab.txt").write_text("\n".join(vocab), encoding="utf-8")
            vocab_kw = "vocab_file" if "vocab_file" in inspect.signature(BertTokenizerFast.__init__).parameters else "vocab"
            tok = BertTokenizerFast(**{vocab_kw: str(root / "vocab.txt")}, do_lower_case=True)
            self.assertEqual(len(tok), len(vocab))
            tok.add_special_tokens({"additional_special_tokens": ["[[TARGET]]", "[CITE]", "[FORMULA]", "[FIGURE]", "[TABLE]"]})
            source = "import json\nfrom pathlib import Path\nimport torch\nfrom transformers import AutoTokenizer, AutoModelForSequenceClassification\n"
            tree = ast.parse(next(code for code in CODES if "INFERENCE_TEMPLATE =" in code))
            assignment = next(n for n in tree.body if isinstance(n, ast.Assign) and
                              any(isinstance(t, ast.Name) and t.id == "INFERENCE_TEMPLATE" for t in n.targets))
            template = ast.literal_eval(assignment.value)
            encoder_source = inspect.getsource(ns["fair_caps"]) + "\n" + inspect.getsource(ns["encode_example"])
            source = template.replace("__ENCODER__", encoder_source)
            for target_position in (0, 10, 500):
                example = {"context": "word " * target_position + "[[TARGET]] " + "word " * (600 - target_position),
                           "title": "word " * 100, "abstract": "word " * 700,
                           "chunks": [{"section": "Methods", "text": "word " * n} for n in (3, 400, 600)]}
                for config in ("base", "fragmentos"):
                    features, stats = ns["encode_example"](example, config, tok)
                    self.assertLessEqual(len(features["input_ids"]), 512)
                    self.assertEqual(features["input_ids"].count(tok.convert_tokens_to_ids("[[TARGET]]")), 1)
                    self.assertEqual(stats["context_kept"], 192)
                    if config == "fragmentos":
                        self.assertTrue(all(stats[f"chunk{i}_kept"] > 0 for i in range(1, 4)))
            config = BertConfig(vocab_size=len(tok), hidden_size=24, num_hidden_layers=1,
                                num_attention_heads=4, intermediate_size=32,
                                num_labels=9, id2label=ns["ID2LABEL"], label2id=ns["LABEL2ID"])
            config._attn_implementation = "eager"
            model = BertForSequenceClassification(config)
            optim = torch.optim.AdamW(model.parameters(), lr=1e-3)
            features, _ = ns["encode_example"](example, "base", tok)
            batch = {k: torch.tensor([v]) for k, v in features.items()}
            old = model.classifier.weight.detach().clone()
            loss = model(**batch, labels=torch.tensor([2])).loss
            loss.backward()
            optim.step()
            self.assertTrue(torch.isfinite(loss))
            self.assertFalse(torch.equal(old, model.classifier.weight))
            model.eval()
            with torch.inference_mode():
                expected = model(**batch).logits.softmax(-1)[0].numpy()
            model.save_pretrained(root)
            tok.save_pretrained(root)
            (root / "input_policy.json").write_text(json.dumps({"config": "base", "max_length": 512, "context_budget": 192}))
            (root / "inference.py").write_text(source, encoding="utf-8")
            spec = importlib.util.spec_from_file_location("a4_test_export", root / "inference.py")
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
            clf = module.CitationClassifier(root, device="cpu")
            output = clf.predict(example)
            actual = [output["scores"][x] for x in LABELS]
            self.assertTrue(np.allclose(expected, actual, atol=1e-6))
            self.assertAlmostEqual(sum(actual), 1, places=6)
            self.assertFalse(output["score_calibrated"])
            print("VERIFIED_SMOKE", {"loss": float(loss.detach()), "export_roundtrip": True,
                                     "model": "BERT aleatorio diminuto, no SciBERT"})


if __name__ == "__main__":
    unittest.main(verbosity=2)
