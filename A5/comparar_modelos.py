"""Compara CSV finales sobre el mismo T_B sin entrenamiento ni llamadas API."""
from pathlib import Path
from collections import Counter
import csv
import hashlib
import json
import numpy as np
import a5_runtime as runtime

ROOT = Path(__file__).resolve().parent
LABELS = runtime.LABELS
CONDITIONS = {"base-generic-zero", "base-generic-few", "base-specific-zero", "base-specific-few"}


def read_csv(path):
    with Path(path).open(encoding="utf-8-sig", newline="") as stream:
        return list(csv.DictReader(stream))


def write_csv(path, rows):
    with Path(path).open("w", encoding="utf-8-sig", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=list(rows[0]))
        writer.writeheader(); writer.writerows(rows)


def macro_from_matrices(matrix):
    tp = np.diagonal(matrix[..., :9], axis1=-2, axis2=-1)
    denominator = matrix.sum(axis=-1) + matrix[..., :9].sum(axis=-2)
    return np.divide(2*tp, denominator, out=np.zeros_like(tp, dtype=float), where=denominator != 0).mean(axis=-1)


def check_commercial(rows, baseline):
    if len(rows) != 4*len(baseline) or {r["condition"] for r in rows} != CONDITIONS:
        raise ValueError("Se requieren cuatro condiciones completas")
    grouped = {}
    for cond in sorted(CONDITIONS):
        subset = [r for r in rows if r["condition"] == cond]
        lookup = {r["inst_key"]: r for r in subset}
        if len(lookup) != len(subset) or set(lookup) != set(baseline):
            raise ValueError("Casos duplicados, faltantes o diferentes: " + cond)
        for key, row in lookup.items():
            base = baseline[key]
            if row["reference"] != base["reference"] or row["citing_id"] != base["citing_paper_id"]:
                raise ValueError("Diferencia de gold o articulo citante: " + key)
            if row["valid"] not in ("True", "False"):
                raise ValueError("Validez no reconocida")
            valid = row["valid"] == "True"
            if (valid and row["predicted_label"] not in LABELS) or (not valid and row["predicted_label"] != "__invalid__"):
                raise ValueError("Etiqueta y validez inconsistentes")
            scores = [row["p_"+label] for label in LABELS]
            if valid:
                values = np.array([float(v) for v in scores])
                if not np.isfinite(values).all() or (values < 0).any() or (values > 1).any() or abs(values.sum()-1) > .001:
                    raise ValueError("Puntajes inconsistentes")
                if LABELS[int(values.argmax())] != row["predicted_label"]:
                    raise ValueError("Etiqueta no coincide con puntajes")
        grouped[cond] = lookup
    return grouped


