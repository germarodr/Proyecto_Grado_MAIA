"""Pruebas reales de MLflow/SQLite, callback, snapshots y recuperación sin GPU.

Ejecutar con MLflow 3.17.2 instalado: python A4/verificar_tracking.py
"""
import contextlib
import hashlib
import json
import shutil
import tempfile
import time
import unittest
import uuid
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch

import tracking_runtime as runtime

ROOT = Path(__file__).resolve().parent / ".test_tmp"
for name in ["Path", "json", "shutil", "time"]:
    setattr(runtime, name, globals()[name])


def sha256(path):
    with Path(path).open("rb") as stream:
        return hashlib.file_digest(stream, "sha256").hexdigest()


def save_json(path, value):
    Path(path).write_text(json.dumps(value), encoding="utf-8")


runtime.sha256, runtime.save_json = sha256, save_json


@contextlib.contextmanager
def temporary_directory():
    ROOT.mkdir(exist_ok=True)
    path = ROOT / ("tracking_" + uuid.uuid4().hex)
    path.mkdir()
    try:
        yield str(path)
    finally:
        # SQLAlchemy mantiene pools con archivos SQLite abiertos en Windows.
        from mlflow.store.tracking.sqlalchemy_store import SqlAlchemyStore
        for engine in SqlAlchemyStore._engine_map.values():
            engine.dispose()
        assert path.resolve().is_relative_to(ROOT.resolve())
        shutil.rmtree(path)


class TrackingTests(unittest.TestCase):
    def test_trainer_checkpoint_and_resume(self):
        import torch
        from transformers import BertConfig, BertForSequenceClassification, Trainer, TrainingArguments, TrainerCallback

        class InterruptAfterCheckpoint(TrainerCallback):
            def on_step_begin(self, args, state, control, **kwargs):
                if state.global_step == 2:
                    raise RuntimeError("simulated session interruption")

        torch.set_num_threads(1)
        with temporary_directory() as tmp, patch.object(tempfile, "TemporaryDirectory", temporary_directory):
            base = Path(tmp)
            output = base / "outputs"
            output.mkdir()
            tracker = runtime.A4Tracking(base / "tracking", base / "snapshots", output, "trainer_01")
            data = [{"input_ids": [2, 5, 6, 3], "attention_mask": [1, 1, 1, 1], "labels": i % 3} for i in range(4)]
            checkpoint = None
            for attempt in [1, 2]:
                expected = self.assertRaisesRegex(RuntimeError, "simulated session interruption") if attempt == 1 else contextlib.nullcontext()
                with expected, tracker.attempt("base", {"seed": 42}, checkpoint) as rid:
                    model = BertForSequenceClassification(BertConfig(vocab_size=12, hidden_size=16,
                        num_hidden_layers=1, num_attention_heads=2, intermediate_size=24, num_labels=3))
                    args = TrainingArguments(output_dir=str(output / "base/checkpoints"),
                        use_cpu=True, num_train_epochs=2, per_device_train_batch_size=2,
                        save_strategy="epoch", logging_steps=1, report_to="none", disable_tqdm=True,
                        eval_strategy="epoch", load_best_model_at_end=True,
                        metric_for_best_model="loss", greater_is_better=False,
                        save_safetensors=True, save_total_limit=2)
                    callbacks = [runtime.A4MLflowCallback(tracker, rid)]
                    if attempt == 1:
                        callbacks.append(InterruptAfterCheckpoint())
                    trainer = Trainer(model=model, args=args, train_dataset=data, eval_dataset=data,
                        callbacks=callbacks)
                    trainer.train(resume_from_checkpoint=checkpoint)
                self.assertEqual(trainer.state.global_step, attempt * 2)
                self.assertEqual(tracker.client.get_run(rid).info.status, "FAILED" if attempt == 1 else "FINISHED")
                checkpoint = runtime.verified_checkpoint(output / "base/checkpoints")
                self.assertTrue(Path(checkpoint, "A4_COMPLETE.json").exists())
                self.assertTrue(tracker.client.get_metric_history(rid, "loss"))

    def test_metrics_failure_restore_and_new_attempt(self):
        with temporary_directory() as tmp, patch.object(tempfile, "TemporaryDirectory", temporary_directory):
            base = Path(tmp)
            output = base / "outputs"
            (output / "base").mkdir(parents=True)
            save_json(output / "run_manifest.json", {"seed": 42})
            save_json(output / "base/scores.json", {"macro_f1": .5})
            tracker = runtime.A4Tracking(base / "tracking", base / "snapshots", output, "test_01", interval=0)
            with self.assertRaisesRegex(RuntimeError, "interruption"):
                with tracker.attempt("base", {"seed": 42}, None) as rid:
                    callback = runtime.A4MLflowCallback(tracker, rid)
                    callback.on_log(None, SimpleNamespace(global_step=50), None,
                                    logs={"loss": 1.2, "eval_f1_macro": .5, "text": "ignore"})
                    callback.on_step_end(None, None, None)
                    raise RuntimeError("interruption")
            self.assertEqual(tracker.client.get_run(rid).info.status, "FAILED")
            self.assertEqual(tracker.client.get_metric_history(rid, "loss")[0].step, 50)
            self.assertTrue(tracker.client.list_artifacts(rid, "reports"))
            # Restaurar a la misma ruta canónica, simulando disco local nuevo.
            from mlflow.store.tracking.sqlalchemy_store import SqlAlchemyStore
            for engine in SqlAlchemyStore._engine_map.values():
                engine.dispose()
            local = base / "tracking"
            local.rename(base / "previous_tracking")
            recovered = runtime.A4Tracking(local, base / "snapshots", output, "test_01")
            self.assertEqual(recovered.client.get_run(rid).data.metrics["loss"], 1.2)
            with recovered.attempt("base", {"seed": 42}, "checkpoint-50") as second:
                recovered.metrics(second, {"loss": .8}, step=60)
            self.assertNotEqual(rid, second)
            self.assertEqual(recovered.client.get_run(second).info.status, "FINISHED")
            self.assertEqual(recovered.client.get_run(second).data.tags["mlflow.parentRunId"], recovered.parent("base"))
            latest = sorted((base / "snapshots").glob("*/COMPLETE.json"))[-1].parent
            receipt = json.loads((latest / "COMPLETE.json").read_text())
            self.assertEqual(sha256(latest / "snapshot.zip"), receipt["zip_sha256"])
            # No elegir una copia anterior silenciosamente si la última está corrupta.
            with (latest / "snapshot.zip").open("ab") as stream:
                stream.write(b"corrupt")
            with self.assertRaises(AssertionError):
                runtime.tracking_restore(base / "empty", base / "snapshots")

    def test_checkpoint_selection_rejects_partial_and_tampered(self):
        with temporary_directory() as tmp:
            root = Path(tmp)
            good = root / "checkpoint-10"
            good.mkdir()
            for name in ["optimizer.pt", "scheduler.pt", "training_args.bin", "model.safetensors", "rng_state.pth"]:
                (good / name).write_bytes(b"fixture")
            save_json(good / "trainer_state.json", {"best_model_checkpoint": str(good)})
            runtime.commit_checkpoint(good)
            (root / "checkpoint-20").mkdir()
            self.assertEqual(runtime.verified_checkpoint(root), str(good))
            (good / "optimizer.pt").write_bytes(b"broken")
            with self.assertRaisesRegex(ValueError, "ninguno completo"):
                runtime.verified_checkpoint(root)


if __name__ == "__main__":
    unittest.main(verbosity=2)
