"""Controles de la corrida V2; no descarga SciBERT ni requiere GPU/Drive."""
import ast
import copy
import json
import unittest
from pathlib import Path

import nbformat
import pandas as pd

from v2_comparison_runtime import compare_v0_v2, load_v0_reference, validate_v2_spec
from verificar_notebook import functions_namespace, workspace_temp, ROOT, LABELS, CODES

NOTEBOOK = Path(__file__).with_name("A4_SciBERT_G15_V2_Colab_A100.ipynb")


class V2Tests(unittest.TestCase):
    def test_notebook_contract_and_same_training_arguments(self):
        notebook = nbformat.read(NOTEBOOK, as_version=4)
        nbformat.validate(notebook)
        self.assertEqual(len(notebook.cells), 34)
        for i, cell in enumerate(notebook.cells):
            self.assertEqual(cell.cell_type, "markdown" if i % 2 == 0 else "code")
            if cell.cell_type == "code":
                ast.parse(cell.source)
                self.assertEqual(cell.outputs, [])
        setup = next(c.source for c in notebook.cells if c.id == "a4-003")
        values = {}
        for node in ast.parse(setup).body:
            if isinstance(node, ast.Assign) and isinstance(node.targets[0], ast.Name):
                try:
                    values[node.targets[0].id] = ast.literal_eval(node.value)
                except (TypeError, ValueError):
                    pass
        self.assertEqual(values["VARIANT"], "V2")
        self.assertEqual(values["CONFIGS"], ["base", "fragmentos"])
        self.assertEqual(values["RUN_ID"], "g15_a4_v2_seed42_mlflow_01")
        self.assertFalse(values["RESUME"])
        self.assertFalse(values["RUN_TEST"])
        self.assertFalse(values["GOLD_FINAL"])
        self.assertEqual(values["GOLD_FILES"], [])
        def trainer_args(source):
            return ast.dump(next(n for n in ast.walk(ast.parse(source)) if isinstance(n, ast.Call)
                and isinstance(n.func, ast.Name) and n.func.id == "TrainingArguments"))
        baseline_code = next(c for c in CODES if "INFERENCE_TEMPLATE =" in c)
        v2_code = next(c.source for c in notebook.cells if c.id == "a4-025")
        self.assertEqual(trainer_args(baseline_code), trainer_args(v2_code))
        self.assertIn('previous_spec = BASELINE_ROOT / "run_manifest.json"',
                      next(c.source for c in notebook.cells if c.id == "a4-019"))

    def test_v2_real_documents_are_disjoint_and_validation_is_subset_of_v0(self):
        ns = functions_namespace()
        ids = ROOT / "Folder_trabajo_Equipos_14_y_15/TrainingData_Grupo15"
        rows = list(ns["read_jsonl"](ids / "training_v1_G15.jsonl"))
        test = list(ns["read_jsonl"](ids / "test_set_ids_G15.jsonl"))
        rules = ns["exclusion_rules"](ns["read_jsonl"](ids / "exclusion_list_G15_V2.jsonl"))
        eligible = [r for r in rows if not ns["excluded"](r, rules)]
        ns.update(SPLIT_SEED="G15-A4-split-v1", VAL_FRAC=.1)
        v2_val = [r for r in eligible if ns["validation_citing"](r["citing_paper_id"])]
        documents = lambda items: {r[k] for r in items for k in ["citing_paper_id", "cited_paper_id"]}
        val_docs = documents(v2_val)
        train = [r for r in eligible if not ns["validation_citing"](r["citing_paper_id"])
                 and r["citing_paper_id"] not in val_docs and r["cited_paper_id"] not in val_docs]
        self.assertEqual((len(eligible), len(train), len(v2_val)), (15349, 11015, 1539))
        self.assertFalse(documents(train) & val_docs)
        self.assertFalse((documents(train) | val_docs) & documents(test))
        v0_val_keys = {r["inst_key"] for r in rows if ns["validation_citing"](r["citing_paper_id"])}
        self.assertTrue({r["inst_key"] for r in v2_val} <= v0_val_keys)
        self.assertEqual({r["primary_pre_label"] for r in train}, set(LABELS))
        self.assertEqual({r["primary_pre_label"] for r in v2_val}, set(LABELS))

    def test_control_rejects_new_data_or_training_policy(self):
        reference = {"isolation": "V0", "input_hashes": {"data": "abc"}, "seed": 42,
                     "model_revision": "frozen", "loss": "unweighted_cross_entropy", "environment": "old",
                     "split_hashes": {"validation": "v0"}}
        current = {**copy.deepcopy(reference), "isolation": "V2", "environment": "new",
                   "split_hashes": {"validation": "v2"}}
        validate_v2_spec(reference, current)
        for field, value in [("seed", 7), ("input_hashes", {"data": "different"}),
                             ("model_revision", "latest"), ("loss", "weighted")]:
            with self.subTest(field=field), self.assertRaisesRegex(ValueError, field):
                validate_v2_spec(reference, {**current, field: value})

    def test_reference_requires_audited_fp32_predictions_from_same_split(self):
        with workspace_temp() as tmp:
            root = Path(tmp)
            evaluation = root / "evaluation"
            evaluation.mkdir()
            spec = {"isolation": "V0", "labels": LABELS, "split_hashes": {"validation": "fixed"}}
            (root / "run_manifest.json").write_text(json.dumps(spec))
            pd.DataFrame({"train": [10], "validation": [1]}, index=["Background"]).to_csv(
                root / "split_class_counts.csv")
            pd.DataFrame([{"config": config, "precision": "fp32", "n": 1}
                          for config in ["base", "fragmentos"]]).to_csv(
                evaluation / "validation_comparison.csv", index=False)
            for config in ["base", "fragmentos"]:
                directory = evaluation / config
                directory.mkdir()
                pd.DataFrame([{"inst_key": "a", "gold_or_prelabel": "Background",
                               "label_source": "pre_label", "predicted_label": "Background"}]).to_csv(
                    directory / "validation_predictions.csv", index=False)
                (directory / "export_precision_audit.json").write_text(json.dumps({
                    "export_check": "passed_full_validation", "split_hashes": spec["split_hashes"]}))
            actual, provenance = load_v0_reference(root, evaluation, LABELS)
            self.assertEqual(actual, spec)
            self.assertEqual(len(provenance["files_sha256"]), 7)
            (evaluation / "base/export_precision_audit.json").write_text(json.dumps({
                "export_check": "passed_full_validation", "split_hashes": {"validation": "other"}}))
            with self.assertRaisesRegex(ValueError, "partición"):
                load_v0_reference(root, evaluation, LABELS)

    def test_common_comparison_aligns_keys_and_rejects_label_changes(self):
        with workspace_temp() as tmp:
            root = Path(tmp)
            columns = ["inst_key", "gold_or_prelabel", "label_source", "predicted_label"]
            v0 = pd.DataFrame([["b", "Gap", "pre_label", "Gap"],
                               ["a", "Background", "pre_label", "Background"],
                               ["c", "Evidence", "pre_label", "Background"]], columns=columns)
            v2 = pd.DataFrame([["a", "Background", "pre_label", "Gap"],
                               ["b", "Gap", "pre_label", "Gap"]], columns=columns)
            for variant, frame in [("V0", v0), ("V2", v2)]:
                for config in ["base", "fragmentos"]:
                    directory = root / variant / config
                    directory.mkdir(parents=True)
                    frame.to_csv(directory / "validation_predictions.csv", index=False)
            full, common, classes = compare_v0_v2(root / "V0", root / "V2", "ref", "new", LABELS,
                                                  100, 50, root / "reports")
            self.assertEqual(full.n.tolist(), [3, 3, 2, 2])
            self.assertEqual(common.n.tolist(), [2, 2, 2, 2])
            self.assertEqual(common.accuracy.tolist(), [1, 1, .5, .5])
            self.assertEqual(len(classes), 36)
            v2.loc[v2.inst_key.eq("a"), "gold_or_prelabel"] = "Evidence"
            v2.to_csv(root / "V2/base/validation_predictions.csv", index=False)
            with self.assertRaisesRegex(ValueError, "etiquetas"):
                compare_v0_v2(root / "V0", root / "V2", "ref", "new", LABELS, 100, 50, root / "bad")


if __name__ == "__main__":
    unittest.main(verbosity=2)
