"""Preparación privada de T_B desde Drive montado. Sin API, GPU ni descargas.

No ejecuta operaciones al importar; el origen compartido solo se abre en lectura.
Los textos preparados aquí son ANTERIORES al recorte de SciBERT.
"""
from __future__ import annotations

from collections import Counter
from pathlib import Path
import hashlib
import json
import os
import re

LABELS = ["Background", "Gap", "Basis", "Comparison", "Application",
          "Improvement/Modification", "Evidence", "Identification of the Originator", "Further Reading"]
SOURCE_FOLDER_URL = "https://drive.google.com/drive/u/0/folders/11RYKPpKDissDfgVTvdXWLJekbZabRK1U"
PREPARATION_VERSION = "a5-drive-tb-base-v3"
EXPECTED_METRICS_SHA256 = "30118fea362fc4c0389ab34e2460d566d886d5dd7f11e8a84483b62b98a7ce5b"
_SENT_END = re.compile(r"[.!?](?:\s+|$)")
_ABBREVIATION = re.compile(r"(?:\bet\s+al|\be\s*\.\s*g|\bi\s*\.\s*e|\bfig|\beq|\bvs|\bsec|\bcf)\s*$", re.IGNORECASE)


def sha256(path):
    h = hashlib.sha256()
    with Path(path).open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()


def rows(path):
    with Path(path).open(encoding="utf-8-sig") as stream:
        for number, line in enumerate(stream, 1):
            if not line.strip():
                continue
            try:
                row = json.loads(line)
            except ValueError as exc:
                raise ValueError(f"JSONL inválido: {Path(path).name}, línea {number}") from exc
            if not isinstance(row, dict):
                raise ValueError(f"Se requiere un objeto: {Path(path).name}, línea {number}")
            yield row


def canonical_ids(row):
    key = row.get("inst_key")
    if not isinstance(key, str) or len(key.split("|")) != 4:
        raise ValueError("inst_key no tiene el formato canónico esperado")
    citing, paragraph, span, cited = key.split("|")
    if not citing or not cited or not paragraph.isdigit() or not re.fullmatch(r"\d+-\d+", span):
        raise ValueError(f"Clave canónica inválida: {key}")
    for field, expected in (("citing_paper_id", citing), ("cited_paper_id", cited),
                            ("citing_id", citing), ("cited_id", cited)):
        if field in row and row[field] != expected:
            raise ValueError(f"{field} no coincide con la clave: {key}")
    return citing, cited


def target_sentence(context):
    """Oración visible del target, incluso tras decodificar texto en minúsculas.

    Es una heurística: conserva abreviaturas científicas frecuentes y devuelve
    una subcadena literal. Nunca completa texto perdido por el recorte.
    """
    if context.count("[[TARGET]]") != 1:
        raise ValueError("El contexto debe contener exactamente un marcador objetivo")
    pos = context.index("[[TARGET]]")
    start, end = 0, len(context)
    for match in _SENT_END.finditer(context):
        if match.group()[0] == "." and _ABBREVIATION.search(context[:match.start()]):
            continue
        if match.group()[0] == "." and (
            re.search(r"\be\s*$", context[:match.start()], re.IGNORECASE)
            and re.match(r"g\s*\.", context[match.end():], re.IGNORECASE)
            or re.search(r"\bi\s*$", context[:match.start()], re.IGNORECASE)
            and re.match(r"e\s*\.", context[match.end():], re.IGNORECASE)
        ):
            continue
        if match.end() < len(context) and not re.match(r"[A-Za-z\[]", context[match.end()]):
            continue
        if match.start() < pos:
            start = match.end()
        else:
            end = match.start() + 1
            break
    return context[start:end].strip()


def normalize_text(row, metadata):
    key = metadata["inst_key"]
    citing, cited = canonical_ids(metadata)
    canonical_ids(row)
    out = {"inst_key": key, "citing_id": citing, "cited_id": cited, "split": "test"}
    for field in ("context", "cited_title", "cited_abstract"):
        value = row.get(field)
        if not isinstance(value, str) or not value.strip():
            raise ValueError(f"Texto faltante: {key}/{field}")
        out[field] = value.strip()
    if out["context"].count("[[TARGET]]") != 1 or "{{cite:" in out["context"]:
        raise ValueError(f"Marcadores no normalizados o target inválido: {key}")
    # El lote de A2 puede traer otros campos. No se leen ni exportan fragmentos.
    out["target_sentence"] = target_sentence(out["context"])
    return out


