"""Comparaciones de reparto de texto y entropía cruzada para las dos entradas de A4."""
import collections
import json
import math
from pathlib import Path

import numpy as np
import pandas as pd
import torch
from transformers import Trainer


def experiment_conditions(kind):
    if kind == "reparto":
        return [{"condition": f"contexto_{n}", "context_budget": n, "loss_mode": "sin_pesos"}
                for n in [192, 128, 256]]
    if kind == "pesos":
        return [{"condition": mode, "context_budget": 192, "loss_mode": mode}
                for mode in ["sin_pesos", "raiz_inversa", "inversa_limitada"]]
    raise ValueError("El experimento debe estudiar reparto o pesos de clase.")


def class_weight_profiles(train_rows, labels):
    """Solo recibe entrenamiento: ni validación ni test intervienen en los pesos."""
    frequency = collections.Counter(r["label"] for r in train_rows)
    if set(frequency) != set(labels) or len(set(labels)) != len(labels):
        raise ValueError("Cada clase debe tener ejemplos de entrenamiento.")
    counts = np.asarray([frequency[label] for label in labels], dtype=np.float64)
    balanced = counts.sum() / (len(labels) * counts)
    raw = {"sin_pesos": np.ones(len(labels)), "raiz_inversa": np.sqrt(balanced),
           "inversa_limitada": np.clip(balanced, .25, 4.)}
    # La media ponderada de los pesos sobre entrenamiento es uno.
    profiles = {name: (values / np.average(values, weights=counts)).tolist()
                for name, values in raw.items()}
    return profiles, pd.DataFrame({"label": labels, "train_count": counts.astype(int), **profiles})


class ClassWeightedTrainer(Trainer):
    def __init__(self, *args, class_weights, **kwargs):
        super().__init__(*args, **kwargs)
        self.class_weights = torch.tensor(class_weights, dtype=torch.float32)
        # Nuestra pérdida ya es una media; Trainer gestiona la acumulación de gradientes.
        self.model_accepts_loss_kwargs = False

    def compute_loss(self, model, inputs, return_outputs=False, num_items_in_batch=None):
        labels = inputs["labels"]
        outputs = model(**{k: v for k, v in inputs.items() if k != "labels"})
        logits = outputs.logits.float()
        loss = torch.nn.functional.cross_entropy(logits, labels,
            weight=self.class_weights.to(logits.device))
        return (loss, outputs) if return_outputs else loss


def experiment_trial_id(spec):
    def number(value):
        return format(float(value), ".8g").replace("-", "m").replace(".", "p").replace("+", "")
    return (f"{spec['stage']}_{spec['input_variant']}_{spec['condition']}_"
            f"lr{number(spec['learning_rate'])}_wd{number(spec['weight_decay'])}_s{spec['seed']}")


def control_grid(kind, learning_rates, weight_decays, seed, max_epochs):
    import itertools
    control = experiment_conditions(kind)[0]
    plan = [{"stage": "grid", "input_variant": config, **control, "learning_rate": float(lr),
             "weight_decay": float(wd), "seed": int(seed), "max_epochs": int(max_epochs)}
            for config, lr, wd in itertools.product(["base", "fragmentos"], learning_rates, weight_decays)]
    if not plan or len({experiment_trial_id(s) for s in plan}) != len(plan):
        raise ValueError("La búsqueda debe tener combinaciones distintas.")
    if any(s["learning_rate"] <= 0 or s["weight_decay"] < 0 or s["max_epochs"] < 1 for s in plan):
        raise ValueError("Los parámetros no son válidos.")
    return plan


def check_experiment_results(results, plan):
    expected = {experiment_trial_id(s): s for s in plan}
    if len(expected) != len(plan) or len(results) != len(plan):
        raise ValueError("Faltan resultados o hay ensayos repetidos.")
    if {r["trial_id"] for r in results} != set(expected):
        raise ValueError("Los resultados no cubren exactamente el plan.")
    for result in results:
        spec = expected[result["trial_id"]]
        if any(result.get(k) != v for k, v in spec.items()):
            raise ValueError("Un resultado no corresponde a sus parámetros.")
        if result.get("evaluation_policy") != "v2_fp32" or not math.isfinite(result["f1_macro"]):
            raise ValueError("La comparación requiere resultados FP32 completos.")


