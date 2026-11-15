"""Evaluación final de dos exportaciones congeladas. No contiene entrenamiento."""
import collections
import contextlib
import gc
import hashlib
import html
import importlib.util
import json
import math
import os
from pathlib import Path
import shutil
import sys
import time
import uuid

import numpy as np
import pandas as pd
from sklearn.metrics import classification_report, confusion_matrix, precision_recall_fscore_support


def sha256(path):
    digest = hashlib.sha256()
    with Path(path).open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def json_digest(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True, ensure_ascii=False, allow_nan=False).encode()).hexdigest()


def save_json(path, value):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(path.name + ".partial_" + uuid.uuid4().hex)
    temporary.write_text(json.dumps(value, ensure_ascii=False, indent=2, allow_nan=False) + "\n", encoding="utf-8")
    os.replace(temporary, path)


def freeze_json(path, value):
    path = Path(path)
    if path.exists() and json.loads(path.read_text(encoding="utf-8")) != value:
        raise ValueError(f"Cambió el protocolo guardado en {path.name}; no se mezclarán resultados.")
    save_json(path, value)


def records(path):
    with Path(path).open(encoding="utf-8-sig") as stream:
        return [json.loads(line) for line in stream if line.strip()]


def verify_files(directory, hashes):
    directory = Path(directory).resolve()
    if not hashes:
        raise ValueError("Faltan huellas de los archivos.")
    for name, expected in hashes.items():
        path = (directory / name).resolve()
        if not path.is_relative_to(directory) or not path.is_file() or sha256(path) != expected:
            raise ValueError(f"Archivo ausente o distinto del esperado: {name}")


def keyed(rows):
    index = {}
    for row in rows:
        key = row["inst_key"]
        if key in index:
            raise ValueError(f"Instancia repetida: {key}")
        citing, _, _, cited = key.split("|")
        if citing != row["citing_paper_id"] or cited != row["cited_paper_id"] or citing == cited:
            raise ValueError("El identificador no corresponde a sus documentos.")
        index[key] = row
    return index


def document_set(rows):
    return {r[k] for r in rows for k in ["citing_paper_id", "cited_paper_id"]}


def verify_isolation(train, validation, reserved):
    sets = {"train": document_set(train), "validation": document_set(validation), "test": document_set(reserved)}
    for left, right in [("train", "validation"), ("train", "test"), ("validation", "test")]:
        if sets[left] & sets[right]:
            raise ValueError(f"Hay documentos compartidos entre {left} y {right}.")
    return {"passed": True, "documents": {k: len(v) for k, v in sets.items()}, "roles": "citing_and_cited"}


def prepare_test(study_root, a3_dir, old_ids_dir, pins, output):
    study_root, a3_dir, old_ids_dir, output = map(Path, [study_root, a3_dir, old_ids_dir, output])
    closed = json.loads((study_root / "STUDY_COMPLETE.json").read_text())
    if closed["study_id"] != pins["source_study_id"] or closed["test_scored"] is not False:
        raise ValueError("La selección no corresponde al estudio previo previsto.")
    verify_files(study_root, closed["report_hashes"])
    selected = json.loads((study_root / "selected_models.json").read_text())
    if selected["models"] != pins["models"] or selected["test_scored"] is not False:
        raise ValueError("Los modelos seleccionados cambiaron respecto de la selección congelada.")
    train_path, validation_path = [study_root / f"split_{name}_ids.jsonl" for name in ["train", "validation"]]
    for name, path in [("train", train_path), ("validation", validation_path)]:
        if sha256(path) != pins["split_hashes"][name]:
            raise ValueError("Cambió una partición de aprendizaje.")
    gold_path, metrics_path = a3_dir / "test_set_gold.jsonl", a3_dir / "manifest_metrics.json"
    ids_path = old_ids_dir / "test_set_ids_G15.jsonl"
    for path in [gold_path, metrics_path, ids_path]:
        if sha256(path) != pins["input_hashes"][path.name]:
            raise ValueError(f"La fuente humana o sus localizadores cambiaron: {path.name}")
    gold = records(gold_path)
    keyed(gold)
    own = [r for r in gold if r["set"] == "B"]
    if len(own) != 2970 or sum(r["in_eval"] is True for r in own) != 2968:
        raise ValueError("El test propio difiere del cierre humano congelado.")
    index = keyed(records(ids_path))
    reserved, test = [], []
    for human in own:
        source = index[human["inst_key"]]
        if human["in_eval"] is not (human["gold_primary"] in pins["labels"]):
            raise ValueError("La etiqueta y la marca de evaluación se contradicen.")
        row = {k: source[k] for k in ["inst_key", "citing_paper_id", "cited_paper_id", "source_batch"]}
        reserved.append(row)
        if human["in_eval"]:
            test.append({**row, "reference": human["gold_primary"]})
    train, validation = records(train_path), records(validation_path)
    keyed(train); keyed(validation); keyed(test)
    if (len(train), len(validation)) != (11616, 1653):
        raise ValueError("Los tamaños del aprendizaje no coinciden.")
    audit = verify_isolation(train, validation, reserved)
    test.sort(key=lambda r: r["inst_key"])
    counts = collections.Counter(r["reference"] for r in test)
    expected = dict(zip(pins["labels"], [330, 310, 322, 313, 400, 268, 386, 324, 315]))
    if dict(counts) != expected:
        raise ValueError("La distribución humana difiere del cierre revisado.")
    audit.update(valid_rows=len(test), unclear_excluded=2, reserved_rows=len(reserved),
        gold_sha256=sha256(gold_path), test_order_sha256=json_digest(test),
        split_hashes=pins["split_hashes"], source_closure_sha256=sha256(study_root / "STUDY_COMPLETE.json"))
    freeze_json(output / "data_audit.json", audit)
    pd.DataFrame(test).to_csv(output / "test_instances.csv", index=False)
    return test, train, validation, audit


