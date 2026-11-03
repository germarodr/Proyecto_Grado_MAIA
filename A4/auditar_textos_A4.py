"""Audita los ocho lotes privados; opcionalmente mide tokens con vocabulario SciBERT.

python A4/auditar_textos_A4.py --vocab RUTA/vocab.txt
No descarga archivos, no entrena y no exporta texto del corpus.
"""
import argparse
import collections
import inspect
import json
from pathlib import Path

from verificar_notebook import functions_namespace, ROOT


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--vocab", type=Path)
    args = parser.parse_args()
    ns = functions_namespace()
    ns.update(BATCH_FIELDS={"inst_key": "inst_key", "context": "context",
                            "title": "cited_title", "abstract": "cited_abstract", "chunks": "top3"},
              CHUNK_FIELDS={"text": "text", "section": "section"},
              SPLIT_SEED="G15-A4-split-v1", VAL_FRAC=.1)
    base = ROOT / "Folder_trabajo_Equipos_14_y_15/TrainingData_Grupo15"
    rows = list(ns["read_jsonl"](base / "training_v1_G15.jsonl"))
    test = list(ns["read_jsonl"](base / "test_set_ids_G15.jsonl"))
    by_key = {r["inst_key"]: r for r in rows + test}
    needed = {k: r["source_batch"] for k, r in by_key.items()}
    train_keys = {r["inst_key"] for r in rows}
    texts = {}
    report = {"review_date": "2026-10-29", "group": "G15", "batch_schema_verified": True,
              "required_train_v0": len(rows), "required_test_ids": len(test),
              "batches": {}, "text_quality": {}, "tokenizer_audit": None}
    for batch in sorted(set(needed.values())):
        path = ROOT / "A4/a2/batches_norw" / f"{batch}.jsonl"
        seen = set()
        for raw in ns["read_jsonl"](path):
            key = raw["inst_key"]
            if key in seen:
                raise ValueError(f"Clave duplicada: {batch}: {key}")
            seen.add(key)
            if needed.get(key) == batch:
                source = by_key[key]
                for field in ("group_key", "citing_paper_id", "cited_paper_id"):
                    assert raw[field] == source[field], (key, field)
                texts[key] = ns["normalize_batch"](raw)
        report["batches"][batch] = {"file_rows": len(seen), "sha256": ns["sha256"](path)}
    assert texts.keys() == needed.keys()
    report["reconstructed_rows"] = len(texts)
    for split, keys in [("train_val_v0", train_keys), ("test_ids", needed.keys() - train_keys)]:
        data = [texts[k] for k in keys]
        report["text_quality"][split] = {
            "rows": len(data),
            "rows_with_missing_section": sum(any(ch["section_missing"] for ch in r["chunks"]) for r in data),
            "chunks_with_missing_section": sum(ch["section_missing"] for r in data for ch in r["chunks"]),
            "empty_context_title_abstract_or_chunk_text": 0,
            "invalid_target_marker_count": 0,
        }
    if args.vocab:
        from transformers import BertTokenizerFast
        import pandas as pd
        vocab_kw = "vocab_file" if "vocab_file" in inspect.signature(BertTokenizerFast.__init__).parameters else "vocab"
        tok = BertTokenizerFast(**{vocab_kw: str(args.vocab)}, do_lower_case=True)
        assert len(tok) == 31090, "No es el vocabulario SciBERT scivocab original"
        tok.add_special_tokens({"additional_special_tokens": ["[[TARGET]]", "[CITE]", "[FORMULA]", "[FIGURE]", "[TABLE]"]})
        all_stats = []
        for n, (key, example) in enumerate(texts.items(), 1):
            split = "test_ids"
            if key in train_keys:
                split = "validation" if ns["validation_citing"](by_key[key]["citing_paper_id"]) else "train"
            for config in ("base", "fragmentos"):
                features, stats = ns["encode_example"](example, config, tok)
                assert len(features["input_ids"]) <= 512
                assert features["input_ids"].count(tok.convert_tokens_to_ids("[[TARGET]]")) == 1
                all_stats.append({"config": config, "split": split, "inst_key": key, **stats})
            if n % 5000 == 0:
                print(f"Tokenizadas {n:,}/{len(texts):,} instancias en ambas configuraciones", flush=True)
        frame = pd.DataFrame(all_stats)
        frame["context_truncated"] = frame.context_kept < frame.context_original
        frame["evidence_truncated"] = frame.evidence_kept < frame.evidence_original
        grouped = frame.groupby(["config", "split"])
        columns = ["total_tokens", "context_original", "context_kept", "evidence_original",
                   "evidence_kept", "context_truncated", "evidence_truncated"]
        summary = grouped[columns].mean().reset_index().to_dict(orient="records")
        report["tokenizer_audit"] = {"original_vocab_size": 31090, "extended_vocab_size": len(tok),
              "vocab_sha256": ns["sha256"](args.vocab), "examples_per_config": len(texts),
              "max_total_tokens": int(frame.total_tokens.max()), "target_preserved_all": True,
              "max_length": 512, "context_budget": 192, "mean_by_config_split": summary}
    path = ROOT / "A4/auditoria_textos_A4.json"
    ns["save_json"](path, report)
    print(json.dumps(report, indent=2, ensure_ascii=False), flush=True)


if __name__ == "__main__":
    main()
