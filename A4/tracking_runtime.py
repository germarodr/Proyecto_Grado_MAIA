"""Se incrusta en el notebook: no requiere subir este archivo a Colab."""
import contextlib
import datetime as dt
import math
import numbers
import sqlite3
import tempfile
import uuid
import zipfile
from pathlib import PurePosixPath
import mlflow
from mlflow import MlflowClient
from transformers import TrainerCallback


def tracking_restore(root, snapshots):
    """Solo restaura antes de abrir MLflow; nunca sobrescribe una DB local."""
    root.mkdir(parents=True, exist_ok=True)
    if (root / "mlflow.db").exists():
        return
    candidates = sorted((p.parent for p in snapshots.glob("*/COMPLETE.json")),
        key=lambda p: dt.datetime.fromisoformat(json.loads((p / "COMPLETE.json").read_text())["created_at_utc"]))
    if not candidates:
        print("Sin historial previo: se creará una base MLflow nueva.")
        return
    source = candidates[-1]
    receipt = json.loads((source / "COMPLETE.json").read_text())
    archive_path = source / "snapshot.zip"
    assert receipt["schema_version"] == 1
    assert receipt["snapshot_id"] == source.name
    assert receipt["mlflow_version"] == mlflow.__version__
    assert archive_path.stat().st_size == receipt["zip_size"]
    assert sha256(archive_path) == receipt["zip_sha256"]
    assert (source / "snapshot.sha256").read_text().split()[0] == receipt["zip_sha256"]
    # Validar todo antes de copiar a las rutas canónicas.
    with tempfile.TemporaryDirectory() as tmp:
        target = Path(tmp)
        with zipfile.ZipFile(archive_path) as archive:
            names = archive.namelist()
            assert len(names) == len(set(names))
            manifest = json.loads(archive.read("snapshot_manifest.json"))
            assert manifest["schema_version"] == 1
            assert manifest["snapshot_id"] == receipt["snapshot_id"]
            assert manifest["canonical_root"] == str(root)
            assert manifest["mlflow_version"] == mlflow.__version__
            assert set(names) == set(manifest["files"]) | {"snapshot_manifest.json"}
            for entry in archive.infolist():
                path = PurePosixPath(entry.filename)
                assert not path.is_absolute() and ".." not in path.parts
                assert "\\" not in entry.filename and ":" not in entry.filename
                assert (entry.external_attr >> 16) & 0o170000 != 0o120000
                assert entry.filename in {"mlflow.db", "snapshot_manifest.json"} or entry.filename.startswith("artifacts/")
            archive.extractall(target)
        for name, metadata in manifest["files"].items():
            path = target / name
            assert path.stat().st_size == metadata["size"] and sha256(path) == metadata["sha256"]
        with contextlib.closing(sqlite3.connect(target / "mlflow.db")) as db:
            assert db.execute("PRAGMA integrity_check").fetchone()[0] == "ok"
        assert not (root / "artifacts").exists(), "Hay artefactos locales sin DB; usa una sesión Colab limpia."
        if (target / "artifacts").exists():
            shutil.copytree(target / "artifacts", root / "artifacts")
        shutil.copyfile(target / "mlflow.db", root / "mlflow.db")
    print("Historial restaurado:", source.name)


