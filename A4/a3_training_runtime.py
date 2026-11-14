"""Lectura verificada de A3 y entrenamiento v2; se incrusta en el notebook."""
import collections
import hashlib
import json
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.metrics import accuracy_score, precision_recall_fscore_support


def file_hash(path):
    digest = hashlib.sha256()
    with Path(path).open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def read_records(path):
    with Path(path).open(encoding="utf-8-sig") as stream:
        return [json.loads(line) for line in stream if line.strip()]


def keyed_records(rows, name):
    result = {}
    for row in rows:
        key = row["inst_key"]
        if key in result:
            raise ValueError(f"Hay una clave repetida en {name}: {key}")
        citing, para, span, cited = key.split("|")
        if citing != row["citing_paper_id"] or cited != row["cited_paper_id"] or citing == cited:
            raise ValueError(f"La clave no corresponde a sus artículos en {name}: {key}")
        if not row["group_key"].startswith(f"{citing}|{para}|"):
            raise ValueError(f"El grupo de citas no corresponde a la clave en {name}: {key}")
        result[key] = row
    return result


def checked_file(root, name, expected, hashes):
    root = Path(root).resolve()
    path = (root / name).resolve()
    if path.parent != root:
        raise ValueError("El manifiesto contiene una ruta fuera de su carpeta.")
    actual = file_hash(path)
    if actual != expected:
        raise ValueError(f"El archivo cambió respecto de la entrega revisada: {name}")
    hashes[str(path)] = actual
    return path


def load_a3_release(ids_dir, a3_dir, old_ids_dir, labels, training_manifest_hash, metrics_manifest_hash):
    ids_dir, a3_dir, old_ids_dir = map(Path, [ids_dir, a3_dir, old_ids_dir])
    hashes = {}
    manifest_path = checked_file(ids_dir, "manifest_training_v2_G15.json", training_manifest_hash, hashes)
    metrics_path = checked_file(a3_dir, "manifest_metrics.json", metrics_manifest_hash, hashes)
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    metrics = json.loads(metrics_path.read_text(encoding="utf-8"))
    if (manifest["group"], manifest["test_set"], manifest["version"], manifest["variant"]) != ("G15", "B", "v2", "V0"):
        raise ValueError("Esta corrida espera la entrega training v2 de G15, cuyo punto de partida es V0.")
    required = {"training_v2_G15.jsonl", *(f"exclusion_list_G15_{v}_v2.jsonl" for v in ["V0", "V1", "V2"])}
    if not required <= manifest["files"].keys():
        raise ValueError("Faltan archivos de entrenamiento o de exclusión en el manifiesto.")
    for name, digest in manifest["files"].items():
        checked_file(ids_dir, name, digest, hashes)
    gold_path = checked_file(a3_dir, "test_set_gold.jsonl", metrics["files"]["test_set_gold.jsonl"], hashes)
    rows, gold = read_records(ids_dir / "training_v2_G15.jsonl"), read_records(gold_path)
    row_index, gold_index = keyed_records(rows, "training v2"), keyed_records(gold, "gold A3")
    if len(rows) != manifest["v2_rows"] or len(gold) != metrics["packages"]:
        raise ValueError("La cantidad de filas no coincide con los manifiestos.")
    if not all(r["high_confidence"] and r["primary_pre_label"] in labels for r in rows):
        raise ValueError("Hay una fila sin preetiqueta válida de alta confianza.")
    for record in gold:
        if record["set"] not in {"A", "B"} or type(record["in_eval"]) is not bool:
            raise ValueError("Conjunto o marca in_eval inválidos en A3.")
        if record["gold_primary"] not in labels + ["unclear"]:
            raise ValueError("Hay una categoría humana desconocida.")
        if record["in_eval"] != (record["gold_primary"] != "unclear"):
            raise ValueError("La etiqueta humana y su marca de evaluación se contradicen.")
    for group in ["A", "B"]:
        valid = sum(r["set"] == group and r["in_eval"] for r in gold)
        unclear = sum(r["set"] == group and not r["in_eval"] for r in gold)
        if valid != metrics["in_eval"][group] or unclear != metrics["unclear"][group]:
            raise ValueError("El cierre humano no coincide con su manifiesto.")
    own_gold = [g for g in gold if g["set"] == "B"]
    if set(row_index) & {g["inst_key"] for g in own_gold}:
        raise ValueError("Se encontró una cita de T_B dentro del entrenamiento: detener.")
    # Recuperar localizadores, no etiquetas antiguas, para identificar el test de A3.
    old_manifest_path = old_ids_dir / "manifest_training_v1_G15.json"
    old_manifest = json.loads(old_manifest_path.read_text(encoding="utf-8"))
    hashes[str(old_manifest_path)] = file_hash(old_manifest_path)
    for name in ["training_v1_G15.jsonl", "test_set_ids_G15.jsonl"]:
        checked_file(old_ids_dir, name, old_manifest["files"][name], hashes)
    old_rows = read_records(old_ids_dir / "training_v1_G15.jsonl")
    old_index = keyed_records(old_rows, "training v1")
    old_test_index = keyed_records(read_records(old_ids_dir / "test_set_ids_G15.jsonl"), "test IDs v1")
    if not old_index.keys() <= row_index.keys() or len(old_rows) != manifest["v1_rows"]:
        raise ValueError("La entrega v2 no conserva todas las filas de v1.")
    regained = [r for r in rows if r["inst_key"] not in old_index]
    if len(regained) != manifest["rows_regained"] or dict(collections.Counter(r["primary_pre_label"] for r in regained)) != manifest["regained_per_label"]:
        raise ValueError("Las reservas recuperadas no coinciden con el manifiesto.")
    test_ids = []
    for record in own_gold:
        if record["inst_key"] not in old_test_index:
            raise ValueError("Una cita del cierre T_B no está en sus identificadores originales.")
        source = old_test_index[record["inst_key"]]
        test_ids.append({k: source[k] for k in ["inst_key", "group_key", "citing_paper_id", "cited_paper_id", "source_batch"]})
    closure_counts = collections.Counter(r["gold_primary"] for r in own_gold if r["in_eval"])
    expected = {"Background": 330, "Gap": 310, "Basis": 322, "Comparison": 313,
                "Application": 400, "Improvement/Modification": 268, "Evidence": 386,
                "Identification of the Originator": 324, "Further Reading": 315}
    if dict(closure_counts) != expected:
        raise ValueError("Los cupos de T_B difieren del cierre revisado del 9 de noviembre.")
    closure = {"date": "2026-11-09", "valid_test_rows": metrics["in_eval"]["B"],
               "unclear_test_rows": metrics["unclear"]["B"], "valid_test_counts": dict(closure_counts),
               "quota_note": "Cierre sin ola 4: Improvement/Modification tiene 268 casos válidos, según iaa_report.",
               "test_scored": False, "dataset_release": "training_v2", "regained_rows": len(regained)}
    return manifest, rows, gold, test_ids, hashes, closure