def inspect_drive(data_root, results_root, expected_manifest_sha256=EXPECTED_METRICS_SHA256):
    """Valida el cierre A3 sin escribir archivos ni exponer etiquetas individuales."""
    data_root, results_root = Path(data_root).resolve(), Path(results_root).resolve()
    if not data_root.is_dir():
        raise FileNotFoundError(f"No se encuentra el acceso directo montado: {data_root}")
    if not results_root.is_dir():
        raise FileNotFoundError(f"No se encuentra tu carpeta propia: {results_root}")
    if results_root == data_root or results_root.is_relative_to(data_root) or data_root.is_relative_to(results_root):
        raise ValueError("Origen compartido y resultados deben ser carpetas separadas")
    a3 = data_root / "a3"
    batch_dir = data_root / "a2" / "batches_norw"
    manifest_path, gold_path = a3 / "manifest_metrics.json", a3 / "test_set_gold.jsonl"
    for p in (manifest_path, gold_path):
        if not p.is_file():
            raise FileNotFoundError(f"Falta {p}; revisa el acceso al Drive compartido")
    if not batch_dir.is_dir():
        raise FileNotFoundError(f"Falta la carpeta de textos A2: {batch_dir}")
    manifest_hash = sha256(manifest_path)
    if expected_manifest_sha256 and manifest_hash != expected_manifest_sha256:
        raise ValueError("El manifiesto A3 difiere del usado por Sebastián. Revisa la nueva entrega antes de cambiar el hash esperado")
    manifest = json.loads(manifest_path.read_text(encoding="utf-8-sig"))
    expected_gold = manifest.get("files", {}).get("test_set_gold.jsonl")
    if not isinstance(expected_gold, str) or not re.fullmatch(r"[0-9a-f]{64}", expected_gold):
        raise ValueError("El manifiesto no declara el SHA-256 esperado de test_set_gold.jsonl")
    gold_hash = sha256(gold_path)
    if gold_hash != expected_gold:
        raise ValueError("El gold no coincide con el hash de su manifiesto")
    gold = list(rows(gold_path))
    if len(gold) != manifest.get("packages"):
        raise ValueError("Cantidad de paquetes distinta del manifiesto")
    by_key = {}
    for row in gold:
        canonical_ids(row)
        key = row["inst_key"]
        if key in by_key:
            raise ValueError(f"Gold duplicado: {key}")
        if row.get("set") not in ("A", "B") or type(row.get("in_eval")) is not bool:
            raise ValueError(f"Conjunto o in_eval inválido: {key}")
        if row.get("gold_primary") not in LABELS + ["unclear"] or row["in_eval"] != (row["gold_primary"] != "unclear"):
            raise ValueError(f"Etiqueta e in_eval incompatibles: {key}")
        if row.get("source") not in ("agreement", "adjudication"):
            raise ValueError(f"El registro no acredita el cierre humano: {key}")
        by_key[key] = row
    for group in ("A", "B"):
        valid = sum(r["set"] == group and r["in_eval"] for r in gold)
        unclear = sum(r["set"] == group and not r["in_eval"] for r in gold)
        if valid != manifest.get("in_eval", {}).get(group) or unclear != manifest.get("unclear", {}).get(group):
            raise ValueError(f"Conteos humanos de {group} no coinciden con el manifiesto")
    own = [r for r in gold if r["set"] == "B"]
    valid = [r for r in own if r["in_eval"]]
    if not valid:
        raise ValueError("T_B no contiene casos evaluables")
    return {"data_root": data_root, "results_root": results_root, "batch_dir": batch_dir,
            "gold": gold, "own": own, "valid": valid,
            "audit": {"preparation_version": PREPARATION_VERSION, "shared_folder_url": SOURCE_FOLDER_URL,
                      "a3_manifest_sha256": manifest_hash, "a3_gold_sha256": gold_hash,
                      "group": "G15", "gold_set": "B", "annotated_tb": len(own), "evaluable_tb": len(valid),
                      "excluded_unclear_tb": len(own) - len(valid),
                      "tb_counts": dict(sorted(Counter(r["gold_primary"] for r in valid).items())),
                      "test_scored": False, "api_called": False,
                      "input_state": "before_scibert_truncation", "a4_aligned": False}}


def _write_jsonl(path, values):
    temp = path.with_name(path.name + ".partial")
    with temp.open("w", encoding="utf-8") as stream:
        for value in values:
            stream.write(json.dumps(value, ensure_ascii=False, sort_keys=True, allow_nan=False) + "\n")
    os.replace(temp, path)


