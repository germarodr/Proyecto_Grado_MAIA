"""Recorte SciBERT base (contexto, título, resumen) y banco humano A5."""
from __future__ import annotations

from collections import Counter
from pathlib import Path
import hashlib
import inspect
import json

import a5_drive as drive
import a5_runtime as runtime

LABELS = runtime.LABELS
MODEL_ID = "allenai/scibert_scivocab_uncased"
MODEL_REVISION = "24f92d32b1bfb0bcaf9ab193ff3ad01e87732fc1"
MARKERS = ["[[TARGET]]", "[CITE]", "[FORMULA]", "[FIGURE]", "[TABLE]"]
VERSION = "a5-scibert-base-alignment-v3"


def encode_example_reference(example, config, tok, max_length=512, context_budget=192):
    """Misma política que encode_example_reference en la entrega de Sebastián."""
    ids = lambda s: tok.encode(s, add_special_tokens=False)
    context = ids(example["context"])
    target_id = tok.convert_tokens_to_ids("[[TARGET]]")
    if context.count(target_id) != 1:
        raise ValueError("El contexto debe contener exactamente un marcador objetivo.")
    target = context.index(target_id)
    start = max(0, min(target - context_budget // 2, len(context) - context_budget))
    context_cut = context[start:start + context_budget]
    assert tok.num_special_tokens_to_add(pair=True) == 3, "Se requiere tokenizador BERT."
    budget = max_length - 3 - len(context_cut)
    assert budget >= 32 and target_id in context_cut
    stats = {"context_original": len(context), "context_kept": len(context_cut)}
    if config == "base":
        title = ids("Title: " + example["title"])
        abstract = ids("Abstract: " + example["abstract"])
        title_kept = title[:min(64, budget // 3)]
        abstract_kept = abstract[:budget - len(title_kept)]
        evidence = title_kept + abstract_kept
        stats.update(evidence_original=len(title) + len(abstract), evidence_kept=len(evidence),
                     title_original=len(title), title_kept=len(title_kept),
                     abstract_original=len(abstract), abstract_kept=len(abstract_kept))
    else:
        raise ValueError("A5 solo admite la configuración base")
    input_ids = [tok.cls_token_id] + context_cut + [tok.sep_token_id] + evidence + [tok.sep_token_id]
    token_types = [0] * (len(context_cut) + 2) + [1] * (len(evidence) + 1)
    assert len(input_ids) <= max_length and len(token_types) == len(input_ids)
    stats["total_tokens"] = len(input_ids)
    return {"input_ids": input_ids, "attention_mask": [1] * len(input_ids),
            "token_type_ids": token_types}, stats


def tokenizer_fingerprint(tok):
    if tok.num_special_tokens_to_add(pair=True) != 3:
        raise ValueError("Se requiere el tokenizador BERT de SciBERT")
    marker_ids = [tok.convert_tokens_to_ids(m) for m in MARKERS]
    if len(set(marker_ids)) != len(MARKERS) or tok.unk_token_id in marker_ids:
        raise ValueError("Registrar los cinco marcadores como tokens especiales, en el orden de Sebastián")
    return {"model_id": MODEL_ID, "revision": MODEL_REVISION,
            "vocabulary_sha256": runtime.digest(tok.get_vocab()), "marker_ids": marker_ids,
            "max_length": 512, "context_budget": 192, "title_budget": 64,
            "encoder_sha256": hashlib.sha256(inspect.getsource(encode_example_reference).encode()).hexdigest(),
            "display": "decode retained token IDs, skip_special_tokens=False, clean_up_tokenization_spaces=False"}


def load_tokenizer(local_path=None):
    """Solo tokenizer/vocabulario, nunca pesos del modelo. Importación opcional."""
    from transformers import AutoTokenizer
    if local_path is not None:
        tok = AutoTokenizer.from_pretrained(str(local_path), use_fast=True, local_files_only=True, token=False)
    else:
        tok = AutoTokenizer.from_pretrained(MODEL_ID, revision=MODEL_REVISION, use_fast=True, token=False)
    tok.add_special_tokens({"additional_special_tokens": MARKERS})
    tokenizer_fingerprint(tok)
    return tok


def align_case(case, tok):
    example = {"context": case["context"], "title": case["cited_title"], "abstract": case["cited_abstract"]}
    out = {k: v for k, v in case.items() if k not in ("top3", "chunks", "a4_inputs")}
    out["a4_inputs"] = {}; audits = []
    for rep in ("base",):
        features, stats = encode_example_reference(example, rep, tok)
        n = stats["context_kept"]
        ids = features["input_ids"]
        context_ids, evidence_ids = ids[1:n + 1], ids[n + 2:-1]
        context = tok.decode(context_ids, skip_special_tokens=False, clean_up_tokenization_spaces=False)
        evidence = tok.decode(evidence_ids, skip_special_tokens=False, clean_up_tokenization_spaces=False)
        if context.count("[[TARGET]]") != 1 or not evidence.strip():
            raise ValueError(f"La decodificación no preserva la entrada: {case['inst_key']}/{rep}")
        # La oración se toma SOLO del contexto visible. Nunca se añade la oración original completa.
        out["a4_inputs"][rep] = {"context": context, "target_sentence": drive.target_sentence(context), "evidence": evidence}
        audits.append({"inst_key": case["inst_key"], "representation": rep, "input_ids": ids,
                       "token_type_ids": features["token_type_ids"], "input_ids_sha256": runtime.digest(ids),
                       "visible_text_sha256": runtime.digest(out["a4_inputs"][rep]), **stats})
    return out, audits


def docs(row):
    return set(drive.canonical_ids(row))


def select_development(gold, per_class=5, seed="G15-A5-fewshot-v1", excluded_keys=None):
    """Selección por hash y etiqueta humana, sin consultar predicciones ni aciertos de T_B."""
    if type(per_class) is not int or per_class < 1:
        raise ValueError("El piloto necesita al menos un caso por categoría")
    tb = [r for r in gold if r["set"] == "B"]
    forbidden = {p for r in tb for p in docs(r)}
    excluded = set(excluded_keys or [])
    eligible_keys = {r["inst_key"] for r in gold if r["set"] == "A" and r["in_eval"]}
    if excluded - eligible_keys:
        raise ValueError("Las exclusiones de desarrollo deben pertenecer al gold evaluable de T_A")
    candidates = [r for r in gold if r["set"] == "A" and r["in_eval"]
                  and r["inst_key"] not in excluded and not docs(r) & forbidden]
    rank = lambda r: hashlib.sha256((seed + "|" + r["inst_key"]).encode()).hexdigest()
    candidates.sort(key=rank)
    bank = []
    for label in LABELS:
        eligible = [r for r in candidates if r["gold_primary"] == label]
        if not eligible:
            raise ValueError(f"No hay ejemplo humano T_A elegible de {label} con V2; no se usa T_B como reemplazo")
        bank.append(eligible[0])
    bank_docs = {p for r in bank for p in docs(r)}
    pilot = []
    for label in LABELS:
        eligible = [r for r in candidates if r["gold_primary"] == label and not docs(r) & bank_docs]
        if len(eligible) < per_class:
            raise ValueError(f"Piloto: {label} tiene {len(eligible)} candidatos separados del banco, se pidieron {per_class}. Revisar per_class sin relajar V2 ni usar T_B")
        pilot.extend(eligible[:per_class])
    return bank, pilot, {"candidate_counts": dict(Counter(r["gold_primary"] for r in candidates)),
                          "seed": seed, "pilot_per_class": per_class, "development_excluded_keys": sorted(excluded),
                          "selection": "fixed SHA-256 order per human category; no model predictions used",
                          "fewshot_reviewed": False, "fewshot_n": len(bank), "pilot_n": len(pilot)}


def reconstruct_selected(inspected, metadata):
    """Recupera solamente el banco y el piloto seleccionados de T_A."""
    needed = {r["inst_key"]: r for r in metadata}
    found = {}; hashes = {}; origins = {}
    for path in sorted(inspected["batch_dir"].glob("*.jsonl")):
        if path.resolve().parent != inspected["batch_dir"].resolve():
            raise ValueError("Lote fuera de la carpeta compartida")
        before = drive.sha256(path); hashes[path.name] = before; seen = set()
        for row in drive.rows(path):
            key = row.get("inst_key")
            if key not in needed: continue
            if key in seen: raise ValueError(f"Clave repetida en el lote: {key}")
            seen.add(key)
            locator = needed[key].get("source_batch")
            if locator:
                if not isinstance(locator, str) or Path(locator).name != locator:
                    raise ValueError("Localizador de lote inválido")
                if Path(locator).stem != path.stem: continue
            case = drive.normalize_text(row, needed[key]); case["split"] = "dev"
            if key in found and case != found[key]:
                raise ValueError(f"Textos divergentes para {key}")
            found[key] = case; origins.setdefault(key, []).append(path.name)
        if drive.sha256(path) != before: raise ValueError("Lote modificado durante la lectura")
    missing = set(needed) - set(found)
    if missing: raise ValueError(f"No se encontraron {len(missing)} textos T_A seleccionados")
    return found, hashes, origins


def prepare_aligned(data_root, results_root, preparation, tok, per_class=5,
                    seed="G15-A5-fewshot-v1", expected_manifest_sha256=drive.EXPECTED_METRICS_SHA256,
                    excluded_keys=None):
    inspected = drive.inspect_drive(data_root, results_root, expected_manifest_sha256)
    prepared_dir = Path(preparation["prepared_dir"]).resolve()
    private_root = inspected["results_root"] / "A5" / "prepared"
    if not prepared_dir.is_relative_to(private_root.resolve()):
        raise ValueError("La preparación T_B debe estar en la carpeta privada de A5")
    complete = json.loads((prepared_dir / "PREPARATION_COMPLETE.json").read_text(encoding="utf-8"))
    if complete["fingerprint"] != preparation["fingerprint"]:
        raise ValueError("Preparación T_B incompatible")
    for name, digest in complete["files"].items():
        if Path(name).name != name or drive.sha256(prepared_dir / name) != digest:
            raise ValueError("La preparación T_B cambió; repetir la verificación")
    old_audit = json.loads((prepared_dir / "drive_audit.json").read_text(encoding="utf-8"))
    if old_audit["a3_gold_sha256"] != inspected["audit"]["a3_gold_sha256"]:
        raise ValueError("El gold cambió desde el bloque 3.1")
    tb = runtime.normalize_cases(runtime.read_jsonl(prepared_dir / "test_cases.jsonl"), "test")
    if {r["inst_key"] for r in tb} != {r["inst_key"] for r in inspected["valid"]}:
        raise ValueError("La preparación no contiene todo T_B evaluable")
    bank_meta, pilot_meta, selection = select_development(inspected["gold"], per_class, seed, excluded_keys)
    texts, batch_hashes, origins = reconstruct_selected(inspected, bank_meta + pilot_meta)
    if batch_hashes != old_audit["batch_hashes"]:
        raise ValueError("Los lotes de A2 cambiaron entre las preparaciones")
    bank = [texts[r["inst_key"]] for r in bank_meta]
    pilot = [texts[r["inst_key"]] for r in pilot_meta]
    heldout = runtime.read_jsonl(prepared_dir / "tb_reserved_ids.jsonl")
    expected_heldout = {r["inst_key"] for r in inspected["own"]}
    if {r["inst_key"] for r in heldout} != expected_heldout:
        raise ValueError("IDs de aislamiento incompletos")
    runtime.audit_isolation(pilot, bank, heldout, [], "V2")
    all_aligned, audits = {}, []
    for case in tb + bank + pilot:
        aligned, audit = align_case(case, tok)
        all_aligned[case["inst_key"]] = aligned; audits.extend(audit)
    tb = [all_aligned[r["inst_key"]] for r in tb]
    bank = [all_aligned[r["inst_key"]] for r in bank]
    pilot = [all_aligned[r["inst_key"]] for r in pilot]
    for group, split in [(tb, "test"), (bank, "dev"), (pilot, "dev")]: runtime.normalize_cases(group, split)
    def gold_rows(metadata):
        return [{"inst_key": r["inst_key"], "gold_primary": r["gold_primary"], "label_source": "human_gold", "adjudicated": True} for r in metadata]
    # Esta lista excluye los unclear de A3; el universo permitido es el gold humano final de T_A.
    # No se presenta como la lista de exclusión general del entrenamiento de A4.
    exclusions = [{"inst_key": r["inst_key"]} for r in inspected["gold"] if not r["in_eval"]]
    policy = tokenizer_fingerprint(tok)
    spec = {"version": VERSION, "policy": policy, "runtime_sha256": drive.sha256(__file__),
            "tb_preparation_fingerprint": preparation["fingerprint"], **selection,
            "bank_keys": [r["inst_key"] for r in bank], "pilot_keys": [r["inst_key"] for r in pilot],
            "sources": {"gold_sha256": inspected["audit"]["a3_gold_sha256"], "batch_hashes": batch_hashes},
            "isolated_from_tb": "V2: both article roles; includes unclear TB in isolation",
            "bank_pilot_isolation": "both article roles", "api_called": False, "test_scored": False,
            "input_state": "scibert_retained_token_ids_decoded", "test_cases": len(tb)}
    fingerprint = runtime.digest(spec)
    out = private_root / ("aligned_" + fingerprint[:16])
    files = {"test_cases.jsonl": tb, "test_gold.jsonl": gold_rows(inspected["valid"]),
             "fewshot_cases.jsonl": bank, "fewshot_gold.jsonl": gold_rows(bank_meta),
             "dev_cases.jsonl": pilot, "dev_gold.jsonl": gold_rows(pilot_meta),
             "tb_reserved_ids.jsonl": heldout, "exclusion_list.jsonl": exclusions,
             "alignment_audit.jsonl": audits,
             "development_provenance.jsonl": [{"inst_key": k, "batches": v} for k, v in sorted(origins.items())]}
    marker = out / "ALIGNMENT_COMPLETE.json"
    if out.exists():
        if not marker.is_file(): raise ValueError("Alineación privada incompleta; revisar antes de reutilizar")
        stored = json.loads(marker.read_text(encoding="utf-8"))
        if stored["fingerprint"] != fingerprint: raise ValueError("Huella de alineación incompatible")
        for name, expected in stored["files"].items():
            if Path(name).name != name or drive.sha256(out / name) != expected:
                raise ValueError("Cambió una exportación de la alineación")
    else:
        out.mkdir(parents=True)
        for name, values in files.items(): drive._write_jsonl(out / name, values)
        runtime.write_json(out / "alignment_manifest.json", spec)
        hashes = {name: drive.sha256(out / name) for name in list(files) + ["alignment_manifest.json"]}
        runtime.write_json(marker, {"fingerprint": fingerprint, "files": hashes})
    return {"prepared_dir": str(out), "fingerprint": fingerprint,
            "policy_version": VERSION + ":" + runtime.digest(policy), "manifest": spec,
            "paths": {"cases": str(out / "dev_cases.jsonl"), "gold": str(out / "dev_gold.jsonl"),
                      "heldout": str(out / "tb_reserved_ids.jsonl"), "exclusions": str(out / "exclusion_list.jsonl"),
                      "examples": str(out / "fewshot_cases.jsonl"), "example_gold": str(out / "fewshot_gold.jsonl")},
            "test_paths": {"cases": str(out / "test_cases.jsonl"), "gold": str(out / "test_gold.jsonl")}}
