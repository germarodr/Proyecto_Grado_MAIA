"""Paquete diagnóstico de validación; no modifica etiquetas ni genera gold de T_B."""
import html
import json
from pathlib import Path
import numpy as np
import pandas as pd


def create_manual_review(root, evaluation_root, rows, texts, labels, seed=42):
    base = pd.read_csv(Path(evaluation_root) / "base/validation_predictions.csv")
    chunks = pd.read_csv(Path(evaluation_root) / "fragmentos/validation_predictions.csv")
    if base.inst_key.duplicated().any() or chunks.inst_key.duplicated().any():
        raise ValueError("Predicciones con claves duplicadas")
    index = {r["inst_key"]: r for r in rows}
    if set(base.inst_key) != set(index) or set(chunks.inst_key) != set(index):
        raise ValueError("Las predicciones no corresponden a esta validación")
    merged = base[["inst_key", "gold_or_prelabel", "predicted_label"]].merge(
        chunks[["inst_key", "gold_or_prelabel", "predicted_label"]], on="inst_key",
        suffixes=("_base", "_fragmentos"), validate="one_to_one")
    if not (merged.gold_or_prelabel_base == merged.gold_or_prelabel_fragmentos).all():
        raise ValueError("Las etiquetas de referencia de ambos modelos difieren")
    if not all(index[r.inst_key]["label"] == r.gold_or_prelabel_base for r in merged.itertuples()):
        raise ValueError("Las preetiquetas no corresponden a la partición actual")
    rng = np.random.default_rng(seed)
    chosen, used = [], set()
    for label in ["Evidence", "Improvement/Modification"]:
        ref = merged.gold_or_prelabel_base == label
        p0, p1 = merged.predicted_label_base == label, merged.predicted_label_fragmentos == label
        strata = [("referencia_objetivo_con_discrepancia", ref & (~p0 | ~p1), 5),
                  ("prediccion_objetivo_con_otra_referencia", ~ref & (p0 | p1), 3),
                  ("concordancia_de_control", ref & p0 & p1, 2)]
        for name, mask, count in strata:
            candidates = merged.loc[mask & ~merged.inst_key.isin(used)]
            if len(candidates) < count:
                raise ValueError(f"Suministro insuficiente para {label}/{name}")
            for i in rng.choice(candidates.index.to_numpy(), size=count, replace=False):
                record = merged.loc[i].to_dict()
                record.update(focus=label, selection_stratum=name)
                chosen.append(record)
                used.add(record["inst_key"])
    chosen = [chosen[i] for i in rng.permutation(len(chosen))]
    root = Path(root)
    root.mkdir(parents=True, exist_ok=False)
    (root / "_analisis").mkdir()
    review, key, cards = [], [], []
    for i, item in enumerate(chosen, 1):
        rid, example = f"R{i:03d}", texts[item["inst_key"]]
        row = dict(review_id=rid, primary_label="", confidence="", supporting_quote="", notes="",
                   chunks_needed="", cited_text_quality="", context=example["context"],
                   cited_title=example["title"], cited_abstract=example["abstract"])
        for j, passage in enumerate(example["chunks"], 1):
            row[f"section_{j}"] = passage["section"]
            row[f"chunk_{j}"] = passage["text"]
        review.append(row)
        key.append({"review_id": rid, **item})
        context = html.escape(example["context"]).replace("[[TARGET]]", "<mark>[[TARGET]]</mark>")
        passages = "".join(f"<h4>Fragmento {j}: {html.escape(p['section'])}</h4><p>{html.escape(p['text'])}</p>"
                           for j, p in enumerate(example["chunks"], 1))
        cards.append(f"<article><h2>{rid}</h2><h3>Contexto citante</h3><p>{context}</p>"
            f"<details><summary>Título y abstract del citado</summary><h3>{html.escape(example['title'])}</h3>"
            f"<p>{html.escape(example['abstract'])}</p></details><details><summary>Ver fragmentos del citado</summary>"
            f"{passages}</details></article>")
    frame = pd.DataFrame(review)
    frame.to_csv(root / "revision_manual.csv", index=False, encoding="utf-8-sig")
    pd.DataFrame(key).to_csv(root / "_analisis/clave_modelos.csv", index=False, encoding="utf-8-sig")
    (root / "casos_revision.html").write_text("<!doctype html><html lang='es'><meta charset='utf-8'>"
        "<title>Revisión diagnóstica A4</title><style>body{font:17px system-ui;max-width:1000px;margin:30px auto;padding:20px}"
        "article{border-top:2px solid #bbb;padding:20px 0}p{white-space:pre-wrap;line-height:1.6}"
        "details{padding:12px;background:#f5f5f5;margin:12px 0}mark{background:#ffe082}</style>"
        "<h1>20 citas para revisión diagnóstica</h1><p>Comienza por [[TARGET]]. Abre el texto citado solo para verificar. "
        "Registra tu decisión en revision_manual.xlsx o revision_manual.csv. No abras _analisis antes de terminar.</p>"
        + "".join(cards) + "</html>", encoding="utf-8")
    try:
        from openpyxl import Workbook
        from openpyxl.styles import Alignment, Font
        from openpyxl.worksheet.datavalidation import DataValidation
        workbook = Workbook()
        sheet = workbook.active
        sheet.title = "revision"
        sheet.append(list(frame.columns))
        for record in review:
            sheet.append(list(record.values()))
        sheet.freeze_panes = "H2"
        sheet.auto_filter.ref = sheet.dimensions
        for cell in sheet[1]:
            cell.font = Font(bold=True)
        for row in sheet.iter_rows(min_row=2):
            for cell in row:
                cell.alignment = Alignment(wrap_text=True, vertical="top")
        for column in ["A", "B", "C", "D", "E", "F", "G"]:
            sheet.column_dimensions[column].width = 25 if column != "E" else 50
        for column in ["H", "I", "J", "K", "L", "M", "N", "O", "P"]:
            sheet.column_dimensions[column].width = 65
        for column, values in [("B", labels + ["unclear"]), ("C", ["Alta", "Media", "Baja"]),
                               ("F", ["Si", "No"]), ("G", ["Suficiente", "Insuficiente"])]:
            validation = DataValidation(type="list", formula1='"' + ",".join(values) + '"')
            validation.errorTitle, validation.error = "Valor no válido", "Usa una opción de la lista."
            validation.showErrorMessage, validation.errorStyle = True, "stop"
            sheet.add_data_validation(validation)
            validation.add(f"{column}2:{column}21")
        instructions = workbook.create_sheet("instrucciones")
        for line in ["Revisión diagnóstica de validación; no es el gold final de T_B.",
            "Lee primero la oración de [[TARGET]] y solo lo que se refiere a esa cita.",
            "El texto citado verifica la función; no determina por sí solo la categoría.",
            "Completa primary_label, confidence, supporting_quote, notes, chunks_needed y cited_text_quality.",
            "Puedes elegir cualquiera de las nueve categorías o unclear. No fuerces Evidence o Improvement/Modification.",
            "No abras _analisis/clave_modelos.csv hasta terminar. Devuelve el XLSX o CSV con los 20 review_id."]:
            instructions.append([line])
        instructions.column_dimensions["A"].width = 115
        workbook.save(root / "revision_manual.xlsx")
    except ImportError:
        print("openpyxl no está instalado; usa revision_manual.csv.")
    manifest = {"purpose": "development_validation_diagnostic", "not_final_gold": True,
        "seed": seed, "n": len(review), "source_evaluation": str(evaluation_root),
        "focus_counts": {label: sum(item["focus"] == label for item in chosen)
                         for label in ["Evidence", "Improvement/Modification"]}}
    (root / "manifest.json").write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    print("PAQUETE_REVISION_MANUAL:", root)
    print("Casos:", len(review), "— abrir revision_manual.xlsx o revision_manual.csv y casos_revision.html")
    return root
