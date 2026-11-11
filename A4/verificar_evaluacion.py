"""Pruebas de evaluación/exportación con un BERT pequeño, sin descargar modelos."""
import hashlib
import ast
import json
import shutil
import unittest
import uuid
from pathlib import Path
from types import SimpleNamespace
from contextlib import contextmanager

import numpy as np
import torch
from transformers import BertConfig, BertForSequenceClassification, BertTokenizerFast
from evaluation_runtime import audit_export, compare_probabilities, probability_metrics

ROOT = Path(__file__).resolve().parent / ".test_tmp"


@contextmanager
def fixture():
    torch.set_num_threads(1)
    ROOT.mkdir(exist_ok=True)
    root = ROOT / ("evaluation_" + uuid.uuid4().hex)
    root.mkdir()
    try:
        vocab = ["[PAD]", "[UNK]", "[CLS]", "[SEP]", "[MASK]", "word", "title"]
        (root / "vocab.txt").write_text("\n".join(vocab), encoding="utf-8")
        tokenizer = BertTokenizerFast(vocab_file=str(root / "vocab.txt"))
        config = BertConfig(vocab_size=len(tokenizer), hidden_size=16,
            num_hidden_layers=1, num_attention_heads=2, intermediate_size=24, num_labels=3)
        config._attn_implementation = "eager"
        model = BertForSequenceClassification(config)
        checkpoint, exported = root / "checkpoint", root / "exported"
        model.save_pretrained(checkpoint)
        model.save_pretrained(exported)
        classifier = SimpleNamespace(root=exported, model=model.eval(), tokenizer=tokenizer, device="cpu")
        data = [{"input_ids": [2] + [5] * (i + 1) + [3],
            "attention_mask": [1] * (i + 3), "labels": i % 3} for i in range(5)]
        yield root, checkpoint, classifier, data
    finally:
        assert root.resolve().is_relative_to(ROOT.resolve())
        shutil.rmtree(root)


def hashes(root):
    result = {}
    for p in root.rglob("*.safetensors"):
        with p.open("rb") as stream:
            result[str(p)] = hashlib.file_digest(stream, "sha256").hexdigest()
    return result


class EvaluationTests(unittest.TestCase):
    def test_generated_report_preserves_legacy_and_logs_class_metrics(self):
        import pandas as pd
        import matplotlib
        matplotlib.use("Agg")
        import matplotlib.pyplot as plt
        from sklearn.metrics import classification_report, confusion_matrix

        with fixture() as (root, _, _, _):
            legacy = root / "base/validation_scores.json"
            legacy.parent.mkdir()
            legacy.write_text('{"f1_macro": 0.847831}', encoding="utf-8")
            before = legacy.read_bytes()
            labels = [f"class_{i}" for i in range(9)]
            rows = [{"inst_key": str(i), "label": labels[i % 9], "label_source": "pre_label"} for i in range(18)]
            probs = np.eye(9)[np.arange(18) % 9] * .9 + .1 / 9
            probs[0] = probs[1]
            notebook = json.loads(Path(__file__).with_name("A4_SciBERT_G15_Colab_A100.ipynb").read_text(encoding="utf-8"))
            code = next(c["source"] for c in notebook["cells"] if c["cell_type"] == "code" and "def report_predictions(" in c["source"])
            tree = ast.parse(code)
            tree.body = [node for node in tree.body if isinstance(node, ast.FunctionDef) and node.name == "report_predictions"]
            logged = []
            ns = dict(np=np, pd=pd, plt=plt, classification_report=classification_report,
                confusion_matrix=confusion_matrix, LABELS=labels, ID2LABEL=dict(enumerate(labels)),
                LABEL2ID={label: i for i, label in enumerate(labels)}, EVALUATION_ROOT=root / "evaluations/new",
                save_json=lambda path, value: path.write_text(json.dumps(value), encoding="utf-8"),
                display=lambda _: None,
                compute_metrics=lambda p: probability_metrics(p.label_ids, p.predictions),
                tracking=SimpleNamespace(metrics=lambda run, values: logged.append((run, values)), parent=lambda _: "parent"))
            exec(compile(tree, "<generated-report>", "exec"), ns)
            result = ns["report_predictions"]("base", "validation", rows, probs, "evaluation")
            reports = root / "evaluations/new/base"
            self.assertEqual(result["precision"], "fp32")
            self.assertEqual(len(pd.read_csv(reports / "validation_errors.csv")), 1)
            self.assertEqual(len(pd.read_csv(reports / "validation_per_class.csv")), 9)
            self.assertEqual(before, legacy.read_bytes())
            self.assertTrue(any("validation/class_0/recall" in values for _, values in logged))
            self.assertTrue(any("validation_fp32_f1_macro" in values for _, values in logged))

    def test_full_validation_fp32_export_and_bf16_replay(self):
        with fixture() as (root, checkpoint, classifier, data):
            before = hashes(root)
            probs, replayed, audit = audit_export(classifier, data, list(map(str, range(5))),
                checkpoint, root / "evaluation", 2, 42, "bf16")
            self.assertEqual(probs.shape, (5, 3))
            self.assertEqual(audit["export_check"], "passed_full_validation")
            self.assertEqual(audit["checkpoint_vs_export_fp32"]["label_disagreements"], 0)
            self.assertEqual(audit["trainer_vs_export_fp32"]["n"], 5)
            self.assertEqual(before, hashes(root))
            self.assertTrue(np.isfinite(list(probability_metrics([row["labels"] for row in data], replayed).values())).all())
            # Un modelo exportado diferente tiene que detener la auditoría.
            with torch.no_grad():
                classifier.model.classifier.bias[0].add_(10)
            with self.assertRaisesRegex(ValueError, "no reproduce"):
                audit_export(classifier, data, list(map(str, range(5))), checkpoint,
                    root / "bad_evaluation", 2, 42, "fp32")

    def test_missing_checkpoint_is_explicit(self):
        with fixture() as (root, checkpoint, classifier, data):
            _, _, audit = audit_export(classifier, data, list(map(str, range(5))), root / "absent",
                root / "evaluation", 2, 42, "fp32")
            self.assertEqual(audit["export_check"], "pending_checkpoint_missing")

    def test_probability_comparison_reports_changed_keys_and_rejects_bad_data(self):
        result = compare_probabilities([[.9, .1], [.4, .6]], [[.8, .2], [.7, .3]], ["a", "b"])
        self.assertEqual(result["changed_inst_keys"], ["b"])
        with self.assertRaises(ValueError):
            compare_probabilities([[.9, .1]], [[.8, np.nan]], ["a"])
        with self.assertRaises(ValueError):
            compare_probabilities([[.9, .1]], [[.8, .1]], ["a"])


if __name__ == "__main__":
    unittest.main(verbosity=2)
