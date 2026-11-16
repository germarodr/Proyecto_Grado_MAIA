"""Verifica integridad y conservacion de invalidos en CSV de comparacion."""
import csv
import hashlib
import importlib.util
import json
from pathlib import Path
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("csv_export_test", ROOT / "exportar_resultados_csv.py")
exporter = importlib.util.module_from_spec(spec)
spec.loader.exec_module(exporter)


def save(path, value):
    path.write_text(json.dumps(value), encoding="utf-8")


def fixture(root):
    gold = root / "gold.jsonl"
    gold.write_text(json.dumps({"inst_key": "CASE", "gold_primary": "Background",
        "label_source": "human_gold", "adjudicated": True})+"\n", encoding="utf-8")
    predictions = []
    for i, cond in enumerate(sorted(exporter.CONDITIONS)):
        valid = i != 0
        predictions.append({"inst_key": "CASE", "citing_id": "ARTICLE", "request_key": cond,
            "condition": cond, "replicate": 0, "synthetic": False,
            "returned_model": "fixture-model", "valid": valid,
            "predicted_label": "Background" if valid else "__invalid__",
            "scores": {k: int(k == "Background") for k in exporter.LABELS} if valid else None,
            "error": None if valid else "invalid fixture"})
    cfg = {"split": "test", "demo": False, "run_id": "fixture", "model": "fixture-model",
           "paths": {"gold": str(gold)}}
    spec = {"config": cfg, "synthetic": False, "task_keys": [r["request_key"] for r in predictions]}
    digest = hashlib.sha256(json.dumps(spec, ensure_ascii=False, sort_keys=True, allow_nan=False).encode()).hexdigest()
    save(root / "manifest.json", {"spec": spec, "fingerprint": digest})
    save(root / "predictions.json", predictions)
    save(root / "run_summary.json", {"status": "completed", "records": 4})
    return gold


class CsvTests(unittest.TestCase):
    def test_export_preserves_invalids_and_originals(self):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d); fixture(root)
            hashes = {p.name: exporter.sha(p) for p in root.iterdir()}
            result = exporter.export_results(root)
            self.assertEqual((result["records"], result["csv_files"], result["invalid"]), (4, 5, 1))
            with (root / "csv/predictions_fixture-model.csv").open(encoding="utf-8-sig", newline="") as stream:
                rows = list(csv.DictReader(stream))
            invalid = next(r for r in rows if r["valid"] == "False")
            self.assertEqual(invalid["predicted_label"], "__invalid__")
            self.assertEqual(invalid["p_Background"], "")
            self.assertTrue(all(exporter.sha(root / name) == h for name, h in hashes.items()))
            for p in (root / "csv").glob("*base-*.csv"):
                with p.open(encoding="utf-8-sig", newline="") as stream:
                    self.assertEqual(len(list(csv.DictReader(stream))), 1)

    def test_wrong_gold_stops_before_export(self):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d); gold = fixture(root)
            gold.write_text(gold.read_text().replace("CASE", "OTHER"))
            with self.assertRaisesRegex(ValueError, "mismos casos"):
                exporter.export_results(root)
            self.assertFalse((root / "csv").exists())

    def test_tampered_scores_stops_before_export(self):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d); fixture(root)
            rows = json.loads((root / "predictions.json").read_text())
            rows[1]["scores"]["Background"] = 0
            save(root / "predictions.json", rows)
            with self.assertRaisesRegex(ValueError, "Puntajes"):
                exporter.export_results(root)
            self.assertFalse((root / "csv").exists())


if __name__ == "__main__":
    unittest.main()