def compare(folder=None, repetitions=2000, seed=20261113):
    folder = Path(folder) if folder else ROOT / "Comparacion_SciBERT"
    source = folder / "base"
    baseline_rows = read_csv(source / "test_predictions.csv")
    baseline = {r["inst_key"]: r for r in baseline_rows}
    if len(baseline) != 2968 or len(baseline_rows) != 2968 or {r["config"] for r in baseline_rows} != {"base"}:
        raise ValueError("Referencia SciBERT base debe contener 2968 casos unicos")
    closure = json.loads((source / "FINAL_COMPLETE.json").read_text(encoding="utf-8"))
    for name in ("test_predictions.csv", "PREDICTIONS_COMPLETE.json", "test_classification_report.json", "evaluation_protocol.json", "data_audit.json", "test_instances.csv"):
        key = "base/"+name if name in ("test_predictions.csv", "PREDICTIONS_COMPLETE.json", "test_classification_report.json") else name
        if runtime.file_hash(source / name) != closure["report_hashes"][key]:
            raise ValueError("Archivo SciBERT modificado: " + name)
    instances = read_csv(source / "test_instances.csv")
    refs = {r["inst_key"]: r["reference"] for r in instances}
    if set(refs) != set(baseline) or any(r["reference"] != refs[r["inst_key"]] or r["pred_label"] not in LABELS for r in baseline_rows):
        raise ValueError("Referencia SciBERT inconsistente")
    keys = sorted(baseline)
    gold = [refs[k] for k in keys]
    groups = sorted({baseline[k]["citing_paper_id"] for k in keys})
    group_index = {k: i for i, k in enumerate(groups)}
    label_index = {k: i for i, k in enumerate(LABELS + ["__invalid__"])}
    expected = {"predictions_gpt-6-luna.csv": "gpt-6-luna",
                "predictions_gemini-3_5-flash-lite.csv": "gemini-3.5-flash-lite"}
    models = [("SciBERT base", "base", [baseline[k]["pred_label"] for k in keys], None)]
    file_hashes = {"base/"+p.name: runtime.file_hash(p) for p in source.iterdir() if p.is_file()}
    runs = {}
    for name, model in expected.items():
        path = folder / "comerciales" / name
        rows = read_csv(path)
        if {r["model"] for r in rows} != {model} or len({r["run_id"] for r in rows}) != 1:
            raise ValueError("CSV de otro modelo o ejecuciones mezcladas")
        runs[model] = rows[0]["run_id"]
        checked = check_commercial(rows, baseline)
        file_hashes["comerciales/"+name] = runtime.file_hash(path)
        for condition, lookup in checked.items():
            models.append((model, condition, [lookup[k]["predicted_label"] for k in keys], lookup))
    rng = np.random.default_rng(seed)
    weights = rng.multinomial(len(groups), np.full(len(groups), 1/len(groups)), size=repetitions)
    bootstraps, metrics, summaries, per_class, disagreements = [], [], [], [], []
    for model, condition, predicted, lookup in models:
        matrix = np.zeros((len(groups), 9, 10), dtype=float)
        for key, ref, pred in zip(keys, gold, predicted):
            matrix[group_index[baseline[key]["citing_paper_id"]], label_index[ref], label_index[pred]] += 1
        sampled = (weights @ matrix.reshape(len(groups), -1)).reshape(repetitions, 9, 10)
        bootstrap = macro_from_matrices(sampled)
        bootstraps.append(bootstrap)
        value = runtime.classification_metrics(gold, predicted)
        if not np.isclose(macro_from_matrices(matrix.sum(axis=0)), value["f1_macro"]):
            raise ValueError("Las implementaciones de F1 no coinciden")
        invalid = predicted.count("__invalid__")
        summary = {"model": model, "condition": condition, "n": len(keys),
            "f1_macro": value["f1_macro"], "f1_micro": value["f1_micro"],
            "coverage": 1-invalid/len(keys), "invalid": invalid,
            "delta_macro_vs_scibert": value["f1_macro"] - metrics[0]["f1_macro"] if metrics else 0.0}
        if lookup is not None:
            delta = bootstrap - bootstraps[0]
            ci = np.quantile(delta, [.025, .975])
            summary.update(delta_ci95_low=float(ci[0]), delta_ci95_high=float(ci[1]),
                           paired_difference_excludes_zero=bool(ci[0] > 0 or ci[1] < 0))
            for key, pred, ref in zip(keys, predicted, gold):
                base_pred = baseline[key]["pred_label"]
                if pred != base_pred:
                    disagreements.append({"model": model, "condition": condition, "inst_key": key,
                        "reference": ref, "scibert_prediction": base_pred, "commercial_prediction": pred,
                        "scibert_correct": base_pred == ref, "commercial_correct": pred == ref})
        else:
            summary.update(delta_ci95_low=0.0, delta_ci95_high=0.0, paired_difference_excludes_zero=False)
        summaries.append(summary)
        metrics.append({"model": model, "condition": condition, **value})
        for label, scores in value["per_class"].items():
            per_class.append({"model": model, "condition": condition, "label": label, **scores})
    scibert_report = json.loads((source / "test_classification_report.json").read_text())
    if not np.isclose(metrics[0]["f1_macro"], scibert_report["macro avg"]["f1-score"]):
        raise ValueError("Metricas SciBERT distintas del reporte original")
    output = folder / "resultados"
    output.mkdir(exist_ok=True)
    write_csv(output / "comparacion_metricas.csv", summaries)
    write_csv(output / "comparacion_por_categoria.csv", per_class)
    write_csv(output / "desacuerdos_por_caso.csv", disagreements)
    write_csv(output / "scibert_base_compatible.csv", [{"inst_key": k, "reference": refs[k], "predicted_label": baseline[k]["pred_label"]} for k in keys])
    report = {"n": len(keys), "same_ids_and_human_references": True, "scientific_metrics": metrics,
        "comparison": summaries, "source_run_scibert": closure["run_id"], "commercial_runs": runs,
        "source_sha256": file_hashes,
        "bootstrap": {"repetitions": repetitions, "seed": seed, "unit": "citing_paper_id",
            "groups": len(groups), "paired": True, "interval": "percentile_95",
            "multiple_comparisons_adjusted": False}, "api_called": False}
    runtime.write_json(output / "comparacion_completa.json", report)
    lines = ["# Comparacion final: SciBERT base, Luna y Gemini", "",
        "Los tres modelos se evaluan sobre los mismos 2968 casos y las mismas etiquetas humanas.",
        "Las respuestas invalidas se conservan como errores. F1 micro coincide con accuracy.", "",
        "| Modelo | Condicion | F1 macro | F1 micro | Delta macro vs SciBERT | IC 95% del delta |",
        "|---|---|---:|---:|---:|---|"]
    for r in summaries:
        ci = "Referencia" if r["model"] == "SciBERT base" else f"[{r['delta_ci95_low']:.4f}, {r['delta_ci95_high']:.4f}]"
        lines.append(f"| {r['model']} | {r['condition']} | {r['f1_macro']:.4f} | {r['f1_micro']:.4f} | {r['delta_macro_vs_scibert']:+.4f} | {ci} |")
    lines += ["", "## Interpretacion", "",
        "SciBERT base obtiene F1 macro 0,7967; Luna especifico con ejemplos obtiene 0,7953.",
        "La diferencia descriptiva es pequena; revisar el intervalo pareado antes de atribuir superioridad.",
        "No se seleccionan ni modifican prompts con los resultados de T_B.", "",
        "## Metodo y alcance", "",
        f"Bootstrap pareado con {repetitions} repeticiones, semilla {seed}, agrupado por articulo citante.",
        "Mismas muestras bootstrap para todos los modelos. Intervalos percentiles bilaterales del 95%.",
        "Comparaciones exploratorias sin ajuste por multiplicidad; no representan una prueba de equivalencia.",
        "Se comparan etiquetas finales; esta verificacion no certifica identidad byte a byte del texto de entrada.",
        "Los costos API y las latencias por lote de SciBERT no se usan para afirmar una ventaja directa de eficiencia.",
        "No hubo entrenamiento ni nuevas inferencias. Originales conservados y hashes incluidos en el JSON."]
    (output / "Comparacion_Final.md").write_text("\n".join(lines)+"\n", encoding="utf-8")
    return {"output_dir": str(output), "cases": len(keys), "conditions_including_scibert": len(summaries),
            "same_ids_and_references": True, "api_called": False}


if __name__ == "__main__":
    print(compare())
