"""Importa resultados A5 ya guardados al historial MLflow, sin inferencia ni AWS."""
from __future__ import annotations

from collections import Counter
from contextlib import closing
from datetime import datetime, timezone
from pathlib import Path, PurePosixPath
import hashlib
import json
import math
import os
import shutil
import sqlite3
import tempfile
import uuid
import zipfile

VERSION = "a5-tracking-v1"
MLFLOW_VERSION = "3.17.2"
CANONICAL_ROOT = "/opt/maia/a4_tracking"
EXPERIMENT = "G15_A5_Comerciales"


def read(path):
    return json.loads(Path(path).read_text(encoding="utf-8-sig"))


def write(path, value):
    Path(path).write_text(json.dumps(value, ensure_ascii=False, indent=2, allow_nan=False) + "\n", encoding="utf-8")


def sha(path):
    h = hashlib.sha256()
    with Path(path).open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()


def digest(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True, allow_nan=False).encode()).hexdigest()


def validate_snapshot(folder, destination=None):
    """Verifica recibo, rutas, archivos e integridad SQLite antes de restaurar."""
    folder = Path(folder).resolve()
    receipt = read(folder / "COMPLETE.json")
    packed = folder / "snapshot.zip"
    if receipt.get("schema_version") != 1 or receipt.get("mlflow_version") != MLFLOW_VERSION:
        raise ValueError("Respaldo incompatible: se requiere MLflow " + MLFLOW_VERSION)
    if packed.stat().st_size != receipt["zip_size"] or sha(packed) != receipt["zip_sha256"]:
        raise ValueError("El ZIP no coincide con COMPLETE.json")
    if (folder / "snapshot.sha256").read_text().split()[0] != receipt["zip_sha256"]:
        raise ValueError("Checksum del ZIP incompatible")
    if destination is not None:
        destination = Path(destination)
        if destination.exists() and any(destination.iterdir()):
            raise ValueError("No se restaura sobre un directorio ocupado")
    with zipfile.ZipFile(packed) as archive:
        names = archive.namelist()
        if len(names) != len(set(names)):
            raise ValueError("ZIP con nombres duplicados")
        for info in archive.infolist():
            p = PurePosixPath(info.filename)
            if (p.is_absolute() or ".." in p.parts or "\\" in info.filename or ":" in info.filename
                    or (info.external_attr >> 16) & 0o170000 == 0o120000
                    or not (info.filename in {"mlflow.db", "snapshot_manifest.json"}
                            or info.filename.startswith("artifacts/"))):
                raise ValueError("Ruta no permitida dentro del ZIP")
        manifest = json.loads(archive.read("snapshot_manifest.json"))
        if (manifest.get("schema_version") != 1 or manifest.get("canonical_root") != CANONICAL_ROOT
                or manifest.get("snapshot_id") != receipt["snapshot_id"]
                or manifest.get("mlflow_version") != MLFLOW_VERSION
                or set(names) != set(manifest["files"]) | {"snapshot_manifest.json"}):
            raise ValueError("Manifiesto de respaldo incompatible")
        for name, meta in manifest["files"].items():
            content = archive.read(name)
            if len(content) != meta["size"] or hashlib.sha256(content).hexdigest() != meta["sha256"]:
                raise ValueError("Archivo alterado en el ZIP: " + name)
        with closing(sqlite3.connect(":memory:")) as db:
            db.deserialize(archive.read("mlflow.db"))
            if db.execute("PRAGMA integrity_check").fetchone()[0] != "ok":
                raise ValueError("Base SQLite dañada")
        if destination is not None:
            destination.mkdir(parents=True, exist_ok=True)
            archive.extractall(destination)
    return {"receipt": receipt, "manifest": manifest}


def database_rows(path):
    """Fotografía de todas las filas originales, no solo el número de runs."""
    with closing(sqlite3.connect(Path(path).as_uri() + "?mode=ro", uri=True)) as db:
        tables = [r[0] for r in db.execute("SELECT name FROM sqlite_master WHERE type='table'")
                  if not r[0].startswith("sqlite_")]
        return {t: Counter(db.execute('SELECT * FROM "' + t.replace('"', '""') + '"').fetchall())
                for t in tables}


def snapshot_rows(folder):
    with zipfile.ZipFile(Path(folder) / "snapshot.zip") as archive:
        with closing(sqlite3.connect(":memory:")) as db:
            db.deserialize(archive.read("mlflow.db"))
            tables = [r[0] for r in db.execute("SELECT name FROM sqlite_master WHERE type='table'")
                      if not r[0].startswith("sqlite_")]
            return {t: Counter(db.execute('SELECT * FROM "' + t.replace('"', '""') + '"').fetchall())
                    for t in tables}