def select_control_anchors(results, plan):
    check_experiment_results(results, plan)
    return {config: min((r for r in results if r["input_variant"] == config),
                       key=lambda r: (-r["f1_macro"], r["learning_rate"], r["weight_decay"], r["trial_id"]))
            for config in ["base", "fragmentos"]}


def comparison_plan(kind, anchors, seeds, primary_seed=42):
    if len(seeds) != 3 or len(set(seeds)) != 3 or primary_seed not in seeds:
        raise ValueError("Se requieren tres semillas únicas, incluida la principal.")
    conditions = experiment_conditions(kind)
    fields = ["stage", "input_variant", "condition", "context_budget", "loss_mode", "learning_rate",
              "weight_decay", "seed", "max_epochs"]
    plan = []
    for config in ["base", "fragmentos"]:
        anchor = anchors[config]
        if anchor["condition"] != conditions[0]["condition"] or anchor["seed"] != primary_seed:
            raise ValueError("El control debe ser el seleccionado con la semilla principal.")
        for condition in conditions:
            for seed in seeds:
                if condition == conditions[0] and seed == primary_seed:
                    plan.append({k: anchor[k] for k in fields})
                else:
                    plan.append({"stage": "comparacion", "input_variant": config, **condition,
                                 "learning_rate": anchor["learning_rate"], "weight_decay": anchor["weight_decay"],
                                 "seed": int(seed), "max_epochs": anchor["max_epochs"]})
    return plan


def summarize_conditions(results, plan, kind):
    check_experiment_results(results, plan)
    frame = pd.DataFrame(results)
    control = experiment_conditions(kind)[0]["condition"]
    summaries, pairs, selected = [], [], {}
    for config in ["base", "fragmentos"]:
        subset = frame.loc[frame.input_variant == config]
        controls = subset.loc[subset.condition == control].set_index("seed")
        for condition in experiment_conditions(kind):
            rows = subset.loc[subset.condition == condition["condition"]].set_index("seed")
            if (len(rows) != 3 or rows.index.has_duplicates or set(rows.index) != set(controls.index)
                    or any(len(subset[k].unique()) != 1 for k in ["learning_rate", "weight_decay", "max_epochs"])):
                raise ValueError("La comparación debe conservar parámetros y emparejar las tres semillas.")
            for seed, row in rows.iterrows():
                pairs.append({"input_variant": config, "condition": condition["condition"], "seed": int(seed),
                    "control_trial_id": controls.loc[seed, "trial_id"], "trial_id": row.trial_id,
                    "control_f1_macro": controls.loc[seed, "f1_macro"], "f1_macro": row.f1_macro,
                    "delta_pp": 100 * (row.f1_macro - controls.loc[seed, "f1_macro"])})
            summaries.append({"input_variant": config, **condition, "n": 3,
                "mean_f1": float(rows.f1_macro.mean()), "std_f1": float(rows.f1_macro.std(ddof=1)),
                "mean_delta_pp": float(100 * (rows.f1_macro - controls.f1_macro).mean()),
                "wins_over_control": int((rows.f1_macro > controls.f1_macro).sum())})
        # Preferimos el control si la media empata; no escogemos la mejor semilla.
        winner = min((r for r in summaries if r["input_variant"] == config),
                     key=lambda r: (-r["mean_f1"], r["condition"] != control, r["condition"]))
        selected[config] = next(r for r in results if r["input_variant"] == config
                               and r["condition"] == winner["condition"] and r["seed"] == 42)
    return pd.DataFrame(summaries), pd.DataFrame(pairs), selected


def acquire_experiment_writer(root):
    import fcntl
    import os
    root = Path(root)
    root.mkdir(parents=True, exist_ok=True)
    locks = globals().setdefault("_EXPERIMENT_WRITER_LOCKS", {})
    key = str(root.resolve())
    if key in locks and not locks[key].closed:
        return locks[key]
    handle = (root / "writer.lock").open("a+")
    try:
        fcntl.flock(handle, fcntl.LOCK_EX | fcntl.LOCK_NB)
    except BlockingIOError:
        handle.close()
        raise RuntimeError("Otra sesión está escribiendo este experimento. Recupera esa sesión antes de continuar.")
    handle.seek(0)
    handle.truncate()
    handle.write(str(os.getpid()))
    handle.flush()
    locks[key] = handle
    return handle