def release_rules(rows):
    rules = {"citing": set(), "cited": set()}
    for row in rows:
        if row["group"] != "G15" or row["role"] not in rules:
            raise ValueError("La lista de exclusión no corresponde a G15 o tiene un rol desconocido.")
        rules[row["role"]].add(row["paper_id"])
    return rules


def release_excluded(row, rules):
    return row["citing_paper_id"] in rules["citing"] or row["cited_paper_id"] in rules["cited"]


def attach_ta_gold(rows, gold, labels):
    index = keyed_records(gold, "gold A3")
    labeled, dropped, corrected = [], [], 0
    for row in rows:
        human = index.get(row["inst_key"])
        if human is not None and human["set"] != "A":
            raise ValueError("Solo se permite incorporar etiquetas humanas de T_A al entrenamiento.")
        if human is not None and not human["in_eval"]:
            dropped.append(row["inst_key"])
            continue
        label = human["gold_primary"] if human else row["primary_pre_label"]
        if label not in labels:
            raise ValueError("Hay una etiqueta de entrenamiento desconocida.")
        corrected += bool(human and label != row["primary_pre_label"])
        labeled.append({**row, "label": label, "label_source": "human_gold" if human else "pre_label",
                        "gold_set": "A" if human else None})
    return labeled, dropped, corrected


def document_set(rows):
    return {r[key] for r in rows for key in ["citing_paper_id", "cited_paper_id"]}


def audit_release_splits(train, validation, test_ids):
    pairs = [("train", train), ("validation", validation), ("test_reserved", test_ids)]
    for i, (name, rows) in enumerate(pairs):
        for other_name, other in pairs[i + 1:]:
            if document_set(rows) & document_set(other):
                raise ValueError(f"Hay documentos compartidos entre {name} y {other_name}.")