def shared_inventory(folder):
    """Solo respaldos completos; los archivos parciales no se consideran publicados."""
    return {str(p.parent): sha(p) for p in Path(folder).glob("*/COMPLETE.json")}


def publish_snapshot(snapshot_dir, shared_snapshots):
    """Publica una carpeta nueva en Drive montado; nunca sustituye respaldos ajenos.

    Exige que el acumulado incluya todas las filas y artefactos del último
    respaldo compartido. No supone que su fecha más reciente implique inclusión.
    """
    source, shared = Path(snapshot_dir).resolve(), Path(shared_snapshots).resolve()
    if not shared.is_dir():
        raise FileNotFoundError("No se encuentra el acceso directo MLFLOW_SNAPSHOTS_SEBAS; monta Drive y revisa la ruta")
    if source == shared or shared.is_relative_to(source) or source.is_relative_to(shared):
        raise ValueError("El respaldo propio y el destino compartido deben estar separados")
    local = validate_snapshot(source)
    sid = local["receipt"]["snapshot_id"]
    if not sid or sid in {".", ".."} or Path(sid).name != sid or "/" in sid or "\\" in sid:
        raise ValueError("Identificador de snapshot inválido")
    lock = shared / ".a5_publish.lock"
    fd = os.open(lock, os.O_CREAT | os.O_EXCL | os.O_WRONLY, 0o600)
    os.close(fd)
    try:
        inventory = shared_inventory(shared)
        if not inventory:
            raise ValueError("El destino no contiene respaldos completos de A4; revisa el acceso directo")
        latest = max((Path(p) for p in inventory),
                     key=lambda p: datetime.fromisoformat(read(p / "COMPLETE.json")["created_at_utc"]))
        prior = validate_snapshot(latest)
        new_rows, old_rows = snapshot_rows(source), snapshot_rows(latest)
        for table, rows in old_rows.items():
            if rows - new_rows.get(table, Counter()):
                raise ValueError("El respaldo compartido contiene historial ausente en tu acumulado. No se publica: solicita un respaldo actualizado e incorpora A5 sobre él.")
        for name, meta in prior["manifest"]["files"].items():
            if name.startswith("artifacts/") and local["manifest"]["files"].get(name) != meta:
                raise ValueError("El respaldo compartido contiene artefactos ausentes o distintos. No se publica.")
        if datetime.fromisoformat(local["receipt"]["created_at_utc"]) < datetime.fromisoformat(prior["receipt"]["created_at_utc"]):
            raise ValueError("Tu respaldo es anterior al último compartido; genera uno acumulado actualizado")
        destination = shared / sid
        if (destination / "COMPLETE.json").exists():
            existing = validate_snapshot(destination)
            if existing["receipt"]["zip_sha256"] != local["receipt"]["zip_sha256"]:
                raise ValueError("Ya existe otro contenido con el mismo snapshot_id; no se sobrescribe")
            return {"status": "already_published", "shared_snapshot_dir": str(destination), "aws_modified": False}
        destination.mkdir(exist_ok=True)
        expected = {"snapshot.zip", "snapshot.sha256", "A5_IMPORT_REPORT.json"}
        if any(p.name not in expected or not p.is_file() for p in destination.iterdir()):
            raise ValueError("Carpeta de destino ocupada por otros archivos; no se sobrescribe")
        for name in ("snapshot.zip", "snapshot.sha256", "A5_IMPORT_REPORT.json"):
            if (source / name).is_file():
                shutil.copyfile(source / name, destination / name)
                if sha(source / name) != sha(destination / name):
                    raise ValueError("La copia no superó la verificación: " + name)
        if shared_inventory(shared) != inventory:
            raise ValueError("El historial compartido cambió durante la copia. Se dejó sin COMPLETE.json; revisa el nuevo respaldo antes de reintentar")
        # Publicar el marcador únicamente tras verificar los datos y volver a revisar el origen compartido.
        shutil.copyfile(source / "COMPLETE.json", destination / "COMPLETE.json")
        try:
            validate_snapshot(destination)
        except Exception:
            (destination / "COMPLETE.json").unlink(missing_ok=True)
            raise
        return {"status": "published", "shared_snapshot_dir": str(destination),
                "previous_shared_snapshot_id": prior["receipt"]["snapshot_id"],
                "shared_history_preserved": True, "aws_modified": False}
    finally:
        lock.unlink(missing_ok=True)


