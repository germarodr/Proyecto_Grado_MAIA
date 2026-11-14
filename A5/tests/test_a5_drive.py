"""Fixtures inventados de un Drive montado. Sin red ni datos reales de T_B."""
from pathlib import Path
import json
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
import a5_drive as drive
import a5_runtime as runtime


def fixture(root):
    shared, own = Path(root) / "MAIA_PROYECTO", Path(root) / "MAIA_TESIS"
    a3 = shared / "a3"; batch = shared / "a2/batches_norw"
    a3.mkdir(parents=True); batch.mkdir(parents=True); own.mkdir()
    gold = [
        {"inst_key": "2001.00001|1|10-20|2002.00002", "set": "A", "gold_primary": "Background", "in_eval": True, "source": "agreement"},
        {"inst_key": "2003.00003|2|10-20|2004.00004", "set": "B", "gold_primary": "Application", "in_eval": True, "source": "adjudication", "annotation_g14": "DO_NOT_LEAK"},
        {"inst_key": "2005.00005|3|10-20|2006.00006", "set": "B", "gold_primary": "unclear", "in_eval": False, "source": "adjudication"},
    ]
    path = a3 / "test_set_gold.jsonl"
    path.write_text("".join(json.dumps(r) + "\n" for r in gold), encoding="utf-8")
    manifest = {"packages": 3, "in_eval": {"A": 1, "B": 1}, "unclear": {"A": 0, "B": 1},
                "files": {path.name: drive.sha256(path)}}
    mp = a3 / "manifest_metrics.json"; mp.write_text(json.dumps(manifest), encoding="utf-8")
    texts = [{"inst_key": r["inst_key"], "context": "Prior context. We use [[TARGET]]. Other topic.",
              "cited_title": "Fixture", "cited_abstract": "Invented text", "gold_primary": "MUST_NOT_APPEAR",
              "top3": [{"text": "Invented passage", "section": None} for _ in range(3)]} for r in gold]
    bp = batch / "fixture.jsonl"; bp.write_text("".join(json.dumps(r) + "\n" for r in texts), encoding="utf-8")
    return shared, own, drive.sha256(mp), bp


class DrivePreparationTests(unittest.TestCase):
    def test_target_sentence_on_uncased_and_decoded_punctuation(self):
        examples = [
            ("previous result. we use [[TARGET]]. another result.", "we use [[TARGET]]."),
            ("liu et al. [CITE] use attention. [[TARGET]] is the first work. another survey.",
             "[[TARGET]] is the first work."),
            ("prior work. following smith et al. [CITE], we adapt [[TARGET]]. next topic.",
             "following smith et al. [CITE], we adapt [[TARGET]]."),
            ("prior work. examples ( e . g . methods ) include [[TARGET]]. next topic.",
             "examples ( e . g . methods ) include [[TARGET]]."),
            ("previous sentence. visible fragment [[TARGET]] without an ending",
             "visible fragment [[TARGET]] without an ending"),
        ]
        for context, expected in examples:
            with self.subTest(context=context):
                self.assertEqual(drive.target_sentence(context), expected)
                self.assertIn(expected, context)

    def test_preparation_filters_b_keeps_gold_separate_and_preserves_source(self):
        with tempfile.TemporaryDirectory() as root:
            shared, own, expected, bp = fixture(root)
            before = {str(p): drive.sha256(p) for p in shared.rglob('*') if p.is_file()}
            result = drive.prepare_tb(shared, own, expected)
            self.assertEqual(result["audit"]["evaluable_tb"], 1)
            self.assertEqual(result["audit"]["excluded_unclear_tb"], 1)
            self.assertFalse(result["audit"]["a4_aligned"])
            cases = runtime.read_jsonl(result["cases"])
            runtime.normalize_cases(cases, "test")
            self.assertEqual(len(cases), 1)
            self.assertEqual(cases[0]["target_sentence"], "We use [[TARGET]].")
            self.assertNotIn("top3", cases[0])
            self.assertNotIn("chunks", cases[0])
            self.assertNotIn("gold_primary", cases[0]); self.assertNotIn("annotation_g14", cases[0])
            self.assertEqual(runtime.normalize_gold(runtime.read_jsonl(result["gold"])), {cases[0]["inst_key"]: "Application"})
            self.assertEqual(len(runtime.read_jsonl(result["heldout"])), 2)
            self.assertEqual(before, {str(p): drive.sha256(p) for p in shared.rglob('*') if p.is_file()})
            again = drive.prepare_tb(shared, own, expected)
            self.assertEqual(result["prepared_dir"], again["prepared_dir"])

    def test_manifest_and_gold_changes_are_blocked(self):
        with tempfile.TemporaryDirectory() as root:
            shared, own, expected, _ = fixture(root)
            with self.assertRaisesRegex(ValueError, "manifiesto A3"):
                drive.inspect_drive(shared, own, "0" * 64)
            (shared / "a3/test_set_gold.jsonl").write_text('{}\n', encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "gold no coincide"):
                drive.inspect_drive(shared, own, expected)

    def test_missing_case_or_divergent_duplicate_blocks_export(self):
        with tempfile.TemporaryDirectory() as root:
            shared, own, expected, bp = fixture(root)
            source = list(drive.rows(bp))
            second = bp.with_name("duplicate.jsonl")
            source[1]["context"] = "Changed text with [[TARGET]]."
            second.write_text(json.dumps(source[1]) + "\n", encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "divergentes"):
                drive.prepare_tb(shared, own, expected)
        with tempfile.TemporaryDirectory() as root:
            shared, own, expected, bp = fixture(root)
            bp.write_text('', encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "No se reconstruyeron"):
                drive.prepare_tb(shared, own, expected)

    def test_results_cannot_be_inside_shared_folder(self):
        with tempfile.TemporaryDirectory() as root:
            shared, own, expected, _ = fixture(root)
            with self.assertRaisesRegex(ValueError, "separadas"):
                drive.inspect_drive(shared, shared, expected)

    def test_export_integrity_checked_before_reuse(self):
        with tempfile.TemporaryDirectory() as root:
            shared, own, expected, _ = fixture(root)
            result = drive.prepare_tb(shared, own, expected)
            Path(result["cases"]).write_text('{}\n', encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "Cambió"):
                drive.prepare_tb(shared, own, expected)

    def test_source_needs_only_context_title_abstract_not_chunks(self):
        with tempfile.TemporaryDirectory() as root:
            shared, own, expected, bp = fixture(root)
            data = list(drive.rows(bp))
            for row in data:
                row.pop("top3", None)
            bp.write_text(''.join(json.dumps(r) + '\n' for r in data), encoding="utf-8")
            result = drive.prepare_tb(shared, own, expected)
            self.assertEqual(len(runtime.read_jsonl(result["cases"])), 1)


if __name__ == "__main__":
    unittest.main()