def plot_release_eda(train, validation, labels, output_root):
    import matplotlib.pyplot as plt
    root = Path(output_root)
    frame = pd.DataFrame({"entrenamiento": collections.Counter(r["label"] for r in train),
                          "validacion": collections.Counter(r["label"] for r in validation)}).reindex(labels).fillna(0).astype(int)
    frame["total"] = frame.sum(axis=1)
    frame.index.name = "label"
    frame.to_csv(root / "eda_class_distribution.csv")
    totals = frame.total
    fig, (pie, bars) = plt.subplots(1, 2, figsize=(17, 6))
    wedges, _, _ = pie.pie(totals, startangle=90, colors=plt.get_cmap("tab10")(np.arange(len(labels))),
        autopct=lambda p: f"{p:.1f}%" if p >= 3 else "", pctdistance=.78,
        wedgeprops={"width": .42, "edgecolor": "white"})
    pie.text(0, 0, f"{int(totals.sum()):,}\nejemplos", ha="center", va="center", fontsize=15)
    pie.set_title("Las clases en los datos que sí usaremos")
    pie.legend(wedges, [f"{label}: {n:,} ({n / totals.sum():.1%})" for label, n in totals.items()],
               loc="upper center", bbox_to_anchor=(.5, -.02), fontsize=8, ncol=2)
    frame[["entrenamiento", "validacion"]].plot.barh(ax=bars, color=["#16877c", "#8fa6be"])
    bars.invert_yaxis()
    for container in bars.containers:
        bars.bar_label(container, fmt="%.0f", padding=3, fontsize=8)
    bars.set(xlabel="Número de ejemplos", ylabel="", title="Cómo quedan repartidas las clases")
    bars.set_xlim(0, int(frame.entrenamiento.max()) * 1.22)
    fig.suptitle("G15 · datos v2 · aislamiento V2 · etiquetas A2 y correcciones humanas de T_A")
    fig.tight_layout()
    fig.savefig(root / "eda_class_distribution.png", dpi=160, bbox_inches="tight")
    plt.show()
    plt.close(fig)
    print(f"1. Usaremos {len(train):,} ejemplos para aprender y {len(validation):,} para validar; T_B queda aparte.")
    print(f"2. La clase más frecuente es {totals.idxmax()} ({totals.max() / totals.sum():.1%}); "
          f"la más escasa es {totals.idxmin()} ({int(totals.min()):,} ejemplos entre ambos conjuntos).")
    return frame


def compare_release_validation(reference_root, current_root, labels, output_root, reference_run, current_run):
    frames = {}
    for release, root in [("v1_prelabels", reference_root), ("v2_goldTA", current_root)]:
        for config in ["base", "fragmentos"]:
            frame = pd.read_csv(Path(root) / config / "validation_predictions.csv")
            if frame.empty or frame.inst_key.isna().any() or frame.inst_key.duplicated().any():
                raise ValueError("La comparación contiene claves ausentes/repetidas o predicciones vacías.")
            if not frame.predicted_label.isin(labels).all() or not frame.gold_or_prelabel.isin(labels).all():
                raise ValueError("Hay una categoría desconocida en la comparación.")
            frames[release, config] = frame.set_index("inst_key", drop=False)
    for release in ["v1_prelabels", "v2_goldTA"]:
        if set(frames[release, "base"].index) != set(frames[release, "fragmentos"].index):
            raise ValueError("Las dos entradas de una entrega no usan la misma validación.")
    keys = sorted(set(frames["v1_prelabels", "base"].index) & set(frames["v2_goldTA", "base"].index))
    if not keys:
        raise ValueError("No hay citas de validación comunes para comparar las entregas.")
    current = frames["v2_goldTA", "base"].loc[keys]
    truth = current.gold_or_prelabel.to_numpy()
    if not np.array_equal(truth, frames["v2_goldTA", "fragmentos"].loc[keys].gold_or_prelabel.to_numpy()):
        raise ValueError("Las etiquetas actuales difieren entre base y Top-3.")
    changed = sum(frames["v1_prelabels", "base"].loc[keys].gold_or_prelabel.to_numpy() != truth)
    result, classes = [], []
    for (release, config), frame in frames.items():
        pred = frame.loc[keys].predicted_label.to_numpy()
        row = {"release": release, "config": config, "n": len(keys), "precision": "fp32",
               "reference_labels_changed": int(changed), "accuracy": float(accuracy_score(truth, pred))}
        for average in ["macro", "micro"]:
            p, r, f, _ = precision_recall_fscore_support(truth, pred, labels=labels, average=average, zero_division=0)
            row.update({f"precision_{average}": float(p), f"recall_{average}": float(r), f"f1_{average}": float(f)})
        result.append(row)
        p, r, f, n = precision_recall_fscore_support(truth, pred, labels=labels, zero_division=0)
        classes.extend({"release": release, "config": config, "label": label, "precision_class": float(a),
                        "recall_class": float(b), "f1_class": float(c), "support": int(d)}
                       for label, a, b, c, d in zip(labels, p, r, f, n))
    output_root = Path(output_root)
    output_root.mkdir(parents=True, exist_ok=True)
    table = pd.DataFrame(result)
    table.to_csv(output_root / "release_common_validation.csv", index=False)
    pd.DataFrame(classes).to_csv(output_root / "release_common_per_class.csv", index=False)
    pd.DataFrame({"inst_key": keys}).to_csv(output_root / "release_common_keys.csv", index=False)
    note = {"reference_run": reference_run, "current_run": current_run, "n": len(keys),
            "labels_policy": "current_v2_labels_for_both_releases", "corrected_reference_labels": int(changed),
            "test_used": False, "interpretation": "Cambian datos y etiquetas; ambas corridas usan aislamiento V2."}
    (output_root / "release_comparison_notes.json").write_text(json.dumps(note, indent=2) + "\n", encoding="utf-8")
    return table