def show_test_data(test, train, validation, labels, output):
    import matplotlib.pyplot as plt
    from IPython.display import display
    counts = pd.DataFrame({"Entrenamiento": collections.Counter(r["label"] for r in train),
        "Validación interna": collections.Counter(r["label"] for r in validation),
        "Test humano": collections.Counter(r["reference"] for r in test)}).reindex(labels).fillna(0).astype(int)
    counts.to_csv(Path(output) / "class_distribution.csv")
    fig, axes = plt.subplots(1, 2, figsize=(17, 7))
    wedges, _, _ = axes[0].pie(counts["Test humano"], startangle=90, autopct="%.1f%%",
        wedgeprops={"width": .4, "edgecolor": "white"})
    axes[0].text(0, 0, f"{len(test):,}\ncitas", ha="center", va="center", fontsize=16)
    axes[0].set_title("Nuestro test validado por personas")
    axes[0].legend(wedges, labels, loc="upper center", bbox_to_anchor=(.5, -.02), fontsize=8, ncol=2)
    counts.plot.barh(ax=axes[1], color=["#8fa6be", "#b8c9d9", "#16877c"])
    axes[1].invert_yaxis()
    axes[1].set(xlabel="Ejemplos", ylabel="", title="Cómo se distribuyen los tres conjuntos")
    fig.tight_layout()
    fig.savefig(Path(output) / "class_distribution.png", dpi=160, bbox_inches="tight")
    plt.show(); plt.close(fig)
    display(counts)
    print(f"Evaluaremos {len(test):,} citas; dos casos sin categoría clara quedan excluidos del cálculo.")
    return counts


def reconstruct_test(test, batch_dir, pins, output):
    texts, hashes = {}, {}
    required = {r["inst_key"]: r["source_batch"] for r in test}
    for batch in sorted(set(required.values())):
        path = Path(batch_dir) / (batch + ".jsonl")
        digest = sha256(path)
        if digest != pins["batch_hashes"].get(batch):
            raise ValueError(f"El lote no coincide con la preparación original: {batch}")
        hashes[batch] = digest
        seen = set()
        for raw in read_jsonl(path):
            key = raw["inst_key"]
            if key in seen:
                raise ValueError(f"Clave repetida en {batch}: {key}")
            seen.add(key)
            if required.get(key) == batch:
                texts[key] = normalize_batch(raw)
    if set(texts) != set(required):
        raise ValueError("No se reconstruyeron todas las entradas del test para ambos modelos.")
    audit = {"n": len(texts), "batch_hashes": hashes, "texts_sha256": json_digest(texts),
             "missing_sections": sum(ch["section_missing"] for r in texts.values() for ch in r["chunks"])}
    freeze_json(Path(output) / "reconstruction_audit.json", audit)
    return texts, audit


def model_payload(text, config):
    if config == "base":
        return {k: text[k] for k in ["context", "title", "abstract"]}
    if config == "fragmentos" and len(text["chunks"]) == 3:
        return {"context": text["context"], "chunks": [{k: c[k] for k in ["text", "section"]} for c in text["chunks"]]}
    raise ValueError("La configuración o el número de fragmentos no es válido.")