class A4Tracking:
    def __init__(self, root, snapshots, output, run_id, interval=300):
        self.root, self.snapshots, self.output = Path(root), Path(snapshots), Path(output)
        self.run_id, self.interval = run_id, interval
        self.last_backup = 0
        self.parents, self.attempts = {}, {}
        self.snapshots.mkdir(parents=True, exist_ok=True)
        tracking_restore(self.root, self.snapshots)
        mlflow.set_tracking_uri("sqlite:///" + (self.root / "mlflow.db").as_posix())
        self.client = MlflowClient()
        name = "G15_A4_SciBERT"
        experiment = self.client.get_experiment_by_name(name)
        self.experiment = (experiment.experiment_id if experiment else
            self.client.create_experiment(name, artifact_location=(self.root / "artifacts/scibert").as_uri()))
        # Solo el mismo RUN_ID: las sesiones anteriores terminaron sin cierre.
        previous = self.client.search_runs([self.experiment], filter_string=f"tags.a4_run_id = '{run_id}'")
        for run in previous:
            if run.info.status == "RUNNING":
                self.client.set_terminated(run.info.run_id, status="KILLED")
        self.backup(force=True)

    def backup(self, force=False):
        if not force and time.monotonic() - self.last_backup < self.interval:
            return
        created = dt.datetime.now(dt.timezone.utc)
        sid = created.strftime("%Y%m%dT%H%M%S%fZ_") + uuid.uuid4().hex[:8]
        with tempfile.TemporaryDirectory() as tmp:
            stage = Path(tmp) / "stage"
            stage.mkdir()
            with contextlib.closing(sqlite3.connect(self.root / "mlflow.db")) as source:
                with contextlib.closing(sqlite3.connect(stage / "mlflow.db")) as dest:
                    source.backup(dest)
                    assert dest.execute("PRAGMA integrity_check").fetchone()[0] == "ok"
            if (self.root / "artifacts").exists():
                shutil.copytree(self.root / "artifacts", stage / "artifacts")
            paths = sorted(p for p in stage.rglob("*") if p.is_file())
            assert not any(p.is_symlink() for p in stage.rglob("*"))
            manifest = dict(schema_version=1, snapshot_id=sid, created_at_utc=created.isoformat(),
                mlflow_version=mlflow.__version__, canonical_root=str(self.root), purpose="scibert_training",
                files={p.relative_to(stage).as_posix(): {"sha256": sha256(p), "size": p.stat().st_size} for p in paths})
            save_json(stage / "snapshot_manifest.json", manifest)
            packed = Path(tmp) / "snapshot.zip"
            with zipfile.ZipFile(packed, "w", zipfile.ZIP_DEFLATED) as archive:
                for path in sorted(p for p in stage.rglob("*") if p.is_file()):
                    archive.write(path, path.relative_to(stage).as_posix())
            digest = sha256(packed)
            destination = self.snapshots / sid
            destination.mkdir(exist_ok=False)
            shutil.copyfile(packed, destination / "snapshot.zip")
            assert sha256(destination / "snapshot.zip") == digest
            (destination / "snapshot.sha256").write_text(f"{digest}  snapshot.zip\n")
            save_json(destination / "COMPLETE.json", dict(schema_version=1, snapshot_id=sid,
                created_at_utc=created.isoformat(), mlflow_version=mlflow.__version__,
                zip_sha256=digest, zip_size=packed.stat().st_size))
        self.last_backup = time.monotonic()
        print("MLflow respaldado:", destination)

    def parent(self, config):
        if config not in self.parents:
            runs = self.client.search_runs([self.experiment],
                filter_string=f"tags.a4_run_id = '{self.run_id}' and tags.config = '{config}' and tags.kind = 'configuration'")
            if len(runs) > 1:
                raise ValueError("Más de un padre para la misma configuración")
            self.parents[config] = (runs[0].info.run_id if runs else self.client.create_run(self.experiment,
                tags={"mlflow.runName": f"{self.run_id}/{config}", "a4_run_id": self.run_id,
                      "config": config, "kind": "configuration"}).info.run_id)
        return self.parents[config]

    def metrics(self, run, values, step=0):
        for key, value in values.items():
            if isinstance(value, numbers.Real) and math.isfinite(float(value)):
                self.client.log_metric(run, key, float(value), step=int(step))

    def reports(self, config, run=None):
        run = run or self.parent(config)
        for directory, artifact_path in [(self.output, "provenance"), (self.output / config, "reports")]:
            for path in sorted(directory.iterdir()):
                if path.is_file() and path.suffix in {".json", ".csv", ".png", ".txt"}:
                    self.client.log_artifact(run, str(path), artifact_path=artifact_path)

    @contextlib.contextmanager
    def evaluation(self, config, directory, policy="v2_fp32"):
        parent = self.parent(config)
        rid = self.client.create_run(self.experiment, tags={
            "mlflow.runName": f"{config}/evaluation_{policy}_{uuid.uuid4().hex[:8]}",
            "mlflow.parentRunId": parent, "a4_run_id": self.run_id, "config": config,
            "kind": "evaluation", "evaluation_policy": policy,
            "canonical_precision": "fp32", "drive_output": str(directory)}).info.run_id
        try:
            yield rid
            self.client.log_artifacts(rid, str(directory), artifact_path="evaluation")
            self.client.set_terminated(rid, "FINISHED")
            self.client.set_tag(parent, "latest_evaluation_run", rid)
            self.backup(force=True)
        except BaseException as error:
            self.client.set_tag(rid, "failure", f"{type(error).__name__}: {error}"[:2000])
            self.client.set_terminated(rid, "KILLED" if isinstance(error, KeyboardInterrupt) else "FAILED")
            try:
                self.backup(force=True)
            except Exception as backup_error:
                print("Falló el respaldo de evaluación:", backup_error)
            raise

    @contextlib.contextmanager
    def attempt(self, config, spec, checkpoint):
        parent = self.parent(config)
        self.client.update_run(parent, status="RUNNING")
        rid = self.client.create_run(self.experiment, tags={"mlflow.runName": f"{config}/attempt_{uuid.uuid4().hex[:8]}",
            "mlflow.parentRunId": parent, "a4_run_id": self.run_id, "config": config,
            "kind": "attempt", "validation_reference": "prelabels_and_available_gold"}).info.run_id
        self.attempts[config] = rid
        try:
            (self.output / config).mkdir(parents=True, exist_ok=True)
            for key, value in spec.items():
                if not isinstance(value, (dict, list)):
                    self.client.log_param(rid, key, str(value)[:5000])
            self.client.log_param(rid, "config", config)
            self.client.log_param(rid, "resume_checkpoint", str(checkpoint))
            self.client.set_tag(rid, "drive_output", str(self.output / config))
            self.reports(config, rid)
            self.backup(force=True)
            yield rid
        except BaseException as error:
            self.client.set_tag(rid, "failure", f"{type(error).__name__}: {error}"[:2000])
            self.client.set_terminated(rid, "KILLED" if isinstance(error, KeyboardInterrupt) else "FAILED")
            self.client.set_terminated(parent, "FAILED")
            try:
                self.backup(force=True)
            except Exception as backup_error:
                print("Falló el respaldo de cierre:", backup_error)
            raise
        else:
            self.reports(config, rid)
            self.client.set_terminated(rid, "FINISHED")
            self.client.set_terminated(parent, "FINISHED")
            self.backup(force=True)


