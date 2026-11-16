"""Recuperacion puntual autorizada de a5_luna_test_01. Importar no modifica archivos."""
from pathlib import Path
from datetime import datetime, timezone
import hashlib
import json
import os
import shutil

EXPECTED_JOURNAL_SHA256 = "a8277345f716f370df0d5d6837f1b4c3bda69d9a79f5c0fbb96c43643bdf5029"
EXPECTED_UNCERTAIN_KEY = "f0c438e1646c9e08480a4180b66ecf8c9f48e7a17e326c60e9725bb127c2ad49"


def prepare_recovery(a5, cfg, bundle, plan, snapshot, *,
                     confirm_no_active_writer=False, authorize_replay=False):
    """Respalda y cierra solo el intento auditado. No realiza inferencia."""
    if not confirm_no_active_writer or not authorize_replay:
        raise ValueError("Confirmar ausencia de otro escritor y autorizar posible cobro repetido")
    if cfg["run_id"] != "a5_luna_test_01" or cfg["model"] != "gpt-6-luna":
        raise ValueError("Esta recuperacion es exclusiva de Luna test 01")
    root = Path(cfg["output_dir"]) / cfg["run_id"]
    journal = root / "attempts.jsonl"
    raw = journal.read_bytes()
    if hashlib.sha256(raw).hexdigest() != EXPECTED_JOURNAL_SHA256:
        raise ValueError("El diario cambio o ya se recupero: detener y revisar; no repetir esta celda")
    if (root / "run_summary.json").exists():
        raise ValueError("Ya existe resumen final: no corresponde esta recuperacion")
    previous = json.loads((root / "manifest.json").read_text(encoding="utf-8"))
    current = {
        "runtime_version": a5.VERSION, "runtime_sha256": a5.file_hash(a5.__file__),
        "config": {k: v for k, v in cfg.items() if k != "output_dir"},
        "data": bundle["provenance"], "snapshot_sha256": a5.digest(snapshot),
        "case_data_sha256": a5.digest(bundle["cases"]),
        "example_data_sha256": a5.digest(bundle["examples"]),
        "example_gold_sha256": a5.digest(bundle["example_gold"]),
        "task_keys": [t["request_key"] for t in plan["tasks"]],
        "synthetic": bundle["synthetic"],
    }
    if previous["fingerprint"] != a5.digest(current):
        changed = [k for k in current if current[k] != previous["spec"].get(k)]
        raise ValueError("Configuracion/datos/codigo distintos del original: " + ", ".join(changed))
    events = [json.loads(line) for line in raw.decode("utf-8").splitlines() if line.strip()]
    starts = {(e["request_key"], e["attempt"]) for e in events if e["event"] == "start"}
    ends = {(e["request_key"], e["attempt"]) for e in events if e["event"] == "outcome"}
    if starts - ends != {(EXPECTED_UNCERTAIN_KEY, 1)}:
        raise ValueError("Los intentos inciertos no coinciden con la auditoria")
    terminal = {e["request_key"] for e in events if e["event"] == "outcome" and e["terminal"]}
    if len(terminal) != 10908 or len(plan["tasks"]) != 11872:
        raise ValueError("Conteos distintos a los auditados")
    if any(e.get("requires_review") for e in events if e["event"] == "outcome"):
        raise ValueError("Existen otros resultados que requieren revision")
    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S%fZ")
    backup = root / "recovery_backups" / stamp
    backup.mkdir(parents=True, exist_ok=False)
    for name in ("attempts.jsonl", "manifest.json", "progress.json", "plan.json", "RUNNING.lock"):
        source = root / name
        if source.exists():
            shutil.copy2(source, backup / name)
    if (backup / "attempts.jsonl").read_bytes() != raw:
        raise ValueError("El respaldo del diario no coincide")
    receipt = {
        "at": a5.utcnow(), "run_id": cfg["run_id"],
        "reason": "Drive journal behind progress after Colab disconnection",
        "user_authorized_replay_and_possible_duplicate_charge": True,
        "original_journal_sha256": EXPECTED_JOURNAL_SHA256,
        "preserved_responses": 10908, "pending_requests": 964,
        "uncertain_request_key": EXPECTED_UNCERTAIN_KEY,
        "missing_responses_reported_by_progress": 692,
        "api_called": False,
    }
    a5.write_json(backup / "recovery_authorization.json", receipt)
    if journal.read_bytes() != raw:
        raise ValueError("Otro proceso modifico el diario: no continuar")
    result = {"ok": False, "status_code": None, "raw_body": None,
              "elapsed_seconds": 0.0, "error_type": "authorized_replay_after_lost_response"}
    event = {
        "event": "outcome", "request_key": EXPECTED_UNCERTAIN_KEY,
        "attempt": 1, "at": a5.utcnow(), "terminal": False,
        "result": result, "parsed": a5.unpack_response(result, cfg),
        "reason": "manual_authorized_uncertain_replay",
        "automatic_retry": False, "retryable_on_resume": True,
        "requires_review": False,
        "user_authorized_possible_duplicate_charge": True,
        "recovery_receipt": str(backup / "recovery_authorization.json"),
    }
    # Append-only: no elimina inicios, respuestas previas ni datos del manifiesto.
    with journal.open("ab") as stream:
        if raw and not raw.endswith(b"\n"):
            stream.write(b"\n")
        stream.write((a5.dumps(event) + "\n").encode("utf-8"))
        stream.flush()
        os.fsync(stream.fileno())
    (root / "RUNNING.lock").unlink(missing_ok=True)
    return {"status": "ready_to_resume", "preserved_responses": 10908,
            "pending_requests": 964, "backup_dir": str(backup),
            "api_called": False, "next_step": "Ejecutar bloque 9 con la misma configuracion"}