def show_examples(test, texts, output):
    from IPython.display import HTML, display
    examples = []
    for row in test[:2]:
        example = {"inst_key": row["inst_key"], "expected_human_label": row["reference"],
                   "base_input": model_payload(texts[row["inst_key"]], "base"),
                   "top3_input": model_payload(texts[row["inst_key"]], "fragmentos")}
        examples.append(example)
        blocks = [f"<h3>Ejemplo {len(examples)} · {html.escape(row['inst_key'])}</h3>",
                  f"<p><b>Referencia humana esperada:</b> {html.escape(row['reference'])}. Se usa para evaluar; no se envía al modelo.</p>"]
        for title, payload in [("Entrada de base", example["base_input"]), ("Entrada de Top-3", example["top3_input"])]:
            blocks.append(f"<details open><summary><b>{title}</b></summary><pre style='white-space:pre-wrap'>" +
                          html.escape(json.dumps(payload, ensure_ascii=False, indent=2)) + "</pre></details>")
        display(HTML("\n".join(blocks)))
    save_json(Path(output) / "two_real_examples.json", examples)


def load_validation_reference(study_root, pins, output):
    reference, reports = {}, {}
    for config, selected in pins["models"].items():
        trial = Path(study_root) / "trials" / selected["trial_id"]
        close = json.loads((trial / "EVALUATION_COMPLETE.json").read_text())
        verify_files(trial / "evaluation", close["files"])
        result = json.loads((trial / "evaluation/result.json").read_text())
        if result["trial_id"] != selected["trial_id"] or result["seed"] != 42 or result["n"] != 1653:
            raise ValueError("La referencia de validación no corresponde al modelo seleccionado.")
        trained=json.loads((trial/"TRAINING_COMPLETE.json").read_text())
        if (trained["model_hashes"] != selected["model_hashes"]
                or result["model_marker_sha256"] != sha256(trial/"TRAINING_COMPLETE.json")
                or not math.isclose(result["f1_macro"],selected["validation_fp32_f1_macro"],abs_tol=1e-12)):
            raise ValueError("El reporte de validación no está vinculado a la exportación seleccionada.")
        reference[config] = result
        reports[config] = json.loads((trial / "evaluation/classification_report.json").read_text())
    save_json(Path(output) / "validation_reference.json", {"results": reference, "reports": reports,
        "reference_type": "125 human and 1528 automatic labels; seed 42; not the three-seed mean"})
    return reference, reports


def verify_protocol(protocol):
    if (protocol["evaluation_policy"] != "fp32_eager" or protocol["batch_size"] != 32
            or protocol["models"].keys() != {"base", "fragmentos"} or protocol["test_count"] != 2968):
        raise ValueError("El protocolo final debe conservar las dos entradas y la evaluación prevista.")
    for config, spec in protocol["models"].items():
        if (spec["primary_seed"] != 42 or spec["context_budget"] != 192 or spec["loss_mode"] != "sin_pesos"
                or spec["learning_rate"] != 3e-5 or spec["weight_decay"] != .1):
            raise ValueError("Los modelos deben conservar la selección previa al test.")


def local_export(study_root, config, selected, cache_root):
    source = Path(study_root) / "trials" / selected["trial_id"] / "model"
    target = Path(cache_root) / config
    verify_files(source, selected["model_hashes"])
    target.mkdir(parents=True, exist_ok=True)
    for name, expected in selected["model_hashes"].items():
        dest = target / name
        if not dest.exists() or sha256(dest) != expected:
            dest.parent.mkdir(parents=True, exist_ok=True)
            temporary = dest.with_name(dest.name + ".partial_" + uuid.uuid4().hex)
            shutil.copyfile(source / name, temporary)
            if sha256(temporary) != expected:
                raise ValueError("La copia local del modelo no coincide.")
            os.replace(temporary, dest)
    verify_files(target, selected["model_hashes"])
    return target


def load_classifier(path, device):
    spec = importlib.util.spec_from_file_location("final_inference_" + uuid.uuid4().hex, Path(path) / "inference.py")
    module = importlib.util.module_from_spec(spec)
    previous = sys.dont_write_bytecode
    try:
        sys.dont_write_bytecode = True
        spec.loader.exec_module(module)
    finally:
        sys.dont_write_bytecode = previous
    classifier = module.CitationClassifier(path, device=device)
    classifier.model.float().eval()
    return module, classifier