def release_experiment_writer(root):
    import fcntl
    handle = globals().get("_EXPERIMENT_WRITER_LOCKS", {}).pop(str(Path(root).resolve()), None)
    if handle is not None and not handle.closed:
        fcntl.flock(handle, fcntl.LOCK_UN)
        handle.close()


def run_experiment_plan(plan, filename):
    global CONTEXT_BUDGET, encoded
    results = []
    for number, trial in enumerate(plan, 1):
        CONTEXT_BUDGET = trial["context_budget"]
        encoded = encoded_by_budget[CONTEXT_BUDGET]
        print(f"Ensayo {number}/{len(plan)}: {trial_id(trial)}")
        results.append(run_final_trial(trial))
        pd.DataFrame(results).to_csv(OUTPUT_ROOT / filename, index=False)
    check_experiment_results(results, plan)
    tracking.backup(force=True)
    return results


def review_experiment_outputs(results, plan, output, val_rows, split_hashes, labels):
    """Reconstruye las métricas a partir de los CSV sin volver a inferir."""
    from sklearn.metrics import accuracy_score, classification_report, precision_recall_fscore_support
    check_experiment_results(results, plan)
    output = Path(output)
    reference = {r["inst_key"]: r for r in val_rows}
    if len(reference) != len(val_rows):
        raise ValueError("La validación tiene identificadores repetidos.")
    proofs = []
    for result in results:
        work = output / "trials" / result["trial_id"]
        training = json.loads((work / "TRAINING_COMPLETE.json").read_text())
        evaluation = json.loads((work / "EVALUATION_COMPLETE.json").read_text())
        verify_files(work / "model", training["model_hashes"])
        verify_files(work / "evaluation", evaluation["files"])
        if result["model_marker_sha256"] != sha256(work / "TRAINING_COMPLETE.json"):
            raise ValueError("La evaluación apunta a otro cierre de modelo.")
        audit = json.loads((work / "evaluation/export_precision_audit.json").read_text())
        if audit["export_check"] != "passed_full_validation" or audit["split_hashes"] != split_hashes:
            raise ValueError("La exportación o la partición no coincide con esta comparación.")
        predictions = pd.read_csv(work / "evaluation/predictions.csv")
        if (len(predictions) != len(reference) or predictions.inst_key.duplicated().any()
                or set(predictions.inst_key) != set(reference)):
            raise ValueError("Las predicciones no cubren exactamente la validación.")
        if any(row.reference != reference[row.inst_key]["label"]
               or row.label_source != reference[row.inst_key]["label_source"]
               for row in predictions.itertuples()):
            raise ValueError("Las referencias o su procedencia cambiaron.")
        probabilities = predictions[["p_" + label for label in labels]].to_numpy(float)
        if (not np.isfinite(probabilities).all() or (probabilities < 0).any() or (probabilities > 1).any()
                or not np.allclose(probabilities.sum(axis=1), 1, atol=1e-5)):
            raise ValueError("Las probabilidades no son válidas.")
        expected = np.asarray(labels)[probabilities.argmax(axis=1)]
        if not np.array_equal(expected, predictions.predicted_label.to_numpy()):
            raise ValueError("Las etiquetas predichas no corresponden a sus probabilidades.")
        measured = {"accuracy": accuracy_score(predictions.reference, expected)}
        for average in ["macro", "micro"]:
            precision, recall, f1, _ = precision_recall_fscore_support(predictions.reference, expected,
                labels=labels, average=average, zero_division=0)
            measured.update({f"precision_{average}": precision, f"recall_{average}": recall, f"f1_{average}": f1})
        if any(not math.isclose(float(result[k]), float(v), abs_tol=1e-10) for k, v in measured.items()):
            raise ValueError("Las métricas no se reproducen desde las predicciones guardadas.")
        report = json.loads((work / "evaluation/classification_report.json").read_text())
        actual = classification_report(predictions.reference, expected, labels=labels, output_dict=True, zero_division=0)
        if any(not math.isclose(float(report[label][k]), float(actual[label][k]), abs_tol=1e-10)
               for label in labels for k in ["precision", "recall", "f1-score", "support"]):
            raise ValueError("El reporte por clase no coincide con las predicciones.")
        proofs.append({"trial_id": result["trial_id"], "n": len(predictions), "metrics": measured,
                       "predictions_sha256": sha256(work / "evaluation/predictions.csv")})
    return {"passed": True, "test_scored": False, "split_hashes": split_hashes,
            "reviewed_trials": len(proofs), "reviewed_prediction_rows": sum(r["n"] for r in proofs), "trials": proofs}