def assert_preserved(before, path, artifacts, root):
    after = database_rows(path)
    for table, rows in before.items():
        if rows - after.get(table, Counter()):
            raise ValueError("Se alteró el historial previo en la tabla " + table)
    for name, meta in artifacts.items():
        if name.startswith("artifacts/") and sha(Path(root) / name) != meta["sha256"]:
            raise ValueError("Se alteró un artefacto previo: " + name)


def load_results(folder):
    folder = Path(folder).resolve()
    required = ["manifest.json", "metrics.json", "predictions.json", "run_summary.json", "attempts.jsonl"]
    for name in required:
        if not (folder / name).is_file():
            raise FileNotFoundError(f"Falta {folder / name}. Copia la ejecución completa desde Drive; no repitas la API.")
    manifest, summary = read(folder / "manifest.json"), read(folder / "run_summary.json")
    spec = manifest["spec"]
    if digest(spec) != manifest["fingerprint"]:
        # El runtime usa JSON compacto, ensure_ascii=False. Comprobar con su función exacta.
        import a5_runtime
        if a5_runtime.digest(spec) != manifest["fingerprint"]:
            raise ValueError("El manifiesto A5 cambió")
    cfg = spec["config"]
    if spec["synthetic"] or cfg["demo"] or summary["status"] != "completed":
        raise ValueError("Solo se importan resultados reales completos; nunca demo ni planes sin API")
    predictions, metrics = read(folder / "predictions.json"), read(folder / "metrics.json")
    if not predictions or len(predictions) != summary["records"] or any(p.get("synthetic") for p in predictions):
        raise ValueError("Predicciones incompletas o sintéticas")
    conditions = {p["condition"] for p in predictions}
    if len(metrics) != len(conditions) or {m["condition"] for m in metrics} != conditions:
        raise ValueError("Faltan métricas por condición")
    if len({p["request_key"] for p in predictions}) != len(predictions):
        raise ValueError("Predicciones duplicadas")
    if {p["request_key"] for p in predictions} != set(spec["task_keys"]):
        raise ValueError("Las predicciones no corresponden al plan original")
    for metric in metrics:
        rows = [p for p in predictions if p["condition"] == metric["condition"] and p["replicate"] == 0]
        if metric["n"] != len(rows) or not rows:
            raise ValueError("Las métricas no corresponden a las predicciones principales")
    events = [json.loads(line) for line in (folder / "attempts.jsonl").read_text(encoding="utf-8").splitlines() if line.strip()]
    return {"folder": folder, "config": cfg, "summary": summary, "predictions": predictions,
            "metrics": metrics, "events": events,
            "hashes": {n: sha(folder / n) for n in required}}


def flat_metrics(values, prefix=""):
    out = {}
    for name, value in values.items():
        key = prefix + name.replace("/", "_")
        if isinstance(value, dict):
            out.update(flat_metrics(value, key + "/"))
        elif isinstance(value, (int, float)) and not isinstance(value, bool) and math.isfinite(value):
            out[key] = float(value)
    return out