def validate_prediction_frame(frame, expected_rows, labels, config):
    if len(frame) != len(expected_rows) or frame.inst_key.duplicated().any():
        raise ValueError("Las predicciones tienen filas ausentes o repetidas.")
    for row, expected in zip(frame.to_dict("records"), expected_rows):
        if any(row[k] != expected[k] for k in ["inst_key", "citing_paper_id", "cited_paper_id", "reference"]):
            raise ValueError("Las predicciones cambiaron de orden o referencia.")
        if row["config"] != config:
            raise ValueError("Se mezclaron modelos en las predicciones.")
    probabilities = frame[["score_" + label for label in labels]].to_numpy(float)
    if (not np.isfinite(probabilities).all() or (probabilities < 0).any() or (probabilities > 1).any()
            or not np.allclose(probabilities.sum(axis=1), 1, atol=1e-5)):
        raise ValueError("Probabilidades inválidas.")
    if not np.array_equal(np.asarray(labels)[probabilities.argmax(axis=1)], frame.pred_label.to_numpy()):
        raise ValueError("La categoría predicha no coincide con las probabilidades.")
    for column in ["latency_ms", "tokenization_ms", "inference_ms"]:
        values = frame[column].to_numpy(float)
        if not np.isfinite(values).all() or (values < 0).any():
            raise ValueError("La medición de tiempo no es válida.")


def read_part(path, receipt, expected, labels, config, protocol_hash):
    if not receipt.exists():
        return None
    marker = json.loads(receipt.read_text())
    if marker["protocol_sha256"] != protocol_hash or sha256(path) != marker["sha256"]:
        raise ValueError("Un lote guardado pertenece a otro protocolo o está dañado.")
    frame = pd.read_csv(path, dtype={"inst_key":str,"citing_paper_id":str,"cited_paper_id":str,
                                     "reference":str,"pred_label":str,"config":str})
    validate_prediction_frame(frame, expected, labels, config)
    return frame