def experiment_conclusions(kind, summary, selected, counts, token_audit, reports, sources, control_reports=None):
    title = "reparto del texto" if kind == "reparto" else "pesos por clase"
    selections = []
    for config, label in [("base", "base"), ("fragmentos", "Top-3")]:
        result = selected[config]
        row = summary.loc[(summary.input_variant == config) & (summary.condition == result["condition"])].iloc[0]
        selections.append(f"{label}: **{result['condition']}**, F1 macro medio **{row.mean_f1:.4f} ± {row.std_f1:.4f}**, "
                          f"diferencia frente al control **{row.mean_delta_pp:+.2f} puntos porcentuales** "
                          f"y mejora en **{int(row.wins_over_control)}/3** semillas")
    first = (f"Comparamos el {title} con {int(counts.train.sum()):,} ejemplos de entrenamiento y "
             f"{int(counts.validation.sum()):,} de validación. Tras ajustar los controles, conservamos sus parámetros "
             "al cambiar una sola condición y repetimos con tres semillas. " + "; ".join(selections) +
             ". La selección usa la media; el modelo guardado conserva la semilla 42.")
    if kind == "reparto":
        readings = []
        for config, label in [("base", "base"), ("fragmentos", "Top-3")]:
            budget = selected[config]["context_budget"]
            rows = token_audit.loc[(token_audit.config == config) & (token_audit.split == "validation")
                                   & (token_audit.context_budget == budget)]
            readings.append(f"{label}, contexto de hasta {budget} tokens: recorte del citado en "
                            f"{100 * rows.evidence_truncated.mean():.2f}% y fracción media de su texto conservada "
                            f"{100 * (rows.evidence_kept / rows.evidence_original.clip(lower=1)).mean():.2f}%")
        second = "La revisión del texto que llegó al modelo mostró: " + "; ".join(readings) + ". Top-3 conserva aportes de los tres fragmentos y sus secciones; menos recorte, por sí solo, no demuestra mayor calidad."
    else:
        im = "Improvement/Modification"
        findings = []
        for config, label in [("base", "base"), ("fragmentos", "Top-3")]:
            report = reports[config][im]
            finding = (f"{label}: precisión {report['precision']:.4f}, recall {report['recall']:.4f} "
                       f"y F1 {report['f1-score']:.4f}")
            if control_reports is not None:
                original = control_reports[config][im]
                finding += (f" (control: precisión {original['precision']:.4f}, recall {original['recall']:.4f} "
                            f"y F1 {original['f1-score']:.4f})")
            findings.append(finding)
        second = (f"Improvement/Modification tuvo {int(counts.loc[im, 'train'])} ejemplos para entrenar y "
                  f"{int(counts.loc[im, 'validation'])} para validar. En los modelos principales seleccionados, " +
                  "; ".join(findings) + ". Los pesos se calcularon únicamente con entrenamiento; este soporte reducido limita la interpretación de los cambios.")
    human = int(sources.loc["human_gold", "validation"]) if "human_gold" in sources.index else 0
    automatic = int(sources.loc["pre_label", "validation"]) if "pre_label" in sources.index else 0
    third = (f"Todas las cifras corresponden a validación interna: {human:,} etiquetas humanas y "
             f"{automatic:,} automáticas. Verificamos las predicciones, las métricas por clase y los archivos "
             "de los modelos. La variación entre semillas describe estas pruebas; no es un intervalo de confianza. "
             "El test humano permanece separado del entrenamiento y de la selección de parámetros.")
    return "\n\n".join([first, second, third]) + "\n"
