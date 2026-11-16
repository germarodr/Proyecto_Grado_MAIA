"""Consolidacion desde respuestas sin fabricar un diario de llamadas."""
import copy
import importlib.util
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("gemini_tracking_test", ROOT / "Gemini/a5_tracking.py")
tracking = importlib.util.module_from_spec(spec)
spec.loader.exec_module(tracking)


class ConsumptionTests(unittest.TestCase):
    def setUp(self):
        self.cfg = {"input_usd_per_million": 0.3, "output_usd_per_million": 2.5}
        self.rows = [{"request_key": str(i), "condition": "base-specific-zero",
            "attempts": 1, "cost_known": True, "estimated_cost_usd": 0.00055,
            "usage": {"prompt_tokens": 1000, "completion_tokens": 100},
            "response_text": "fixture", "returned_model": "fixture", "valid": True,
            "scores": {}, "predicted_label": "Background"} for i in range(2)]
        self.events = [{"event": "start", "request_key": "0", "attempt": 1},
            {"event": "outcome", "request_key": "0", "attempt": 1,
             "terminal": True, "parsed": copy.deepcopy(self.rows[0])},
            {"event": "start", "request_key": "1", "attempt": 1}]
        self.summary = {"ledger": {"estimated_known_cost_usd": 0.0011, "unknown_cost_attempts": 0}}

    def test_partial_journal_keeps_complete_response_cost(self):
        original = copy.deepcopy(self.events)
        value = tracking.consolidate_consumption(self.rows, self.events, self.cfg, self.summary)
        self.assertFalse(value["provenance"]["attempt_log_complete"])
        self.assertEqual(value["provenance"]["missing_terminal_records"], 1)
        self.assertEqual(value["by_condition"]["base-specific-zero"]["responses_processed"], 2)
        self.assertAlmostEqual(value["by_condition"]["base-specific-zero"]["calculated_cost_usd"], .0011)
        self.assertEqual(self.events, original)
        self.assertNotIn("at", value["records"][0])

    def test_complete_journal_detected(self):
        self.events.append({"event": "outcome", "request_key": "1", "attempt": 1,
                            "terminal": True, "parsed": copy.deepcopy(self.rows[1])})
        value = tracking.consolidate_consumption(self.rows, self.events, self.cfg, self.summary)
        self.assertTrue(value["provenance"]["attempt_log_complete"])

    def test_tampered_cost_summary_or_overlap_rejected(self):
        for change in ("cost", "summary", "overlap", "retries"):
            rows, events, summary = copy.deepcopy((self.rows, self.events, self.summary))
            if change == "cost": rows[1]["estimated_cost_usd"] = 1
            elif change == "summary": summary["ledger"]["estimated_known_cost_usd"] = 1
            elif change == "overlap": events[1]["parsed"]["usage"]["prompt_tokens"] = 1
            else: rows[1]["attempts"] = 2
            with self.subTest(change=change), self.assertRaises(ValueError):
                tracking.consolidate_consumption(rows, events, self.cfg, summary)


if __name__ == "__main__":
    unittest.main()