def score_model(config, test, texts, protocol, study_root, cache_root, output, tracking, device="cuda"):
    import torch
    from transformers import DataCollatorWithPadding
    labels, size = protocol["labels"], protocol["batch_size"]
    protocol_hash = json_digest(protocol)
    directory = Path(output) / config
    parts = directory / "parts"
    parts.mkdir(parents=True, exist_ok=True)
    chunks = [test[start:start + size] for start in range(0, len(test), size)]
    cached = [read_part(parts / f"{i:05d}.csv", parts / f"{i:05d}.complete.json", rows, labels, config, protocol_hash)
              for i, rows in enumerate(chunks)]
    if all(frame is not None for frame in cached):
        print(config, ": todas las predicciones están verificadas; reutilizamos la inferencia.")
    with tracking.evaluation(config, directory, policy="test_gold_fp32") as run:
        tracking.client.set_tag(run, "reference", "human_gold_B")
        tracking.client.log_param(run, "protocol_sha256", protocol_hash)
        tracking.client.log_param(run, "trial_id", protocol["models"][config]["trial_id"])
        tracking.client.log_param(run, "latency_definition", "tokenization+forward; batch-average; warmup/IO excluded")
        tracking.backup(force=True)
        classifier = None
        try:
            if any(frame is None for frame in cached):
                path = local_export(study_root, config, protocol["models"][config], cache_root)
                module, classifier = load_classifier(path, device)
                mapping = {int(k): v for k, v in classifier.model.config.id2label.items()}
                if (mapping != dict(enumerate(labels)) or classifier.policy["config"] != config
                        or classifier.policy["context_budget"] != 192 or classifier.policy["max_length"] != 512
                        or classifier.model.config._attn_implementation != "eager"):
                    raise ValueError("La exportación cambió de categorías o preparación.")
                collator = DataCollatorWithPadding(classifier.tokenizer, pad_to_multiple_of=8)
                # Calentamiento sintético: no consulta etiquetas ni escoge modelos.
                warm = {"context": "We refer to [[TARGET]] for the method.", "title": "A scientific method",
                        "abstract": "A description of the scientific method.",
                        "chunks": [{"text": "A description of the scientific method.", "section": "Methods"}] * 3}
                feature, _ = module.encode_example(model_payload(warm, config), config, classifier.tokenizer, 512, 192)
                batch = {k: v.to(device) for k, v in collator([feature]).items()}
                with torch.inference_mode(), torch.autocast(device_type=torch.device(device).type, enabled=False):
                    classifier.model(**batch)
                if torch.device(device).type == "cuda": torch.cuda.synchronize()
            for i, rows in enumerate(chunks):
                if cached[i] is not None:
                    continue
                started = time.perf_counter()
                features, audits = [], []
                for row in rows:
                    feature, audit = module.encode_example(model_payload(texts[row["inst_key"]], config), config,
                                                           classifier.tokenizer, 512, 192)
                    features.append(feature); audits.append(audit)
                batch = {k: v.to(device) for k, v in collator(features).items()}
                if torch.device(device).type == "cuda": torch.cuda.synchronize()
                tokenization_ms = 1000 * (time.perf_counter() - started)
                started = time.perf_counter()
                with torch.inference_mode(), torch.autocast(device_type=torch.device(device).type, enabled=False):
                    probabilities = classifier.model(**batch).logits.float().softmax(-1).cpu().numpy()
                if torch.device(device).type == "cuda": torch.cuda.synchronize()
                inference_ms = 1000 * (time.perf_counter() - started)
                records_out = []
                for row, values, token_audit in zip(rows, probabilities, audits):
                    records_out.append({**row, "config": config, "measurement_run_id":str(run), "pred_label": labels[int(values.argmax())],
                        **{"score_" + label: float(p) for label, p in zip(labels, values)},
                        "latency_ms": (tokenization_ms + inference_ms) / len(rows),
                        "tokenization_ms": tokenization_ms / len(rows), "inference_ms": inference_ms / len(rows),
                        "total_tokens": token_audit["total_tokens"],
                        "context_truncated": token_audit["context_kept"] < token_audit["context_original"],
                        "evidence_truncated": token_audit["evidence_kept"] < token_audit["evidence_original"]})
                frame = pd.DataFrame(records_out)
                validate_prediction_frame(frame, rows, labels, config)
                path = parts / f"{i:05d}.csv"
                temporary = path.with_suffix(".partial.csv")
                frame.to_csv(temporary, index=False)
                os.replace(temporary, path)
                save_json(parts / f"{i:05d}.complete.json", {"sha256": sha256(path), "protocol_sha256": protocol_hash, "n": len(frame)})
                cached[i] = frame
                tracking.metrics(run, {"completed_examples": min((i + 1) * size, len(test))}, i + 1)
                tracking.backup()
                if i % 10 == 0 or i == len(chunks) - 1:
                    print(config, ":", min((i + 1) * size, len(test)), "/", len(test))
            predictions = pd.concat(cached, ignore_index=True)
            validate_prediction_frame(predictions, test, labels, config)
            predictions.to_csv(directory / "test_predictions.csv", index=False)
            save_json(directory / "PREDICTIONS_COMPLETE.json", {"n": len(predictions), "protocol_sha256": protocol_hash,
                "predictions_sha256": sha256(directory / "test_predictions.csv"), "latency_includes": "tokenization+host_to_device+forward+device_to_host",
                "latency_excludes": "model load, disk IO, initial warmup", "latency_unit": "batch average per example"})
            return predictions
        finally:
            if classifier is not None:
                del classifier
            gc.collect()
            if torch.cuda.is_available(): torch.cuda.empty_cache()


def calculate_metrics(frame, labels):
    report = classification_report(frame.reference, frame.pred_label, labels=labels, output_dict=True, zero_division=0)
    result = {"n": len(frame), "accuracy": float((frame.reference == frame.pred_label).mean())}
    for average in ["macro", "micro"]:
        precision, recall, f1, _ = precision_recall_fscore_support(frame.reference, frame.pred_label,
            labels=labels, average=average, zero_division=0)
        result.update({f"precision_{average}": float(precision), f"recall_{average}": float(recall), f"f1_{average}": float(f1)})
    return result, report, confusion_matrix(frame.reference, frame.pred_label, labels=labels)