def prepare_tb(data_root, results_root, expected_manifest_sha256=EXPECTED_METRICS_SHA256):
    """Reconstruye T_B y guarda copias privadas, sin recortar ni ejecutar inferencia.

    Si A3 no contiene source_batch se buscan las claves en los lotes de A2.
    Duplicados idénticos entre lotes se registran; textos divergentes bloquean.
    """
    inspected = inspect_drive(data_root, results_root, expected_manifest_sha256)
    needed = {r["inst_key"]: r for r in inspected["valid"]}
    cases, origins, hashes = {}, {}, {}
    batch_dir = inspected["batch_dir"]
    files = sorted(batch_dir.glob("*.jsonl"))
    if not files:
        raise FileNotFoundError("No hay lotes JSONL en a2/batches_norw")
    for path in files:
        # No se aceptan enlaces que saquen la lectura de los lotes compartidos.
        if path.resolve().parent != batch_dir.resolve():
            raise ValueError("Lote fuera de la carpeta de origen")
        hashes[path.name] = sha256(path)
        seen = set()
        for row in rows(path):
            key = row.get("inst_key")
            if key not in needed:
                continue
            if key in seen:
                raise ValueError(f"Clave duplicada en {path.name}: {key}")
            seen.add(key)
            locator = needed[key].get("source_batch")
            if locator:
                if not isinstance(locator, str) or Path(locator).name != locator:
                    raise ValueError("Localizador source_batch inválido")
                if Path(locator).stem != path.stem:
                    continue
            case = normalize_text(row, needed[key])
            if key in cases and cases[key] != case:
                raise ValueError(f"Textos divergentes para una clave en varios lotes: {key}")
            cases[key] = case
            origins.setdefault(key, []).append(path.name)
        if sha256(path) != hashes[path.name]:
            raise ValueError("Un lote cambió durante su lectura; repetir con una entrega estable")
    missing = set(needed) - set(cases)
    if missing:
        raise ValueError(f"No se reconstruyeron {len(missing)} casos T_B; revisa que estén todos los lotes")
    if sha256(inspected["data_root"] / "a3/test_set_gold.jsonl") != inspected["audit"]["a3_gold_sha256"]:
        raise ValueError("El gold cambió durante la preparación")
    case_rows = [cases[k] for k in sorted(cases)]
    # Solo etiquetas finales necesarias para evaluación, en archivo diferente de los textos.
    gold_rows = [{"inst_key": k, "gold_primary": needed[k]["gold_primary"],
                  "label_source": "human_gold", "adjudicated": True} for k in sorted(needed)]
    # Conjunto propio completo anotado, incluidos unclear; reservas nunca anotadas se rigen por training v2.
    heldout = [{"inst_key": r["inst_key"], "citing_id": canonical_ids(r)[0], "cited_id": canonical_ids(r)[1]}
               for r in sorted(inspected["own"], key=lambda r: r["inst_key"])]
    provenance = [{"inst_key": k, "batches": origins[k]} for k in sorted(origins)]
    spec = {**inspected["audit"], "batch_hashes": hashes, "runtime_sha256": sha256(__file__),
            "input_root": str(inspected["data_root"]), "reconstructed_tb": len(case_rows),
            "identical_multi_batch_matches": sum(len(v) > 1 for v in origins.values()),
            "fewshot_prepared": False, "exclusions_prepared": False,
            "quota_note": "Cierre sin ola 4: Improvement/Modification puede quedar por debajo de 300; no completar con preetiquetas."}
    fingerprint = hashlib.sha256(json.dumps(spec, sort_keys=True, ensure_ascii=False).encode()).hexdigest()
    out = inspected["results_root"] / "A5" / "prepared" / ("tb_" + fingerprint[:16])
    marker = out / "PREPARATION_COMPLETE.json"
    if out.exists():
        if not marker.is_file():
            raise RuntimeError("Preparación privada incompleta; revisa esa carpeta antes de reutilizarla")
        complete = json.loads(marker.read_text(encoding="utf-8"))
        if complete["fingerprint"] != fingerprint:
            raise ValueError("Huella de preparación incompatible")
        for name, expected in complete["files"].items():
            if Path(name).name != name or sha256(out / name) != expected:
                raise ValueError("Cambió un archivo de la preparación privada")
    else:
        out.mkdir(parents=True)
        exports = {"test_cases.jsonl": case_rows, "test_gold.jsonl": gold_rows,
                   "tb_reserved_ids.jsonl": heldout, "text_provenance.jsonl": provenance}
        for name, values in exports.items():
            _write_jsonl(out / name, values)
        audit_path = out / "drive_audit.json"
        audit_path.write_text(json.dumps(spec, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        file_hashes = {name: sha256(out / name) for name in list(exports) + [audit_path.name]}
        marker.write_text(json.dumps({"fingerprint": fingerprint, "files": file_hashes}, indent=2) + "\n", encoding="utf-8")
    return {"audit": spec, "prepared_dir": str(out), "cases": str(out / "test_cases.jsonl"),
            "gold": str(out / "test_gold.jsonl"), "heldout": str(out / "tb_reserved_ids.jsonl"),
            "fingerprint": fingerprint}
