"""Reanudación con saldo agotado, errores de servicio y límites; todas las respuestas son inventadas."""
from pathlib import Path
import json
import sys
import tempfile
import unittest
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import a5_runtime as runtime
from test_a5_runtime import config, scores


def response():
    return {"ok": True, "status_code": 200, "elapsed_seconds": .1, "raw_body": json.dumps({
        "model": "fixture", "choices": [{"finish_reason": "stop", "message": {"content": json.dumps(scores())}}],
        "usage": {"prompt_tokens": 100, "completion_tokens": 100}})}


class ResumeTests(unittest.TestCase):
    def setup_run(self, root):
        cfg = config(root, demo=False)
        cfg.update(budget_usd=None, styles=['generic', 'specific'], shots=['zero'], limit_cases=1)
        bundle = runtime.synthetic_demo()
        bundle['synthetic'] = False
        snapshot = json.loads((Path(__file__).resolve().parents[1] / 'prompt_v11_1_snapshot.json').read_text(encoding='utf-8'))
        return cfg, bundle, runtime.make_plan(cfg, bundle, snapshot), snapshot

    def test_balance_exhaustion_stops_and_recharge_resumes_only_pending(self):
        for code in ('credit_balance_exhausted', 'insufficient_quota', 'project_spend_limit_exceeded'):
            with self.subTest(code=code), tempfile.TemporaryDirectory() as root, patch.object(runtime.time, 'sleep'):
                cfg, bundle, plan, snapshot = self.setup_run(root)
                calls = []
                def transport(payload, cfg, token):
                    calls.append(payload)
                    if len(calls) == 2:
                        return {'ok': False, 'status_code': 429, 'elapsed_seconds': .1,
                                'raw_body': json.dumps({'error': {'code': code, 'type': 'insufficient_quota'}})}
                    return response()
                with self.assertRaisesRegex(RuntimeError, 'provider_balance_or_quota'):
                    runtime.run_experiment(cfg, bundle, plan, snapshot, token='fixture', transport=transport)
                self.assertEqual(len(calls), 2)  # No se reintenta la cuota aunque MAX_RETRIES sea 2.
                directory = Path(root) / cfg['run_id']
                state = json.loads((directory / 'progress.json').read_text())
                self.assertEqual(state['completed_requests'], 1)
                self.assertEqual(state['pending_requests'], 1)
                original = runtime.read_jsonl(directory / 'attempts.jsonl')[1]
                result = runtime.run_experiment(cfg, bundle, plan, snapshot, token='new-fixture', transport=transport)
                self.assertEqual(len(calls), 3)
                self.assertEqual(result['records'], 2)
                self.assertEqual(result['invalid'], 0)
                self.assertAlmostEqual(result['ledger']['estimated_known_cost_usd'], .0006)
                self.assertEqual(result['ledger']['unknown_cost_attempts'], 0)
                self.assertEqual(original, runtime.read_jsonl(directory / 'attempts.jsonl')[1])
                again = runtime.run_experiment(cfg, bundle, plan, snapshot, token='fixture', transport=transport)
                self.assertEqual(len(calls), 3)
                self.assertEqual(again['records'], 2)

    def test_rate_limit_after_retry_budget_pauses_and_can_resume(self):
        with tempfile.TemporaryDirectory() as root, patch.object(runtime.time, 'sleep'):
            cfg, bundle, plan, snapshot = self.setup_run(root)
            cfg['max_retries'] = 0
            with self.assertRaisesRegex(RuntimeError, 'service_or_rate_limit'):
                runtime.run_experiment(cfg, bundle, plan, snapshot, token='fixture', transport=lambda *args:
                    {'ok': False, 'status_code': 429, 'elapsed_seconds': .1, 'raw_body': 'rate limited'})
            result = runtime.run_experiment(cfg, bundle, plan, snapshot, token='fixture', transport=lambda *args: response())
            self.assertEqual(result['invalid'], 0)
            self.assertEqual(result['ledger']['unknown_cost_attempts'], 1)

    def test_uncertain_response_blocks_automatic_resend(self):
        with tempfile.TemporaryDirectory() as root:
            cfg, bundle, plan, snapshot = self.setup_run(root)
            with self.assertRaisesRegex(RuntimeError, 'incierta'):
                runtime.run_experiment(cfg, bundle, plan, snapshot, token='fixture', transport=lambda *args:
                    {'ok': False, 'status_code': None, 'elapsed_seconds': 90, 'raw_body': None})
            with self.assertRaisesRegex(RuntimeError, 'sin desenlace'):
                runtime.run_experiment(cfg, bundle, plan, snapshot, token='fixture', transport=lambda *args:
                    self.fail('No reenviar un intento incierto'))

    def test_no_local_cap_accepts_cost_above_accounting_reserve_and_freezes_configuration(self):
        with tempfile.TemporaryDirectory() as root, patch.object(runtime.time, 'sleep'):
            cfg, bundle, plan, snapshot = self.setup_run(root)
            cfg['reserve_per_attempt_usd'] = .000001
            result = runtime.run_experiment(cfg, bundle, plan, snapshot, token='fixture', transport=lambda *args: response())
            self.assertEqual(result['records'], 2)
            cfg['model'] = 'different-model'
            with self.assertRaisesRegex(ValueError, 'cambiaron'):
                runtime.run_experiment(cfg, bundle, plan, snapshot, token='fixture', transport=lambda *args:
                    self.fail('No cambiar modelo de un run existente'))

    def test_stale_lock_requires_explicit_confirmation_and_is_scoped(self):
        with tempfile.TemporaryDirectory() as root:
            p = Path(root) / 'fixture'
            p.mkdir()
            (p / 'RUNNING.lock').write_text('fixture')
            with self.assertRaises(ValueError): runtime.release_stale_run_lock(root, 'fixture')
            self.assertTrue((p / 'RUNNING.lock').exists())
            runtime.release_stale_run_lock(root, 'fixture', confirm_no_active_writer=True)
            self.assertFalse((p / 'RUNNING.lock').exists())
            with self.assertRaises(ValueError): runtime.release_stale_run_lock(root, '../other', confirm_no_active_writer=True)


if __name__ == '__main__': unittest.main()
