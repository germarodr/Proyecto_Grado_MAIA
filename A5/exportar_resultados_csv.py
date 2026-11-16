"""Exporta predicciones comerciales finales a CSV. No realiza inferencia."""
from pathlib import Path
from collections import Counter
import csv
import hashlib
import json
import math
import re

LABELS = ["Background", "Gap", "Basis", "Comparison", "Application",
          "Improvement/Modification", "Evidence", "Identification of the Originator",
          "Further Reading"]
CONDITIONS = {"base-generic-zero", "base-generic-few", "base-specific-zero", "base-specific-few"}


def read(path):
    return json.loads(Path(path).read_text(encoding="utf-8-sig"))


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def export_results(run_dir, gold_path=None):
    """Un CSV completo y cuatro CSV compatibles por inst_key con la comparacion A5."""
    run_dir = Path(run_dir)
    manifest = read(run_dir / "manifest.json")
    spec = manifest["spec"]
    fingerprint = hashlib.sha256(json.dumps(spec, ensure_ascii=False, sort_keys=True,
                                            allow_nan=False).encode("utf-8")).hexdigest()
    if fingerprint != manifest["fingerprint"]:
        raise ValueError("Manifiesto modificado")
    cfg = spec["config"]
    summary = read(run_dir / "run_summary.json")
    if cfg["split"] != "test" or cfg["demo"] or spec["synthetic"] or summary["status"] != "completed":
        raise ValueError("Se requieren resultados finales reales de T_B")
    predictions = read(run_dir / "predictions.json")
    if len(predictions) != summary["records"] or len({p["request_key"] for p in predictions}) != len(predictions):
        raise ValueError("Predicciones incompletas o duplicadas")
    if {p["request_key"] for p in predictions} != set(spec["task_keys"]):
        raise ValueError("Las predicciones no corresponden al plan")
    gold_path = Path(gold_path) if gold_path is not None else Path(cfg["paths"]["gold"])
    gold = {}
    for line in gold_path.read_text(encoding="utf-8-sig").splitlines():
        if not line.strip():
            continue
        row = json.loads(line)
        key, label = row["inst_key"], row.get("gold_primary")
        if (key in gold or label not in LABELS or row.get("label_source") != "human_gold"
                or row.get("adjudicated") is not True or row.get("status") == "excluded"):
            raise ValueError("Gold duplicado o no adjudicado")
        gold[key] = label
    if set(gold) != {p["inst_key"] for p in predictions}:
        raise ValueError("Gold y predicciones no contienen exactamente los mismos casos")
    primary = [p for p in predictions if p["replicate"] == 0]
    if len(primary) != len(predictions) or {p["condition"] for p in primary} != CONDITIONS:
        raise ValueError("Se requieren las cuatro condiciones principales sin replicas de estabilidad")
    for cond in CONDITIONS:
        keys = [p["inst_key"] for p in primary if p["condition"] == cond]
        if len(keys) != len(set(keys)) or set(keys) != set(gold):
            raise ValueError("Condicion incompleta o duplicada: " + cond)
    rows = []
    for p in primary:
        if p.get("synthetic") or p["returned_model"] != cfg["model"]:
            raise ValueError("Prediccion sintetica o modelo distinto")
        scores = p.get("scores")
        if p["valid"]:
            if (not isinstance(scores, dict) or set(scores) != set(LABELS)
                    or any(type(v) not in (int, float) or not math.isfinite(v) or not 0 <= v <= 1 for v in scores.values())
                    or abs(sum(scores.values()) - 1) > .001):
                raise ValueError("Puntajes validos inconsistentes")
            chosen = max(LABELS, key=lambda label: scores[label])
            if p["predicted_label"] != chosen:
                raise ValueError("Etiqueta no coincide con puntajes")
        elif p["predicted_label"] != "__invalid__":
            raise ValueError("Respuesta invalida sin marca explicita")
        row = {"inst_key": p["inst_key"], "citing_id": p["citing_id"],
               "model": cfg["model"], "run_id": cfg["run_id"], "condition": p["condition"],
               "reference": gold[p["inst_key"]], "predicted_label": p["predicted_label"],
               "valid": p["valid"], "correct": p["valid"] and p["predicted_label"] == gold[p["inst_key"]],
               "error": p.get("error") or ""}
        row.update({"p_" + label: scores[label] if p["valid"] else "" for label in LABELS})
        rows.append(row)
    rows.sort(key=lambda r: (r["condition"], r["inst_key"]))
    model = re.sub(r"[^a-zA-Z0-9_-]+", "_", cfg["model"])
    output = run_dir / "csv"
    output.mkdir(exist_ok=True)
    groups = [(f"predictions_{model}.csv", rows)] + [
        (f"predictions_{model}_{cond}.csv", [r for r in rows if r["condition"] == cond])
        for cond in sorted(CONDITIONS)]
    files = {}
    for name, records in groups:
        target = output / name
        with target.open("w", newline="", encoding="utf-8-sig") as stream:
            writer = csv.DictWriter(stream, fieldnames=list(rows[0]))
            writer.writeheader()
            writer.writerows(records)
        files[name] = {"rows": len(records), "sha256": sha(target)}
    receipt = {"run_id": cfg["run_id"], "model": cfg["model"], "cases": len(gold),
        "records": len(rows), "invalid": sum(not r["valid"] for r in rows),
        "conditions": dict(Counter(r["condition"] for r in rows)),
        "source_sha256": {n: sha(run_dir / n) for n in ("manifest.json", "predictions.json", "run_summary.json")},
        "gold_sha256": sha(gold_path), "files": files, "api_called": False}
    (output / "export_manifest.json").write_text(json.dumps(receipt, ensure_ascii=False, indent=2)+"\n", encoding="utf-8")
    return {"output_dir": str(output), "cases": len(gold), "records": len(rows),
            "invalid": receipt["invalid"], "csv_files": len(groups), "api_called": False}