def plot_confusions(matrices, labels, output):
    import matplotlib.pyplot as plt
    short = ["BG", "Gap", "Basis", "Comp", "App", "I/M", "Evid", "Origin", "FR"]
    fig, axes = plt.subplots(2, 2, figsize=(16, 13))
    for column, (config, matrix) in enumerate(matrices.items()):
        normalized = np.divide(matrix, matrix.sum(axis=1, keepdims=True), out=np.zeros_like(matrix, dtype=float),
                               where=matrix.sum(axis=1, keepdims=True) != 0)
        for row, values in enumerate([matrix, normalized]):
            ax = axes[row, column]
            ax.imshow(values, cmap="Blues", vmin=0, vmax=matrix.max() if row == 0 else 1)
            ax.set(xticks=range(9), yticks=range(9), xticklabels=short, yticklabels=short,
                   xlabel="Predicción", ylabel="Referencia humana", title=f"{config}: " + ("conteos" if row == 0 else "% por clase real"))
            for i in range(9):
                for j in range(9):
                    ax.text(j, i, str(matrix[i,j]) if row == 0 else f"{100*values[i,j]:.0f}%", ha="center", va="center",
                            fontsize=8, color="white" if values[i,j] > values.max()/2 else "black")
    legend="BG: Background · Comp: Comparison · App: Application · I/M: Improvement/Modification\nEvid: Evidence · Origin: Identification of the Originator · FR: Further Reading"
    fig.text(.5,.01,legend,ha="center",fontsize=9)
    fig.tight_layout(rect=(0,.055,1,1))
    fig.savefig(Path(output) / "test_confusion_comparison.png", dpi=180)
    plt.show(); plt.close(fig)
    # Copias individuales para la entrega común.
    for config, matrix in matrices.items():
        fig, ax = plt.subplots(figsize=(10, 8))
        ax.imshow(matrix, cmap="Blues")
        ax.set(xticks=range(9), yticks=range(9), xticklabels=short, yticklabels=short,
               xlabel="Predicción", ylabel="Referencia humana", title=config)
        for i in range(9):
            for j in range(9):ax.text(j, i, str(matrix[i,j]), ha="center", va="center", fontsize=8)
        fig.tight_layout(); fig.savefig(Path(output) / config / "test_confusion.png", dpi=160); plt.close(fig)


def build_reports(predictions, test, train, validation_results, labels, output):
    import matplotlib.pyplot as plt
    from IPython.display import display
    output = Path(output)
    results, reports, matrices, per_class = {}, {}, {}, []
    before_after = []
    for config, frame in predictions.items():
        validate_prediction_frame(frame, test, labels, config)
        result, report, matrix = calculate_metrics(frame, labels)
        results[config], reports[config], matrices[config] = result, report, matrix
        folder = output / config
        folder.mkdir(exist_ok=True)
        save_json(folder / "test_classification_report.json", report)
        pd.DataFrame(matrix, index=labels, columns=labels).to_csv(folder / "test_confusion.csv")
        normalized=np.divide(matrix,matrix.sum(axis=1,keepdims=True),out=np.zeros_like(matrix,dtype=float),
                             where=matrix.sum(axis=1,keepdims=True)!=0)
        pd.DataFrame(normalized,index=labels,columns=labels).to_csv(folder/"test_confusion_normalized.csv")
        frame.loc[frame.reference != frame.pred_label].to_csv(folder / "test_errors.csv", index=False)
        per_class.extend({"config": config, "label": label, **report[label]} for label in labels)
        cited_in_train = {r["cited_paper_id"] for r in train}
        seen = frame.cited_paper_id.isin(cited_in_train)
        group_results = {}
        for name, mask in [("seen_as_cited_in_train", seen), ("unseen_as_cited_in_train", ~seen)]:
            group_results[name] = calculate_metrics(frame.loc[mask], labels)[0] if mask.any() else {"n": 0, "f1_macro": None}
        save_json(folder / "test_cited_seen_unseen.json", group_results)
        for split, source in [("Validación interna · 125 humanas / 1.528 automáticas", validation_results[config]),
                              ("Test · referencias humanas", result)]:
            before_after.append({"config": config, "conjunto": split, **{k: source[k] for k in result}})
    comparison = pd.DataFrame([{"config": config, **r} for config, r in results.items()])
    comparison.to_csv(output / "test_comparison.csv", index=False)
    per_class = pd.DataFrame(per_class)
    per_class.to_csv(output / "test_per_class.csv", index=False)
    before_after = pd.DataFrame(before_after)
    before_after.to_csv(output / "validation_vs_test.csv", index=False)
    latency = [{"config":config,"n":len(frame),"mean_ms":float(frame.latency_ms.mean()),
                "median_ms":float(frame.latency_ms.median()),"p95_ms":float(frame.latency_ms.quantile(.95)),
                "measurement_sessions":int(frame.measurement_run_id.nunique()),
                "definition":"batch_average_per_example; not individually timed requests"}
               for config,frame in predictions.items()]
    pd.DataFrame(latency).to_csv(output/"latency_summary.csv",index=False)
    display(comparison); display(per_class); display(before_after)
    plot_confusions(matrices, labels, output)
    fig, axes = plt.subplots(1, 2, figsize=(16, 6))
    comparison.set_index("config")[["precision_macro", "recall_macro", "f1_macro"]].plot.bar(ax=axes[0], ylim=(0,1), rot=0)
    axes[0].set(title="Comparación sobre el mismo test humano", ylabel="Puntuación", xlabel="")
    per_class.pivot(index="label", columns="config", values="f1-score").reindex(labels).plot.barh(ax=axes[1], xlim=(0,1))
    axes[1].invert_yaxis(); axes[1].set(title="F1 por categoría", xlabel="F1", ylabel="")
    fig.tight_layout(); fig.savefig(output / "test_metrics_comparison.png", dpi=160); plt.show(); plt.close(fig)
    fig, ax = plt.subplots(figsize=(11,5))
    before_after.pivot(index="config", columns="conjunto", values="f1_macro").plot.bar(ax=ax, ylim=(0,1), rot=0)
    ax.set(title="Validación interna frente a test humano · mismos modelos, distintos conjuntos", ylabel="F1 macro", xlabel="")
    fig.tight_layout(); fig.savefig(output / "validation_vs_test.png", dpi=160); plt.show(); plt.close(fig)
    print("La diferencia entre conjuntos no demuestra una mejora o deterioro del modelo: cambian las citas y sus referencias.")
    return results, reports


