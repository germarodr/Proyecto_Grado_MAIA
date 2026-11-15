"""Importación offline: datos de prueba inventados sobre una copia del respaldo A4."""
from pathlib import Path
from contextlib import closing
import importlib.metadata
import json
import sqlite3
import sys
import tempfile
import unittest
from unittest.mock import patch
import zipfile

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
import a5_runtime as runtime
import a5_tracking as tracking


def results_fixture(folder):
    """Simula los archivos de salida; nunca llama al proveedor ni usa sus métricas."""
    folder.mkdir()
    conditions = ['base-generic-zero', 'base-generic-few', 'base-specific-zero', 'base-specific-few']
    cfg = {'run_id': 'FIXTURE_NOT_REAL_API', 'model': 'FIXTURE_MODEL', 'demo': False,
           'split': 'dev', 'limit_cases': 1, 'api_key': 'DO_NOT_EXPORT_THIS_FIXTURE_VALUE'}
    spec = {'config': cfg, 'synthetic': False, 'task_keys': conditions}
    tracking.write(folder / 'manifest.json', {'spec': spec, 'fingerprint': runtime.digest(spec)})
    tracking.write(folder / 'run_summary.json', {'status': 'completed', 'records': 4})
    predictions, metrics, events = [], [], []
    for cond in conditions:
        predictions.append({'request_key': cond, 'inst_key': 'INVENTED_CASE', 'condition': cond,
                            'replicate': 0, 'synthetic': False, 'returned_model': 'FIXTURE_MODEL'})
        metrics.append({'condition': cond, 'n': 1, 'f1_macro': 1/9, 'f1_micro': 1,
                        'valid_coverage': 1, 'latency_mean_seconds': 2,
                        'per_class': {'Application': {'precision': 1, 'recall': 1, 'f1': 1}}})
        for attempt in (1, 2):
            events.append({'event': 'outcome', 'request_key': cond, 'attempt': attempt,
                           'parsed': {'estimated_cost_usd': .01, 'cost_known': True,
                                      'usage': {'prompt_tokens': 100, 'completion_tokens': 20}},
                           'result': {'raw_body': 'PRIVATE_TEXT_MUST_NOT_BE_EXPORTED'}})
    tracking.write(folder / 'predictions.json', predictions)
    tracking.write(folder / 'metrics.json', metrics)
    (folder / 'attempts.jsonl').write_text(''.join(json.dumps(e)+'\n' for e in events), encoding='utf-8')


class SnapshotTests(unittest.TestCase):
    def test_missing_saved_results_stops_without_creating_history(self):
        with tempfile.TemporaryDirectory() as tmp:
            with self.assertRaisesRegex(FileNotFoundError, 'no repitas la API'):
                tracking.load_results(tmp)

    def test_demo_and_changed_manifest_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            p = Path(tmp) / 'run'
            results_fixture(p)
            tracking.load_results(p)
            m = tracking.read(p / 'manifest.json')
            m['spec']['synthetic'] = True
            tracking.write(p / 'manifest.json', m)
            with self.assertRaisesRegex(ValueError, 'manifiesto'):
                tracking.load_results(p)
            m['fingerprint'] = runtime.digest(m['spec'])
            tracking.write(p / 'manifest.json', m)
            with self.assertRaisesRegex(ValueError, 'reales completos'):
                tracking.load_results(p)


def tiny_snapshot(folder, sid, date, values):
    folder.mkdir(parents=True)
    with tempfile.TemporaryDirectory() as tmp:
        db_path = Path(tmp) / 'mlflow.db'
        with closing(sqlite3.connect(db_path)) as db:
            db.execute('CREATE TABLE runs (run_uuid TEXT)')
            db.executemany('INSERT INTO runs VALUES (?)', [(v,) for v in values])
            db.commit()
        files = {'mlflow.db': {'sha256': tracking.sha(db_path), 'size': db_path.stat().st_size}}
        m = {'schema_version': 1, 'snapshot_id': sid, 'created_at_utc': date,
             'mlflow_version': tracking.MLFLOW_VERSION, 'canonical_root': tracking.CANONICAL_ROOT, 'files': files}
        with zipfile.ZipFile(folder / 'snapshot.zip', 'w') as z:
            z.write(db_path, 'mlflow.db')
            z.writestr('snapshot_manifest.json', json.dumps(m))
    checksum = tracking.sha(folder / 'snapshot.zip')
    (folder / 'snapshot.sha256').write_text(checksum + '  snapshot.zip\n')
    tracking.write(folder / 'COMPLETE.json', {'schema_version': 1, 'snapshot_id': sid,
                   'created_at_utc': date, 'mlflow_version': tracking.MLFLOW_VERSION,
                   'zip_size': (folder / 'snapshot.zip').stat().st_size, 'zip_sha256': checksum})


