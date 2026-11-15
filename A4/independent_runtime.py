"""Controles de A4 independiente: etiquetas A2 y exclusión de todo documento de T_A."""
import collections
import hashlib
import json
from pathlib import Path

import numpy as np
import pandas as pd
from a3_training_runtime import (checked_file, document_set, file_hash, keyed_records,
                                 read_records, release_excluded, release_rules)


def load_independent_release(ids_dir, a3_dir, old_ids_dir, exclusion_file, labels,
                             training_hash, metrics_hash, exclusion_hash):
    ids_dir, a3_dir, old_ids_dir = map(Path, [ids_dir, a3_dir, old_ids_dir])
    exclusion_file = Path(exclusion_file)
    hashes = {}
    manifest_path = checked_file(ids_dir, "manifest_training_v2_G15.json", training_hash, hashes)
    metrics_path = checked_file(a3_dir, "manifest_metrics.json", metrics_hash, hashes)
    checked_file(exclusion_file.parent, exclusion_file.name, exclusion_hash, hashes)
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    metrics = json.loads(metrics_path.read_text(encoding="utf-8"))
    exclusion = json.loads(exclusion_file.read_text(encoding="utf-8"))
    if (manifest["group"], manifest["test_set"], manifest["version"], manifest["variant"]) != ("G15", "B", "v2", "V0"):
        raise ValueError("La entrega no corresponde a training v2 de G15.")
    for filename, digest in manifest["files"].items():
        checked_file(ids_dir, filename, digest, hashes)
    rows = read_records(ids_dir / "training_v2_G15.jsonl")
    keyed_records(rows, "training v2 G15")
    if len(rows) != manifest["v2_rows"]:
        raise ValueError("El tamaño de la entrega no coincide con su manifiesto.")
    if not all(r["high_confidence"] and r["primary_pre_label"] in labels and r["label_source"] == "pre_label" for r in rows):
        raise ValueError("Esta corrida solo acepta las preetiquetas originales de A2.")
    if exclusion["purpose"] != "exclude_TA_documents_from_G15_training_and_validation" or exclusion["scope"] != "all_sampled_packages_including_unused_reserves_and_buffers":
        raise ValueError("La exclusión no cubre todos los paquetes de T_A, incluidas sus reservas.")
    ta_documents = set(exclusion["documents"])
    if len(ta_documents) != exclusion["document_count"] or len(ta_documents) != 5233 or exclusion["packages"] != 3510:
        raise ValueError("La lista de documentos de T_A está incompleta o tiene duplicados.")
    gold_path = checked_file(a3_dir, "test_set_gold.jsonl", metrics["files"]["test_set_gold.jsonl"], hashes)
    own = []
    counts = collections.Counter()
    unclear = 0
    # De las filas ajenas solo se lee el identificador de conjunto para ignorarlas.
    # Las etiquetas humanas propias se usan aquí exclusivamente para comprobar el cierre.
    with gold_path.open(encoding="utf-8-sig") as stream:
        for line in stream:
            if not line.strip():
                continue
            record = json.loads(line)
            if record["set"] != "B":
                continue
            label = record["gold_primary"]
            if type(record["in_eval"]) is not bool or record["in_eval"] != (label != "unclear"):
                raise ValueError("El cierre humano de T_B tiene una marca contradictoria.")
            if label not in labels + ["unclear"]:
                raise ValueError("Hay una categoría desconocida en T_B.")
            if record["in_eval"]:
                counts[label] += 1
            else:
                unclear += 1
            own.append({key: record[key] for key in ["inst_key", "group_key", "citing_paper_id", "cited_paper_id"]})
    keyed_records(own, "identificadores anotados de T_B")
    expected = {"Background": 330, "Gap": 310, "Basis": 322, "Comparison": 313,
                "Application": 400, "Improvement/Modification": 268, "Evidence": 386,
                "Identification of the Originator": 324, "Further Reading": 315}
    if dict(counts) != expected or sum(counts.values()) != metrics["in_eval"]["B"] or unclear != metrics["unclear"]["B"]:
        raise ValueError("T_B no coincide con el cierre documentado de A3.")
    old_manifest = json.loads((old_ids_dir / "manifest_training_v1_G15.json").read_text(encoding="utf-8"))
    checked_file(old_ids_dir, "test_set_ids_G15.jsonl", old_manifest["files"]["test_set_ids_G15.jsonl"], hashes)
    old_index = keyed_records(read_records(old_ids_dir / "test_set_ids_G15.jsonl"), "identificadores originales G15")
    for row in own:
        if row["inst_key"] not in old_index:
            raise ValueError("Una cita del cierre T_B no está en la muestra original.")
        row["source_batch"] = old_index[row["inst_key"]]["source_batch"]
    closure = {"date": "2026-11-09", "valid_test_rows": sum(counts.values()), "unclear_test_rows": unclear,
               "valid_test_counts": dict(counts), "test_scored": False, "training_uses_human_labels": False}
    return manifest, rows, own, ta_documents, hashes, closure, exclusion