def import_results(client, experiment_id, data):
    """Una ejecución MLflow por condición. Repetir una importación no la duplica."""
    cfg = data["config"]
    bundle_hash = digest(data["hashes"])
    imported = []
    for metric in data["metrics"]:
        condition = metric["condition"]
        key = digest([cfg["run_id"], cfg["model"], condition])
        runs = client.search_runs([experiment_id], filter_string=f"tags.a5_import_key = '{key}'")
        if len(runs) > 1:
            raise ValueError("Importación duplicada en el historial")
        if runs and runs[0].data.tags.get("a5_bundle_sha256") != bundle_hash:
            raise ValueError("Cambió una ejecución ya importada: conserva los resultados originales")
        if runs and runs[0].info.status == "FINISHED":
            imported.append(runs[0].info.run_id)
            continue
        tags = {"mlflow.runName": cfg["run_id"] + "/" + condition, "a5_run_id": cfg["run_id"],
                "a5_import_key": key, "a5_bundle_sha256": bundle_hash, "phase": "A5",
                "condition": condition, "evaluation_split": cfg["split"],
                "purpose": "connection_check" if cfg.get("limit_cases") == 1 else "evaluation",
                "test_scored": str(cfg["split"] == "test").lower(), "source": "saved_results_no_inference"}
        rid = runs[0].info.run_id if runs else client.create_run(experiment_id, tags=tags).info.run_id
        try:
            allowed = ("provider", "model", "split", "dataset_version", "guide_version", "variant", "temperature",
                       "max_output_tokens", "response_format", "seed", "input_policy_version",
                       "fewshot_reviewed", "limit_cases", "pricing_source", "pricing_date")
            for name in allowed:
                if name in cfg:
                    client.log_param(rid, name, str(cfg[name]))
            client.log_param(rid, "condition", condition)
            values = flat_metrics(metric)
            keys = {p["request_key"] for p in data["predictions"] if p["condition"] == condition}
            outcomes = [e for e in data["events"] if e["event"] == "outcome" and e["request_key"] in keys]
            values.update(attempts=len(outcomes),
                          cost_known_attempts_usd=sum(e["parsed"].get("estimated_cost_usd") or 0 for e in outcomes),
                          unknown_cost_attempts=sum(not e["parsed"].get("cost_known", False) for e in outcomes),
                          input_tokens=sum((e["parsed"].get("usage") or {}).get("prompt_tokens", 0) for e in outcomes),
                          output_tokens=sum((e["parsed"].get("usage") or {}).get("completion_tokens", 0) for e in outcomes))
            for name, value in values.items():
                client.log_metric(rid, name, float(value))
            returned = sorted({str(p.get("returned_model")) for p in data["predictions"] if p["condition"] == condition})
            client.set_tag(rid, "returned_models", json.dumps(returned))
            # Lista cerrada: nunca se suben claves, requests, textos ni respuestas originales.
            with tempfile.TemporaryDirectory() as tmp:
                report = Path(tmp) / "a5_condition.json"
                write(report, {"condition": condition, "metrics": metric, "ledger": values,
                               "source_file_hashes": data["hashes"], "importer_version": VERSION})
                client.log_artifact(rid, str(report), artifact_path="reports")
            matrix = data["folder"] / ("confusion_" + condition + ".csv")
            if matrix.is_file() and matrix.parent == data["folder"]:
                client.log_artifact(rid, str(matrix), artifact_path="reports")
            client.set_terminated(rid, "FINISHED")
        except Exception:
            client.set_terminated(rid, "FAILED")
            raise
        imported.append(rid)
    return imported