class PublicationTests(unittest.TestCase):
    def fixture(self, root):
        shared, own = Path(root) / 'shared', Path(root) / 'own'
        shared.mkdir()
        tiny_snapshot(shared / 'old', 'old', '2026-11-12T00:00:00+00:00', ['A4'])
        tiny_snapshot(own, 'new', '2026-11-14T00:00:00+00:00', ['A4', 'A5'])
        return shared, own

    def test_publish_preserves_source_and_is_idempotent(self):
        with tempfile.TemporaryDirectory() as tmp:
            shared, own = self.fixture(tmp)
            original = tracking.sha(shared / 'old/snapshot.zip')
            result = tracking.publish_snapshot(own, shared)
            self.assertEqual(result['status'], 'published')
            tracking.validate_snapshot(shared / 'new')
            self.assertEqual(original, tracking.sha(shared / 'old/snapshot.zip'))
            self.assertEqual(tracking.publish_snapshot(own, shared)['status'], 'already_published')

    def test_newer_shared_rows_block_publication(self):
        with tempfile.TemporaryDirectory() as tmp:
            shared, own = self.fixture(tmp)
            tiny_snapshot(shared / 'other', 'other', '2026-11-13T00:00:00+00:00', ['A4', 'A4_NEW'])
            with self.assertRaisesRegex(ValueError, 'historial ausente'):
                tracking.publish_snapshot(own, shared)
            self.assertFalse((shared / 'new').exists())

    def test_shared_change_during_copy_leaves_no_complete_marker(self):
        with tempfile.TemporaryDirectory() as tmp:
            shared, own = self.fixture(tmp)
            inventory = tracking.shared_inventory(shared)
            with patch.object(tracking, 'shared_inventory', side_effect=[inventory, {**inventory, 'other': 'changed'}]):
                with self.assertRaisesRegex(ValueError, 'cambió durante'):
                    tracking.publish_snapshot(own, shared)
            self.assertTrue((shared / 'new/snapshot.zip').exists())
            self.assertFalse((shared / 'new/COMPLETE.json').exists())

    def test_missing_shortcut_is_not_created_silently(self):
        with tempfile.TemporaryDirectory() as tmp:
            with self.assertRaisesRegex(FileNotFoundError, 'acceso directo'):
                tracking.publish_snapshot(Path(tmp) / 'source', Path(tmp) / 'missing')


class RealHistoryTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.source = ROOT / 'MLflow_Respaldo_A4'
        if not (cls.source / 'COMPLETE.json').is_file():
            raise unittest.SkipTest('Respaldo privado A4 no disponible; no se publica en Git')
        try:
            version = importlib.metadata.version('mlflow')
        except importlib.metadata.PackageNotFoundError:
            version = None
        if version != tracking.MLFLOW_VERSION:
            raise unittest.SkipTest('Prueba de integración requiere MLflow ' + tracking.MLFLOW_VERSION)

    def test_preserves_real_70_runs_and_artifacts_and_does_not_duplicate(self):
        from mlflow import MlflowClient
        original_hash = tracking.sha(self.source / 'snapshot.zip')
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            results_fixture(root / 'results')
            out = root / 'snapshots'
            report = tracking.incorporate(self.source, root / 'results', out, work_parent=root)
            self.assertEqual(report['previous_runs'], 70)
            self.assertEqual(report['total_runs'], 74)
            self.assertEqual(report['added_runs'], 4)
            self.assertTrue(report['previous_rows_and_artifacts_preserved'])
            again = tracking.incorporate(self.source, root / 'results', out, work_parent=root)
            self.assertEqual(again['total_runs'], 74)
            self.assertEqual(again['added_runs'], 0)
            self.assertEqual(report['a5_run_ids'], again['a5_run_ids'])
            destination = Path(again['snapshot_dir'])
            tracking.validate_snapshot(destination, root / 'inspection')
            with closing(sqlite3.connect(root / 'inspection/mlflow.db')) as db:
                rows = db.execute("SELECT r.run_uuid,r.artifact_uri FROM runs r JOIN experiments e ON r.experiment_id=e.experiment_id WHERE e.name=?", (tracking.EXPERIMENT,)).fetchall()
                self.assertEqual(len(rows), 4)
                for rid, uri in rows:
                    self.assertTrue(uri.startswith('file:///opt/maia/a4_tracking/artifacts/a5_commercials/'))
                    values = dict(db.execute('SELECT key,value FROM latest_metrics WHERE run_uuid=?', (rid,)))
                    self.assertEqual(values['attempts'], 2)
                    self.assertAlmostEqual(values['cost_known_attempts_usd'], .02)
                    self.assertEqual(values['input_tokens'], 200)
            with zipfile.ZipFile(destination / 'snapshot.zip') as z:
                reports = [n for n in z.namelist() if n.startswith('artifacts/a5_commercials/')]
                self.assertEqual(len(reports), 4)
                for n in reports:
                    b = z.read(n)
                    self.assertNotIn(b'DO_NOT_EXPORT', b)
                    self.assertNotIn(b'PRIVATE_TEXT', b)
            # Un cambio de fuente del mismo run se bloquea antes de duplicar condiciones.
            metric = tracking.read(root / 'results/metrics.json')
            metric[0]['f1_macro'] = .5
            tracking.write(root / 'results/metrics.json', metric)
            with self.assertRaisesRegex(ValueError, 'Cambió una ejecución'):
                tracking.incorporate(self.source, root / 'results', out, work_parent=root)
            self.assertEqual(original_hash, tracking.sha(self.source / 'snapshot.zip'))


if __name__ == '__main__':
    unittest.main()
