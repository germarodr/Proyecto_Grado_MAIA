"""Se incrusta en el notebook V2: referencias V0 y comparación sin consultar T_B."""
import hashlib
import json
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.metrics import accuracy_score, precision_recall_fscore_support


def reference_digest(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def load_v0_reference(root, evaluation_root, labels):
    root, evaluation_root = Path(root), Path(evaluation_root)
    spec = json.loads((root / "run_manifest.json").read_text(encoding="utf-8"))
    if spec["isolation"] != "V0" or spec["labels"] != labels:
        raise ValueError("La referencia debe ser V0 y usar las mismas nueve categorías.")
    required = [root / "run_manifest.json", root / "split_class_counts.csv",
                evaluation_root / "validation_comparison.csv"]
    summary = pd.read_csv(required[-1])
    if set(summary.config) != {"base", "fragmentos"} or len(summary) != 2:
        raise ValueError("Faltan las dos referencias V0 o hay configuraciones duplicadas.")
    if not summary.precision.eq("fp32").all():
        raise ValueError("La comparación debe usar referencias FP32.")
    for config in ["base", "fragmentos"]:
        prediction_path = evaluation_root / config / "validation_predictions.csv"
        audit_path = evaluation_root / config / "export_precision_audit.json"
        audit = json.loads(audit_path.read_text(encoding="utf-8"))
        if audit["export_check"] != "passed_full_validation":
            raise ValueError(f"La exportación V0 de {config} no pasó la auditoría.")
        if audit["split_hashes"] != spec["split_hashes"]:
            raise ValueError("La evaluación V0 pertenece a otra partición.")
        frame = pd.read_csv(prediction_path)
        validate_prediction_frame(frame, labels)
        if len(frame) != int(summary.loc[summary.config.eq(config), "n"].iloc[0]):
            raise ValueError("El tamaño de las predicciones V0 no coincide con su reporte.")
        required.extend([prediction_path, audit_path])
    provenance = {"run_id": root.name, "evaluation_root": str(evaluation_root),
                  "isolation": "V0", "files_sha256": {str(p): reference_digest(p) for p in required}}
    return spec, provenance


def validate_v2_spec(reference, current):
    if reference["isolation"] != "V0" or current["isolation"] != "V2":
        raise ValueError("Se espera una referencia V0 y una corrida nueva V2.")
    allowed = {"isolation", "split_hashes", "environment"}
    changes = [key for key in sorted(set(reference) | set(current))
               if key not in allowed and reference.get(key) != current.get(key)]
    if changes:
        raise ValueError(f"Además del aislamiento cambiaron datos/hiperparámetros: {changes}")


def validate_prediction_frame(frame, labels):
    required = {"inst_key", "gold_or_prelabel", "label_source", "predicted_label"}
    if not required <= set(frame.columns) or frame.empty:
        raise ValueError("Predicciones vacías o sin claves/etiquetas/procedencia.")
    if frame.inst_key.isna().any() or frame.inst_key.duplicated().any():
        raise ValueError("Claves ausentes o repetidas en las predicciones.")
    if not frame.gold_or_prelabel.isin(labels).all() or not frame.predicted_label.isin(labels).all():
        raise ValueError("Categoría desconocida en las predicciones.")
    if not frame.label_source.eq("pre_label").all():
        raise ValueError("Esta prueba compara únicamente las preetiquetas A2 congeladas.")


def isolation_scores(frame, labels):
    truth, pred = frame.gold_or_prelabel, frame.predicted_label
    metrics = {"n": len(frame), "accuracy": float(accuracy_score(truth, pred))}
    for average in ["macro", "micro"]:
        precision, recall, f1, _ = precision_recall_fscore_support(
            truth, pred, labels=labels, average=average, zero_division=0)
        metrics.update({f"precision_{average}": float(precision), f"recall_{average}": float(recall),
                        f"f1_{average}": float(f1)})
    return metrics


def compare_v0_v2(reference_root, current_root, reference_run, current_run, labels,
                  reference_train_n, current_train_n, output_dir):
    frames, full_rows, common_rows, class_rows = {}, [], [], []
    for isolation, root in [("V0", reference_root), ("V2", current_root)]:
        for config in ["base", "fragmentos"]:
            frame = pd.read_csv(Path(root) / config / "validation_predictions.csv")
            validate_prediction_frame(frame, labels)
            frames[isolation, config] = frame.set_index("inst_key", drop=False)
    reference_keys = set(frames["V0", "base"].index)
    current_keys = set(frames["V2", "base"].index)
    if set(frames["V0", "fragmentos"].index) != reference_keys:
        raise ValueError("Base y Top-3 de V0 no usan la misma validación.")
    if set(frames["V2", "fragmentos"].index) != current_keys:
        raise ValueError("Base y Top-3 de V2 no usan la misma validación.")
    # Mismos archivos y hash por citante: la validación V2 debe ser subconjunto de V0.
    if not current_keys <= reference_keys:
        raise ValueError("V2 contiene claves de validación ajenas a la referencia V0.")
    keys = sorted(current_keys)
    truth = frames["V0", "base"].loc[keys, "gold_or_prelabel"]
    for (isolation, config), frame in frames.items():
        aligned = frame.loc[keys]
        if not np.array_equal(aligned.gold_or_prelabel.to_numpy(), truth.to_numpy()):
            raise ValueError("Las etiquetas no coinciden al alinear por inst_key.")
        identity = {"run_id": reference_run if isolation == "V0" else current_run,
                    "isolation": isolation, "config": config, "precision": "fp32",
                    "train_n": int(reference_train_n if isolation == "V0" else current_train_n)}
        full_rows.append({**identity, "scope": "own_validation", **isolation_scores(frame, labels)})
        common_rows.append({**identity, "scope": "common_validation", **isolation_scores(aligned, labels)})
        precision, recall, f1, support = precision_recall_fscore_support(
            aligned.gold_or_prelabel, aligned.predicted_label, labels=labels, zero_division=0)
        class_rows.extend({**identity, "label": label, "precision_class": float(p),
                           "recall_class": float(r), "f1_class": float(f), "support": int(n)}
                          for label, p, r, f, n in zip(labels, precision, recall, f1, support))
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    full, common, per_class = map(pd.DataFrame, [full_rows, common_rows, class_rows])
    full.to_csv(output_dir / "isolation_own_validation.csv", index=False)
    common.to_csv(output_dir / "isolation_common_validation.csv", index=False)
    per_class.to_csv(output_dir / "isolation_common_per_class.csv", index=False)
    pd.DataFrame({"inst_key": keys}).to_csv(output_dir / "isolation_common_keys.csv", index=False)
    return full, common, per_class