def macro_from_cm(cm):
    cm = np.asarray(cm, dtype=float)
    tp = np.diagonal(cm, axis1=-2, axis2=-1)
    denominator = cm.sum(axis=-1) + cm.sum(axis=-2)
    return np.divide(2*tp, denominator, out=np.zeros_like(tp), where=denominator != 0).mean(axis=-1)


def paired_bootstrap(base, top3, labels, repetitions=2000, seed=20261113):
    keys = ["inst_key", "citing_paper_id", "reference"]
    if len(base) == 0 or not base[keys].equals(top3[keys]) or base.inst_key.duplicated().any():
        raise ValueError("El bootstrap requiere las mismas instancias y referencias, en el mismo orden.")
    if repetitions < 100:
        raise ValueError("Se requieren al menos 100 remuestreos.")
    groups, inverse = np.unique(base.citing_paper_id.to_numpy(), return_inverse=True)
    label_ids = {label: i for i, label in enumerate(labels)}
    true = base.reference.map(label_ids).to_numpy()
    if pd.isna(true).any(): raise ValueError("Referencia desconocida.")
    matrices = []
    for frame in [base, top3]:
        pred = frame.pred_label.map(label_ids).to_numpy()
        if pd.isna(pred).any(): raise ValueError("Predicción desconocida.")
        cm = np.zeros((len(groups), len(labels), len(labels)), dtype=np.int64)
        np.add.at(cm, (inverse, true, pred), 1)
        matrices.append(cm)
    rng, deltas = np.random.default_rng(seed), []
    for _ in range(repetitions):
        counts = rng.multinomial(len(groups), np.full(len(groups), 1/len(groups)))
        sampled = [np.tensordot(counts, cm, axes=(0,0)) for cm in matrices]
        deltas.append(float(macro_from_cm(sampled[1]) - macro_from_cm(sampled[0])))
    lo, hi = np.quantile(deltas, [.025,.975])
    return {"difference": "Top-3 minus base", "metric":"f1_macro", "delta":float(macro_from_cm(matrices[1].sum(0))-macro_from_cm(matrices[0].sum(0))),
        "ci95_percentile":[float(lo),float(hi)], "bootstrap_unit":"citing_paper_id", "n_groups":len(groups),
        "n_instances":len(base), "repetitions":repetitions, "seed":seed, "fixed_labels":labels}, np.asarray(deltas)