def make_independent_labels(rows, labels):
    labeled = []
    for row in rows:
        if row.get("test_set") == "A" or row.get("label_source") != "pre_label" or row.get("gold_set") is not None:
            raise ValueError("Una fila de T_A o una etiqueta humana intentó entrar al entrenamiento.")
        label = row["primary_pre_label"]
        if label not in labels:
            raise ValueError("La preetiqueta no pertenece a las nueve clases.")
        labeled.append({**row, "label": label, "label_source": "pre_label"})
    return labeled


def audit_independent_splits(train, validation, test_ids, ta_documents):
    for name, rows in [("train", train), ("validation", validation)]:
        if document_set(rows) & ta_documents:
            raise ValueError(f"Un documento de T_A aparece en {name}.")
        if any(r.get("test_set") == "A" or r.get("label_source") != "pre_label" or r.get("gold_set") is not None for r in rows):
            raise ValueError(f"Hay una cita ajena o una etiqueta humana en {name}.")
    splits = [("train", train), ("validation", validation), ("test_reserved", test_ids)]
    for i, (name, rows) in enumerate(splits):
        for other_name, other in splits[i + 1:]:
            if document_set(rows) & document_set(other):
                raise ValueError(f"Hay documentos compartidos entre {name} y {other_name}.")


def plot_independent_eda(train, validation, labels, output_root):
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
        autopct=lambda pct: f"{pct:.1f}%" if pct >= 3 else "", pctdistance=.78,
        wedgeprops={"width": .42, "edgecolor": "white"})
    pie.text(0, 0, f"{int(totals.sum()):,}\nejemplos", ha="center", va="center", fontsize=15)
    pie.set_title("Las clases de nuestros datos de trabajo")
    pie.legend(wedges, [f"{label}: {n:,} ({n / totals.sum():.1%})" for label, n in totals.items()],
        loc="upper center", bbox_to_anchor=(.5, -.02), fontsize=8, ncol=2)
    frame[["entrenamiento", "validacion"]].plot.barh(ax=bars, color=["#16877c", "#8fa6be"])
    bars.invert_yaxis()
    for container in bars.containers:
        bars.bar_label(container, fmt="%.0f", padding=3, fontsize=8)
    bars.set(xlabel="Número de ejemplos", ylabel="", title="Entrenamiento y validación por clase")
    bars.set_xlim(0, int(frame.entrenamiento.max()) * 1.22)
    fig.suptitle("A4 · Grupo 15 · etiquetas automáticas A2 · aislamiento por documento")
    fig.tight_layout()
    fig.savefig(root / "eda_class_distribution.png", dpi=160, bbox_inches="tight")
    plt.show()
    plt.close(fig)
    print(f"1. Usaremos {len(train):,} ejemplos para entrenar y {len(validation):,} para validar; T_B queda reservado.")
    print(f"2. La clase más frecuente es {totals.idxmax()} ({totals.max()/totals.sum():.1%}); "
          f"la más escasa es {totals.idxmin()} ({int(totals.min()):,} en total, {int(frame.loc[totals.idxmin(),'validacion'])} en validación).")
    return frame