def commit_checkpoint(path):
    path = Path(path)
    required = ["trainer_state.json", "optimizer.pt", "scheduler.pt", "training_args.bin"]
    assert all((path / name).is_file() for name in required)
    assert list(path.glob("*safetensors")) or list(path.glob("pytorch_model*.bin"))
    assert list(path.glob("rng_state*.pth")), "Falta el estado aleatorio para reanudar"
    files = {p.name: {"sha256": sha256(p), "size": p.stat().st_size} for p in path.iterdir() if p.is_file() and p.name != "A4_COMPLETE.json"}
    save_json(path / "A4_COMPLETE.json", {"files": files})


def verified_checkpoint(directory):
    directory = Path(directory)
    candidates = sorted(directory.glob("checkpoint-*"), key=lambda p: int(p.name.split("-")[-1]), reverse=True)
    for path in candidates:
        if not (path / "A4_COMPLETE.json").exists():
            print("Se omite checkpoint sin cierre:", path)
            continue
        files = json.loads((path / "A4_COMPLETE.json").read_text())["files"]
        if all((path / name).is_file() and (path / name).stat().st_size == meta["size"] and sha256(path / name) == meta["sha256"] for name, meta in files.items()):
            # Trainer vuelve a cargar también el mejor checkpoint previo.
            state = json.loads((path / "trainer_state.json").read_text())
            best = state.get("best_model_checkpoint")
            if best and not Path(best).is_dir():
                raise ValueError(f"Falta el mejor checkpoint requerido: {best}")
            if best and Path(best) != path:
                marker = Path(best) / "A4_COMPLETE.json"
                assert marker.is_file(), "El mejor checkpoint previo no tiene cierre"
                best_files = json.loads(marker.read_text())["files"]
                assert all((Path(best) / name).is_file() and sha256(Path(best) / name) == meta["sha256"]
                           for name, meta in best_files.items()), "Mejor checkpoint previo corrupto"
            return str(path)
        print("Se omite checkpoint con hashes inválidos:", path)
    if candidates:
        raise ValueError("Hay checkpoints pero ninguno completo. No se reinicia silenciosamente.")
    return None


class A4MLflowCallback(TrainerCallback):
    def __init__(self, tracking, run):
        self.tracking, self.run = tracking, run

    def on_log(self, args, state, control, logs=None, **kwargs):
        self.tracking.metrics(self.run, logs or {}, state.global_step)

    def on_step_end(self, args, state, control, **kwargs):
        self.tracking.backup()

    def on_save(self, args, state, control, **kwargs):
        path = Path(args.output_dir) / f"checkpoint-{state.global_step}"
        commit_checkpoint(path)
        self.tracking.client.set_tag(self.run, "latest_complete_checkpoint", str(path))
        self.tracking.client.log_artifact(self.run, str(path / "A4_COMPLETE.json"),
            artifact_path=f"checkpoints/{path.name}")
        self.tracking.backup(force=True)