def show_paired_and_errors(predictions, labels, texts, output, repetitions=2000, seed=20261113):
    import matplotlib.pyplot as plt
    from IPython.display import display
    result, deltas = paired_bootstrap(predictions["base"], predictions["fragmentos"], labels, repetitions, seed)
    save_json(Path(output) / "paired_test_comparison.json", result)
    pd.DataFrame({"delta_f1_macro":deltas}).to_csv(Path(output) / "bootstrap_deltas.csv", index=False)
    fig, ax = plt.subplots(figsize=(9,4))
    ax.hist(100*deltas, bins=40, color="#16877c")
    ax.axvline(0, color="black", linestyle="--")
    for endpoint in result["ci95_percentile"]:ax.axvline(100*endpoint,color="#c76c35")
    ax.set(title="Diferencia Top-3 − base · bootstrap por artículo citante", xlabel="Diferencia de F1 macro (puntos porcentuales)",ylabel="Remuestreos")
    fig.tight_layout(); fig.savefig(Path(output)/"paired_test_comparison.png",dpi=160); plt.show(); plt.close(fig)
    merged = predictions["base"][["inst_key","reference","pred_label"]].rename(columns={"pred_label":"base_prediction"}).merge(
        predictions["fragmentos"][["inst_key","pred_label"]].rename(columns={"pred_label":"top3_prediction"}),on="inst_key",validate="one_to_one")
    merged["disagree"] = merged.base_prediction != merged.top3_prediction
    errors = merged.loc[(merged.reference != merged.base_prediction) | (merged.reference != merged.top3_prediction)]
    counts = collections.Counter((r.reference,p) for r in errors.itertuples() for p in [r.base_prediction,r.top3_prediction] if p != r.reference)
    chosen = []
    for (reference,predicted),count in sorted(counts.items(),key=lambda item:(-item[1],item[0])):
        candidates = errors.loc[(errors.reference==reference)&((errors.base_prediction==predicted)|(errors.top3_prediction==predicted))].sort_values("inst_key")
        for row in candidates.to_dict("records"):
            if row["inst_key"] not in {r["inst_key"] for r in chosen}:
                chosen.append({**row,"frequent_confusion":f"{reference} → {predicted}","confusion_count_across_models":count,
                    "context_excerpt":texts[row["inst_key"]]["context"][:400]})
                break
        if len(chosen)==2:break
    save_json(Path(output)/"error_examples.json",chosen)
    pd.DataFrame(chosen).to_csv(Path(output)/"error_examples.csv",index=False)
    display(pd.DataFrame(chosen)); display(pd.DataFrame([result]))
    print("Los ejemplos muestran errores reales frecuentes. Sus causas requieren lectura; no se asignan explicaciones automáticas.")
    return result


def final_conclusions(results, reports, paired, validation_results):
    base, top = results["base"], results["fragmentos"]
    lo, hi = (100*v for v in paired["ci95_percentile"])
    if lo > 0: interpretation="El intervalo favorece a Top-3 en este test."
    elif hi < 0: interpretation="El intervalo favorece a base en este test."
    else: interpretation="El intervalo incluye cero; no establece una ventaja clara de una entrada sobre la otra."
    first=(f"Evaluamos los dos modelos congelados sobre **{base['n']:,} citas con referencia humana**. "
        f"Base obtuvo F1 macro **{base['f1_macro']:.4f}** y micro **{base['f1_micro']:.4f}**; "
        f"Top-3 obtuvo **{top['f1_macro']:.4f}** y **{top['f1_micro']:.4f}**, respectivamente. "
        f"La diferencia Top-3 − base fue **{100*paired['delta']:+.2f} puntos porcentuales**, con IC 95 % "
        f"por bootstrap pareado por artículo citante **[{lo:+.2f}; {hi:+.2f}]**. {interpretation}")
    label="Improvement/Modification"
    second=(f"En {label}, con {int(reports['base'][label]['support'])} ejemplos de test, "
        f"el F1 fue **{reports['base'][label]['f1-score']:.4f}** para base y **{reports['fragmentos'][label]['f1-score']:.4f}** "
        "para Top-3. Las matrices y los reportes permiten distinguir las confusiones por categoría. "
        "Esta clase tuvo solo 140 ejemplos de entrenamiento; su resultado no elimina la limitación de representación.")
    third=(f"Los mismos modelos habían obtenido F1 macro de validación interna "
        f"{validation_results['base']['f1_macro']:.4f} y {validation_results['fragmentos']['f1_macro']:.4f}. "
        "Esa validación tenía 125 etiquetas humanas y 1.528 automáticas: la diferencia con el test no demuestra "
        "por sí sola una mejora o deterioro. Conservamos los modelos, el recorte a 512 tokens y la separación por documento; "
        "el test no se utilizó para ajustar parámetros. Los resultados se limitan al conjunto evaluado y sus criterios de selección.")
    return "\n\n".join([first,second,third])+"\n"
