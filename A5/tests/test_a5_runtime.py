"""Pruebas offline. Ninguna solicitud sale a la red."""
from pathlib import Path
import copy
import contextlib
import io
import json
import sys
import tempfile
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
import a5_runtime as a5


def config(output, demo=True):
    return {"demo": demo, "split": "dev", "paths": {}, "output_dir": str(output), "run_id": "test-run",
            "dataset_version": "fixture-only", "guide_version": "rev3.1", "variant": "V0",
            "gold_final": False, "protocol_frozen": False, "min_gold_per_class": 300,
            "quota_deviation_reason": "", "enable_api": not demo, "endpoint": "https://api.example.invalid/v1/chat/completions",
            "model": "mock-model", "temperature": None, "max_output_tokens": 2048,
            "output_token_parameter": "max_completion_tokens", "response_format": "json_object", "extra_body": {},
            "budget_usd": 1.0, "reserve_per_attempt_usd": .05, "input_usd_per_million": 1.0,
            "output_usd_per_million": 2.0, "pricing_verified": True, "pricing_source": "fixture",
            "pricing_date": "2026-11-09", "timeout_seconds": 30, "max_retries": 2,
            "request_interval_seconds": 0, "representations": ["base", "fragmentos"],
            "styles": ["generic", "specific"], "shots": ["zero", "few"],
            "aligned_inputs": False, "input_policy_version": "fixture", "seed": 42,
            "limit_cases": None, "stability_cases": 0}


def scores(label="Application"):
    return {"scores": {k: int(k == label) for k in a5.LABELS}}


class RuntimeTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.snapshot = json.loads((ROOT / "prompt_v11_1_snapshot.json").read_text(encoding="utf-8"))

    def test_score_contract_rejects_invalid_values(self):
        self.assertTrue(a5.validate_scores(json.dumps(scores()))["valid"])
        for bad in ['```json\n' + json.dumps(scores()) + '\n```', '{"scores":{},"extra":1}',
                    '{"scores":{"Application":1,"Application":0}}', '{"scores":{"Application":NaN}}']:
            self.assertFalse(a5.validate_scores(bad)["valid"], bad)
        for value in [True, -1, 1.1, "0.1"]:
            obj = scores(); obj["scores"]["Application"] = value
            self.assertFalse(a5.validate_scores(json.dumps(obj))["valid"])
        obj = scores(); obj["scores"]["Evidence"] = .3
        self.assertFalse(a5.validate_scores(json.dumps(obj))["valid"])

    def test_ties_are_recorded_with_fixed_order(self):
        obj = {"scores": {k: .5 if k in ("Application", "Evidence") else 0 for k in a5.LABELS}}
        result = a5.validate_scores(json.dumps(obj))
        self.assertTrue(result["tie"]); self.assertEqual(result["predicted_label"], "Application")

    def test_no_label_leakage_and_target_checks(self):
        bundle = a5.synthetic_demo(); source = copy.deepcopy(bundle["cases"][0])
        source.update(gold_primary="SECRET-GOLD", pre_label="SECRET-PRELABEL", notes="SECRET-NOTES")
        case = a5.normalize_cases([source], "dev")[0]
        condition = a5.make_conditions(["base"], ["specific"], ["zero"])[0]
        messages = a5.build_messages(case, condition, self.snapshot, [], {}, False)
        self.assertNotIn("SECRET-", json.dumps(messages))
        source["context"] += " [[TARGET]]"
        with self.assertRaises(ValueError): a5.normalize_cases([source], "dev")

    def test_isolation_all_variants(self):
        bundle = a5.synthetic_demo()
        for variant in ("V0", "V1", "V2"):
            a5.audit_isolation(bundle["cases"], bundle["examples"], bundle["heldout"], [], variant)
        ex = copy.deepcopy(bundle["examples"])
        ex[0]["citing_id"] = bundle["heldout"][0]["citing_id"]
        with self.assertRaises(ValueError): a5.audit_isolation(bundle["cases"], ex, bundle["heldout"], [], "V0")
        ex[0]["citing_id"] = "different"; ex[0]["cited_id"] = bundle["heldout"][0]["cited_id"]
        a5.audit_isolation(bundle["cases"], ex, bundle["heldout"], [], "V0")
        with self.assertRaises(ValueError): a5.audit_isolation(bundle["cases"], ex, bundle["heldout"], [], "V1")
        ex[0]["cited_id"] = bundle["heldout"][0]["citing_id"]
        with self.assertRaises(ValueError): a5.audit_isolation(bundle["cases"], ex, bundle["heldout"], [], "V2")
        with self.assertRaises(ValueError):
            a5.audit_isolation(bundle["cases"], bundle["examples"], bundle["heldout"], [{"inst_key": bundle["cases"][0]["inst_key"]}], "V0")

    def test_matrix_and_fewshot(self):
        bundle = a5.synthetic_demo()
        with tempfile.TemporaryDirectory() as out:
            cfg = config(out); cfg["stability_cases"] = 2
            plan = a5.make_plan(cfg, bundle, self.snapshot)
            self.assertEqual(plan["primary_calls"], 72)
            self.assertEqual(plan["total_calls"], 104)
            zero = next(t for t in plan["tasks"] if "-zero" in t["condition"])
            few = next(t for t in plan["tasks"] if "-few" in t["condition"])
            self.assertEqual(len(zero["messages"]), 2)
            self.assertEqual(len(few["messages"]), 20)
            for m in few["messages"]:
                if m["role"] == "assistant": self.assertTrue(a5.validate_scores(m["content"])["valid"])

    def test_gold_requires_adjudicated_human_rows(self):
        valid = {"inst_key": "x", "gold_primary": "Application", "label_source": "human_gold", "adjudicated": True}
        self.assertEqual(a5.normalize_gold([valid]), {"x": "Application"})
        for field, value in [("gold_primary", "unclear"), ("adjudicated", False), ("label_source", "prelabel")]:
            with self.assertRaises(ValueError): a5.normalize_gold([{**valid, field: value}])

    def test_test_requires_aligned_inputs_and_no_sample(self):
        bundle = a5.synthetic_demo()
        with tempfile.TemporaryDirectory() as out:
            cfg = config(out); cfg["split"] = "test"
            with self.assertRaisesRegex(ValueError, "alineadas"): a5.make_plan(cfg, bundle, self.snapshot)
            cfg["limit_cases"] = 1
            with self.assertRaises(ValueError): a5.make_plan(cfg, bundle, self.snapshot)

    def test_demo_runs_offline_and_resumes(self):
        with tempfile.TemporaryDirectory() as out:
            cfg = config(out); bundle = a5.synthetic_demo(); plan = a5.make_plan(cfg, bundle, self.snapshot)
            def forbidden(*args): raise AssertionError("No network in demo")
            first = a5.run_experiment(cfg, bundle, plan, self.snapshot, transport=forbidden)
            root = Path(first["output_dir"]); count = len(a5.read_jsonl(root / "attempts.jsonl"))
            second = a5.run_experiment(cfg, bundle, plan, self.snapshot, transport=forbidden)
            self.assertEqual(count, len(a5.read_jsonl(root / "attempts.jsonl")))
            self.assertEqual(first["predictions"], second["predictions"])
            self.assertTrue(all(p["synthetic"] for p in second["predictions"]))
            metrics = a5.evaluate(first["predictions"], bundle["demo_gold"], bundle["cases"], root)
            self.assertEqual(len(metrics), 8)
            self.assertTrue(all(m["f1_macro"] == 1 for m in metrics))
            cfg["model"] = "changed"
            with self.assertRaisesRegex(ValueError, "run_id"): a5.run_experiment(cfg, bundle, plan, self.snapshot)

    def mock_api_setup(self, output):
        cfg = config(output, demo=False); cfg.update(representations=["base"], styles=["generic"], shots=["zero"], limit_cases=1)
        bundle = a5.synthetic_demo(); bundle["synthetic"] = False
        return cfg, bundle, a5.make_plan(cfg, bundle, self.snapshot)

    def test_disabled_api_prepares_only_and_no_token_saved(self):
        with tempfile.TemporaryDirectory() as out:
            cfg, bundle, plan = self.mock_api_setup(out); cfg["enable_api"] = False
            result = a5.run_experiment(cfg, bundle, plan, self.snapshot)
            self.assertEqual(result["status"], "prepared_without_api")
            self.assertFalse((Path(result["output_dir"]) / "attempts.jsonl").exists())

    def test_paid_guards_reject_demo_insecure_url_and_no_prices(self):
        cfg = config("unused", demo=False); bundle = a5.synthetic_demo()
        with self.assertRaises(ValueError): a5.check_api_config(cfg, bundle)
        bundle["synthetic"] = False
        for key, val in [("endpoint", "http://example.com"), ("endpoint", "https://example.com?token=x"), ("pricing_verified", False), ("budget_usd", 0)]:
            with self.assertRaises(ValueError): a5.check_api_config({**cfg, key: val}, bundle)

    def test_invalid_json_is_not_retried(self):
        calls = []
        def mock(payload, cfg, token):
            calls.append(payload)
            return {"ok": True, "status_code": 200, "elapsed_seconds": .1, "raw_body": json.dumps({
                "model": "mock", "choices": [{"finish_reason": "stop", "message": {"content": "invalid"}}],
                "usage": {"prompt_tokens": 100, "completion_tokens": 10}})}
        with tempfile.TemporaryDirectory() as out:
            cfg, bundle, plan = self.mock_api_setup(out)
            result = a5.run_experiment(cfg, bundle, plan, self.snapshot, token="secret-for-test", transport=mock)
            self.assertEqual(len(calls), 1)
            self.assertEqual(result["predictions"][0]["predicted_label"], a5.INVALID)
            self.assertNotIn("secret-for-test", (Path(result["output_dir"]) / "manifest.json").read_text())

    def test_retry_resume_and_ledger_account_all_attempts(self):
        calls = []
        def mock(payload, cfg, token):
            calls.append(1)
            if len(calls) == 1:
                return {"ok": False, "status_code": 429, "elapsed_seconds": .1, "raw_body": "rate limited"}
            return {"ok": True, "status_code": 200, "elapsed_seconds": .2, "raw_body": json.dumps({
                "model": "mock", "choices": [{"finish_reason": "stop", "message": {"content": json.dumps(scores())}}],
                "usage": {"prompt_tokens": 100, "completion_tokens": 100}})}
        with tempfile.TemporaryDirectory() as out, patch.object(a5.time, "sleep"):
            cfg, bundle, plan = self.mock_api_setup(out)
            result = a5.run_experiment(cfg, bundle, plan, self.snapshot, token="test", transport=mock)
            self.assertEqual(len(calls), 2); self.assertTrue(result["predictions"][0]["valid"])
            self.assertEqual(result["ledger"]["unknown_cost_attempts"], 1)
            self.assertAlmostEqual(result["ledger"]["reserved_usd"], .1)
            a5.run_experiment(cfg, bundle, plan, self.snapshot, token="test", transport=mock)
            self.assertEqual(len(calls), 2)

    def test_budget_and_uncertain_attempt_do_not_send(self):
        with tempfile.TemporaryDirectory() as out:
            cfg, bundle, plan = self.mock_api_setup(out); cfg["budget_usd"] = .01
            with self.assertRaisesRegex(RuntimeError, "Tope"):
                a5.run_experiment(cfg, bundle, plan, self.snapshot, token="test", transport=lambda *args: self.fail("budget bypass"))
        with tempfile.TemporaryDirectory() as out:
            cfg, bundle, plan = self.mock_api_setup(out)
            def crash(*args): raise RuntimeError("simulated process interruption")
            with self.assertRaises(RuntimeError): a5.run_experiment(cfg, bundle, plan, self.snapshot, token="test", transport=crash)
            with self.assertRaisesRegex(RuntimeError, "sin desenlace"):
                a5.run_experiment(cfg, bundle, plan, self.snapshot, token="test", transport=lambda *args: self.fail("duplicate send"))

    def test_invalid_predictions_remain_in_metrics(self):
        y = list(a5.LABELS); pred = list(y); pred[0] = a5.INVALID
        metrics = a5.classification_metrics(y, pred)
        self.assertAlmostEqual(metrics["accuracy"], 8/9)
        self.assertAlmostEqual(metrics["f1_macro"], 8/9)
        self.assertEqual(metrics["per_class"]["Background"]["recall"], 0)

    def test_truncated_response_cannot_be_valid(self):
        cfg = config("unused")
        result = a5.unpack_response({"ok": True, "raw_body": json.dumps({"choices": [{"finish_reason": "length", "message": {"content": json.dumps(scores())}}]})}, cfg)
        self.assertFalse(result["valid"])

    def test_all_notebook_blocks_execute_in_demo_without_network(self):
        book = json.loads((ROOT / "A5_Modelo_Comercial_G15.ipynb").read_text(encoding="utf-8"))
        self.assertEqual(sum(c["cell_type"] == "code" for c in book["cells"]), 14)
        namespace = {"__name__": "__main__"}
        with tempfile.TemporaryDirectory() as out, contextlib.redirect_stdout(io.StringIO()), patch.object(Path, "cwd", return_value=ROOT), patch.object(a5.urllib.request.OpenerDirector, "open", side_effect=AssertionError("Network forbidden")):
            for i, cell in enumerate(book["cells"]):
                if cell["cell_type"] != "code": continue
                self.assertEqual(book["cells"][i-1]["cell_type"], "markdown")
                self.assertIsNone(cell["execution_count"])
                self.assertEqual(cell["outputs"], [])
                exec(compile(cell["source"], f"notebook-cell-{i}", "exec"), namespace)
                if "DATA_DIR =" in cell["source"]:
                    namespace["OUTPUT_DIR"] = Path(out)
            self.assertEqual(namespace["run"]["status"], "SIMULATED")
            self.assertEqual(len(namespace["predictions"]), 72)
            self.assertEqual(len(namespace["metrics"]), 8)
            self.assertIsNone(namespace["api_token"])


if __name__ == "__main__":
    unittest.main()