def incorporate(base_snapshot, results_dir, snapshots_dir, work_parent=None):
    """Restaura en temporal, añade A5, comprueba A4 y publica otro snapshot completo.

    No modifica el respaldo fuente ni llama APIs. La salida es una rama acumulada
    desde el respaldo recibido; no sincroniza cambios posteriores de Sebastián.
    """
    import mlflow
    from mlflow import MlflowClient
    if mlflow.__version__ != MLFLOW_VERSION:
        raise ValueError("Instala mlflow==" + MLFLOW_VERSION + " en un entorno separado")
    base_snapshot = Path(base_snapshot).resolve()
    snapshots_dir = Path(snapshots_dir).resolve()
    data = load_results(results_dir)
    original = validate_snapshot(base_snapshot)
    if snapshots_dir == base_snapshot or snapshots_dir.is_relative_to(base_snapshot) or base_snapshot.is_relative_to(snapshots_dir):
        raise ValueError("Los respaldos nuevos deben estar separados del respaldo original")
    snapshots_dir.mkdir(parents=True, exist_ok=True)
    lock = snapshots_dir / ".a5_tracking.lock"
    fd = os.open(lock, os.O_CREAT | os.O_EXCL | os.O_WRONLY, 0o600)
    os.close(fd)
    try:
        candidates = []
        for marker in snapshots_dir.glob("*/COMPLETE.json"):
            receipt = read(marker)
            if receipt.get("base_zip_sha256") != original["receipt"]["zip_sha256"]:
                raise ValueError("La salida ya contiene otra rama de historial; no se mezclan bases automáticamente")
            candidates.append((receipt["created_at_utc"], marker.parent))
        source = max(candidates)[1] if candidates else base_snapshot
        previous = validate_snapshot(source)
        with tempfile.TemporaryDirectory(dir=work_parent) as tmp:
            root = Path(tmp) / "tracking"
            validate_snapshot(source, root)
            db_path = root / "mlflow.db"
            before = database_rows(db_path)
            with closing(sqlite3.connect(db_path)) as db:
                old_runs = db.execute("SELECT count(*) FROM runs").fetchone()[0]
            client = MlflowClient(tracking_uri="sqlite:///" + db_path.as_posix())
            experiment = client.get_experiment_by_name(EXPERIMENT)
            local_artifacts = root / "artifacts/a5_commercials"
            if experiment is None:
                eid = client.create_experiment(EXPERIMENT, artifact_location=local_artifacts.as_uri())
            else:
                eid = experiment.experiment_id
                # Solo las URI de A5 se reubican en esta copia temporal.
                with closing(sqlite3.connect(db_path)) as db:
                    db.execute("UPDATE experiments SET artifact_location=? WHERE experiment_id=?", (local_artifacts.as_uri(), eid))
                    for rid, in db.execute("SELECT run_uuid FROM runs WHERE experiment_id=?", (eid,)).fetchall():
                        db.execute("UPDATE runs SET artifact_uri=? WHERE run_uuid=?", ((local_artifacts / rid / "artifacts").as_uri(), rid))
                    db.commit()
            try:
                ids = import_results(client, eid, data)
            finally:
                # Versión fijada: liberar SQLite antes de empaquetar y limpiar el temporal en Windows.
                client._tracking_client.store.engine.dispose()
            # Restablecer rutas portables para el visor AWS, sin cambiar rutas de A4.
            canonical = "file://" + CANONICAL_ROOT + "/artifacts/a5_commercials"
            with closing(sqlite3.connect(db_path)) as db:
                db.execute("UPDATE experiments SET artifact_location=? WHERE experiment_id=?", (canonical, eid))
                for rid, in db.execute("SELECT run_uuid FROM runs WHERE experiment_id=?", (eid,)).fetchall():
                    db.execute("UPDATE runs SET artifact_uri=? WHERE run_uuid=?", (canonical + "/" + rid + "/artifacts", rid))
                db.commit()
                final_runs = db.execute("SELECT count(*) FROM runs").fetchone()[0]
                if db.execute("PRAGMA integrity_check").fetchone()[0] != "ok":
                    raise ValueError("La base acumulada falló la verificación")
            assert_preserved(before, db_path, previous["manifest"]["files"], root)
            sid = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S%fZ_") + uuid.uuid4().hex[:8]
            created = datetime.now(timezone.utc).isoformat()
            report = {"source_snapshot_id": original["receipt"]["snapshot_id"], "previous_snapshot_id": previous["receipt"]["snapshot_id"],
                      "base_zip_sha256": original["receipt"]["zip_sha256"], "previous_runs": old_runs,
                      "total_runs": final_runs, "added_runs": final_runs - old_runs, "a5_run_ids": ids,
                      "source_run_id": data["config"]["run_id"], "experiment": EXPERIMENT,
                      "previous_rows_and_artifacts_preserved": True, "api_called": False, "aws_modified": False}
            files = {p.relative_to(root).as_posix(): {"sha256": sha(p), "size": p.stat().st_size}
                     for p in root.rglob("*") if p.is_file() and (p.name == "mlflow.db" or "artifacts" in p.relative_to(root).parts)}
            manifest = {"schema_version": 1, "snapshot_id": sid, "created_at_utc": created,
                        "mlflow_version": MLFLOW_VERSION, "canonical_root": CANONICAL_ROOT,
                        "purpose": "a4_history_plus_a5_commercials", "files": files, "a5_import": report}
            write(root / "snapshot_manifest.json", manifest)
            destination = snapshots_dir / sid
            destination.mkdir(exist_ok=False)
            packed = destination / "snapshot.zip"
            with zipfile.ZipFile(packed, "w", zipfile.ZIP_DEFLATED) as archive:
                for name in sorted(set(files) | {"snapshot_manifest.json"}):
                    archive.write(root / name, name)
            checksum = sha(packed)
            (destination / "snapshot.sha256").write_text(checksum + "  snapshot.zip\n", encoding="utf-8")
            receipt = {"schema_version": 1, "snapshot_id": sid, "created_at_utc": created,
                       "mlflow_version": MLFLOW_VERSION, "zip_sha256": checksum, "zip_size": packed.stat().st_size,
                       "base_zip_sha256": original["receipt"]["zip_sha256"]}
            # Marcador final después de escribir y verificar el ZIP.
            write(destination / "COMPLETE.json", receipt)
            try:
                validate_snapshot(destination)
            except Exception:
                (destination / "COMPLETE.json").unlink(missing_ok=True)
                raise
            write(destination / "A5_IMPORT_REPORT.json", report)
            return {"snapshot_dir": str(destination), **report}
    finally:
        lock.unlink(missing_ok=True)
