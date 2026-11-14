"""Preparación, búsqueda y reportes de la versión final de SciBERT.

Las dependencias de entrenamiento se importan en el notebook; las funciones de
datos y selección también se pueden verificar sin una sesión de entrenamiento.
"""
import collections
import gc
import hashlib
import importlib.util
import itertools
import json
import math
import os
from pathlib import Path
import re
import shutil
import sys
import time
import uuid

import numpy as np
import pandas as pd
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix, f1_score


def save_json(path, value):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    temp = path.with_name(path.name + ".partial_" + uuid.uuid4().hex)
    temp.write_text(json.dumps(value, indent=2, ensure_ascii=False, allow_nan=False, default=str) + "\n", encoding="utf-8")
    os.replace(temp, path)


def freeze_json(path, value):
    path = Path(path)
    if path.exists() and json.loads(path.read_text(encoding="utf-8")) != value:
        raise ValueError(f"La configuración guardada es distinta: {path.name}. Usa otro RUN_ID.")
    save_json(path, value)


def sha256(path):
    h = hashlib.sha256()
    with Path(path).open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()


def tree_hashes(directory):
    directory = Path(directory)
    return {p.relative_to(directory).as_posix(): sha256(p) for p in sorted(directory.rglob("*")) if p.is_file()}


def verify_files(directory, hashes):
    directory = Path(directory).resolve()
    if not hashes:
        raise ValueError("El cierre no contiene archivos verificables.")
    for name, expected in hashes.items():
        path = (directory / name).resolve()
        if not path.is_relative_to(directory) or not path.is_file() or sha256(path) != expected:
            raise ValueError(f"Archivo guardado ausente o modificado: {name}")


def prepare_final_data(ids_dir, a3_dir, old_ids_dir, output, labels, training_hash, a3_hash,
                       split_seed="G15-A4-split-v1", validation_fraction=.10):
    output = Path(output)
    output.mkdir(parents=True, exist_ok=True)
    manifest, raw, gold, test_ids, hashes, closure = load_a3_release(
        ids_dir, a3_dir, old_ids_dir, labels, training_hash, a3_hash)
    rules = release_rules(read_records(Path(ids_dir) / "exclusion_list_G15_V2_v2.jsonl"))
    eligible = [dict(r) for r in raw if not release_excluded(r, rules)]
    labeled, unclear, corrected = attach_ta_gold(eligible, gold, labels)

    def validation_citing(citing):
        digest = hashlib.sha256(f"{split_seed}|val|{citing}".encode()).hexdigest()
        return int(digest[:16], 16) / 2**64 < validation_fraction

    validation = [r for r in labeled if validation_citing(r["citing_paper_id"])]
    candidates = [r for r in labeled if not validation_citing(r["citing_paper_id"])]
    val_docs = document_set(validation)
    train = [r for r in candidates if not {r["citing_paper_id"], r["cited_paper_id"]} & val_docs]
    audit_release_splits(train, validation, test_ids)
    splits = {"train": train, "validation": validation}
    counts = pd.DataFrame({k: collections.Counter(r["label"] for r in rows) for k, rows in splits.items()}).reindex(labels).fillna(0).astype(int)
    if counts.eq(0).any().any():
        raise ValueError("Cada clase debe estar representada en entrenamiento y validación.")
    if any(r.get("gold_set") == "B" or r.get("test_set") == "B" and r.get("sample_status") == "active"
           for rows in splits.values() for r in rows):
        raise ValueError("Una cita de la prueba propia intentó entrar al aprendizaje.")
    fields = ["inst_key", "group_key", "citing_paper_id", "cited_paper_id", "label", "label_source", "source_batch"]
    split_hashes = {}
    for name, rows in splits.items():
        rows.sort(key=lambda r: r["inst_key"])
        content = "".join(json.dumps({k: r[k] for k in fields}, ensure_ascii=False, sort_keys=True) + "\n" for r in rows)
        split_hashes[name] = hashlib.sha256(content.encode()).hexdigest()
        path = output / f"split_{name}_ids.jsonl"
        if path.exists() and path.read_text(encoding="utf-8") != content:
            raise ValueError("Las particiones cambiaron. Usa otro RUN_ID.")
        path.write_text(content, encoding="utf-8")
    source_counts = pd.DataFrame({k: collections.Counter(r["label_source"] for r in rows) for k, rows in splits.items()}).fillna(0).astype(int)
    counts.to_csv(output / "split_class_counts.csv")
    source_counts.to_csv(output / "split_label_sources.csv")
    summary = {"dataset_release": "training_v2", "isolation": "V2", "raw_rows": len(raw),
        "rows_after_exclusions": len(eligible), "removed_unclear": len(unclear),
        "corrected_prelabels": corrected, "removed_for_validation_isolation": len(candidates)-len(train),
        "rows": {k: len(v) for k, v in splits.items()}, "split_hashes": split_hashes,
        "input_hashes": hashes, "label_sources": source_counts.to_dict(),
        "split_seed": split_seed, "validation_fraction_target": validation_fraction,
        "temporal_split": False, "section_stratification": False, "test_scored": False,
        "contract_url": "https://drive.google.com/file/d/1X7JXN5ZvoYJodhRxdT5Y-8wOaDlXwRXi/view",
        "release_readme_url": "https://drive.google.com/file/d/1m55jsSkHlb-MlCTJKgy36X4EIK8x23GN/view"}
    freeze_json(output / "data_manifest.json", summary)
    save_json(output / "label_provenance.json", {"human_source_set": "A", "own_test_set": "B",
        "rule": "join by inst_key; replace eligible prelabels with final gold; never append own test",
        "source_counts": source_counts.to_dict(), "corrected_prelabels": corrected,
        "removed_unclear_keys": unclear})
    save_json(output / "a3_closure.json", closure)
    return splits, test_ids, hashes, split_hashes, counts, source_counts, summary


def show_final_data(counts, source_counts, output):
    import matplotlib.pyplot as plt
    totals = counts.sum(axis=1)
    fig, (pie, bars) = plt.subplots(1, 2, figsize=(17, 6))
    wedges, _, _ = pie.pie(totals, startangle=90, autopct=lambda p: f"{p:.1f}%" if p >= 3 else "",
        pctdistance=.78, colors=plt.get_cmap("tab10")(np.arange(len(totals))),
        wedgeprops={"width": .42, "edgecolor": "white"})
    pie.text(0, 0, f"{int(totals.sum()):,}\nejemplos", ha="center", va="center", fontsize=15)
    pie.set_title("Nuestros datos de entrenamiento y validación")
    pie.legend(wedges, [f"{k}: {v:,} ({v/totals.sum():.1%})" for k, v in totals.items()],
        loc="upper center", bbox_to_anchor=(.5, -.02), fontsize=8, ncol=2)
    counts.rename(columns={"train":"Entrenamiento", "validation":"Validación"}).plot.barh(ax=bars, color=["#16877c", "#8fa6be"])
    bars.invert_yaxis()
    for container in bars.containers:
        bars.bar_label(container, fmt="%.0f", padding=3, fontsize=8)
    bars.set(xlabel="Ejemplos", ylabel="", title="Distribución por clase")
    bars.set_xlim(0, int(counts.train.max())*1.22)
    fig.tight_layout()
    fig.savefig(Path(output)/"eda_class_distribution.png", dpi=160, bbox_inches="tight")
    plt.show()
    plt.close(fig)
    display(counts.rename(columns={"train":"Entrenamiento", "validation":"Validación"}))
    display(source_counts.rename(index={"pre_label":"Etiqueta automática", "human_gold":"Etiqueta humana"},
        columns={"train":"Entrenamiento", "validation":"Validación"}))
    print(f"Usamos {int(counts.train.sum()):,} ejemplos para entrenar y {int(counts.validation.sum()):,} para validar.")
    print(f"La clase más frecuente es {totals.idxmax()} ({totals.max()/totals.sum():.1%}); la menos frecuente es {totals.idxmin()} ({int(totals.min()):,} ejemplos).")


def trial_id(spec):
    def number(value):
        return format(float(value), ".8g").replace("-", "m").replace(".", "p").replace("+", "")
    return f"{spec['stage']}_{spec['input_variant']}_lr{number(spec['learning_rate'])}_wd{number(spec['weight_decay'])}_s{spec['seed']}"


def grid_plan(configs, learning_rates, weight_decays, seed, max_epochs):
    result = [{"stage":"grid", "input_variant":c, "learning_rate":float(lr), "weight_decay":float(wd),
        "seed":int(seed), "max_epochs":int(max_epochs)} for c, lr, wd in itertools.product(configs, learning_rates, weight_decays)]
    ids = [trial_id(s) for s in result]
    if not result or len(set(ids)) != len(ids):
        raise ValueError("La búsqueda contiene combinaciones vacías o repetidas.")
    if any(s["learning_rate"] <= 0 or s["weight_decay"] < 0 or s["max_epochs"] < 1 for s in result):
        raise ValueError("Los parámetros de la búsqueda no son válidos.")
    return result


def select_winners(results, plan):
    expected = {trial_id(s) for s in plan}
    if len(results) != len(expected) or {r["trial_id"] for r in results} != expected:
        raise ValueError("La selección requiere todos los ensayos de la búsqueda, sin duplicados.")
    if any(r["stage"] != "grid" or r["evaluation_policy"] != "v2_fp32" or not math.isfinite(r["f1_macro"]) for r in results):
        raise ValueError("La selección requiere resultados FP32 válidos de la búsqueda.")
    specs = {trial_id(s): s for s in plan}
    for r in results:
        s = specs[r["trial_id"]]
        if any(r[k] != s[k] for k in s):
            raise ValueError("El resultado no corresponde a la combinación declarada.")
    # Desempate fijado antes de entrenar: menor LR, menor regularización e ID.
    return {c: min((r for r in results if r["input_variant"] == c),
            key=lambda r:(-r["f1_macro"],r["learning_rate"],r["weight_decay"],r["trial_id"]))
            for c in sorted({s["input_variant"] for s in plan})}


def repetition_plan(winners, seeds, primary_seed=42):
    seeds = list(map(int, seeds))
    if len(seeds) != len(set(seeds)) or primary_seed not in seeds:
        raise ValueError("Las semillas deben ser únicas e incluir la semilla principal.")
    return [{"stage":"repeticion", "input_variant":c, "learning_rate":r["learning_rate"],
        "weight_decay":r["weight_decay"], "seed":s, "max_epochs":r["max_epochs"]}
        for c,r in sorted(winners.items()) for s in seeds if s != primary_seed]


def stability_table(winners, repeated, seeds, primary_seed=42):
    all_rows = [*winners.values(), *repeated]
    for config in winners:
        rows = [r for r in all_rows if r["input_variant"] == config]
        if len(rows) != len(seeds) or {r["seed"] for r in rows} != set(seeds):
            raise ValueError("Faltan repeticiones o hay una semilla duplicada.")
        w = winners[config]
        if w["seed"] != primary_seed or any(r["evaluation_policy"] != "v2_fp32" or
            any(r[k] != w[k] for k in ["learning_rate","weight_decay","max_epochs"]) for r in rows):
            raise ValueError("Las repeticiones deben conservar los ajustes seleccionados.")
    frame = pd.DataFrame(all_rows)
    return frame.groupby("input_variant").agg(n=("f1_macro","size"),mean_f1=("f1_macro","mean"),
        std_f1=("f1_macro","std"),min_f1=("f1_macro","min"),max_f1=("f1_macro","max"))


def completed_trial(workdir, spec):
    workdir = Path(workdir)
    stored = workdir / "trial_spec.json"
    if stored.exists() and json.loads(stored.read_text()) != spec:
        raise ValueError("Los ajustes de un ensayo existente cambiaron.")
    train_marker = workdir / "TRAINING_COMPLETE.json"
    if train_marker.exists():
        verify_files(workdir/"model", json.loads(train_marker.read_text())["model_hashes"])
    marker = workdir / "EVALUATION_COMPLETE.json"
    if not marker.exists():
        return None
    if not train_marker.exists():
        raise ValueError("Hay una evaluación sin un modelo verificado.")
    verify_files(workdir/"evaluation", json.loads(marker.read_text())["files"])
    result = json.loads((workdir/"evaluation/result.json").read_text())
    if (result["trial_id"] != workdir.name or result["model_marker_sha256"] != sha256(train_marker)
            or any(result.get(k) != v for k,v in spec["trial"].items())):
        raise ValueError("El cierre de evaluación no corresponde al ensayo.")
    return result


def load_trial_export(model_dir):
    module_spec = importlib.util.spec_from_file_location("scibert_inference_"+uuid.uuid4().hex, Path(model_dir)/"inference.py")
    module = importlib.util.module_from_spec(module_spec)
    previous = sys.dont_write_bytecode
    try:
        sys.dont_write_bytecode = True
        module_spec.loader.exec_module(module)
    finally:
        sys.dont_write_bytecode = previous
    return module.CitationClassifier(model_dir)


def run_final_trial(trial):
    name = trial_id(trial)
    workdir = OUTPUT_ROOT/"trials"/name
    workdir.mkdir(parents=True,exist_ok=True)
    spec = {"study":STUDY_SPEC,"trial":trial}
    freeze_json(workdir/"trial_spec.json",spec)
    previous = completed_trial(workdir,spec)
    if previous is not None:
        parent = tracking.parent(name)
        tracking.client.set_tag(parent,"input_variant",trial["input_variant"])
        tracking.client.set_tag(parent,"stage",trial["stage"])
        tracking.client.set_tag(parent,"export_check","passed_full_validation")
        tracking.metrics(parent,{f"validation_fp32_{k}":v for k,v in previous.items()})
        tracking.client.log_artifacts(parent,str(workdir/"evaluation"),artifact_path="validation")
        tracking.reports(name)
        tracking.client.set_terminated(parent,"FINISHED")
        print(name, "comprobado; resultado recuperado.")
        return previous
    checkpoint_dir = workdir/"checkpoints"
    trained = workdir/"TRAINING_COMPLETE.json"
    last = verified_checkpoint(checkpoint_dir) if not trained.exists() and checkpoint_dir.exists() else None
    params = {"study_id":RUN_ID,"input_variant":trial["input_variant"],"stage":trial["stage"],
        "learning_rate":trial["learning_rate"],"weight_decay":trial["weight_decay"],
        "seed":trial["seed"],"max_epochs":trial["max_epochs"],"early_stopping_patience":PATIENCE,
        "train_batch":TRAIN_BATCH,"gradient_accumulation":GRAD_ACCUM,"max_length":MAX_LENGTH,
        "evaluation_policy":"v2_fp32","isolation":"V2","dataset_release":"training_v2","test_scored":False}
    with tracking.attempt(name,params,last) as attempt_id:
        parent = tracking.parent(name)
        for k in ["input_variant","stage"]:
            tracking.client.set_tag(parent,k,trial[k])
        tracking.client.set_tag(parent,"trial_drive",str(workdir))
        if not trained.exists():
            set_seed(trial["seed"])
            model = AutoModelForSequenceClassification.from_pretrained(MODEL_ID,revision=MODEL_REVISION,
                token=False,num_labels=len(LABELS),id2label=ID2LABEL,label2id=LABEL2ID,
                problem_type="single_label_classification",attn_implementation="eager")
            model.resize_token_embeddings(len(tokenizer),mean_resizing=False)
            args = TrainingArguments(output_dir=str(checkpoint_dir),num_train_epochs=trial["max_epochs"],
                learning_rate=trial["learning_rate"],weight_decay=trial["weight_decay"],
                per_device_train_batch_size=TRAIN_BATCH,gradient_accumulation_steps=GRAD_ACCUM,
                per_device_eval_batch_size=EVAL_BATCH,warmup_ratio=.1,lr_scheduler_type="linear",
                eval_strategy="epoch",save_strategy="epoch",logging_strategy="steps",logging_steps=50,
                load_best_model_at_end=True,metric_for_best_model="f1_macro",greater_is_better=True,
                save_total_limit=2,save_safetensors=True,seed=trial["seed"],data_seed=trial["seed"],
                restore_callback_states_from_checkpoint=True,bf16=USE_BF16,fp16=False,tf32=False,
                full_determinism=True,dataloader_num_workers=0,dataloader_pin_memory=True,
                optim="adamw_torch",report_to="none",push_to_hub=False)
            trainer = Trainer(model=model,args=args,train_dataset=encoded[trial["input_variant"]]["train"],
                eval_dataset=encoded[trial["input_variant"]]["validation"],processing_class=tokenizer,
                data_collator=DataCollatorWithPadding(tokenizer,pad_to_multiple_of=8),compute_metrics=compute_metrics,
                callbacks=[EarlyStoppingCallback(early_stopping_patience=PATIENCE),A4MLflowCallback(tracking,attempt_id)])
            torch.cuda.reset_peak_memory_stats()
            started = time.perf_counter()
            trained_result = trainer.train(resume_from_checkpoint=last)
            torch.cuda.synchronize()
            elapsed = time.perf_counter()-started
            checkpoint = trainer.state.best_model_checkpoint
            best_epoch = json.loads((Path(checkpoint)/"trainer_state.json").read_text())["epoch"]
            model_dir = workdir/"model"
            trainer.save_model(str(model_dir))
            tokenizer.save_pretrained(model_dir)
            save_json(model_dir/"input_policy.json",{"config":trial["input_variant"],"max_length":MAX_LENGTH,
                "context_budget":CONTEXT_BUDGET,"markers":MARKERS,"model_revision":MODEL_REVISION,"score_calibrated":False})
            save_json(model_dir/"label_mapping.json",{"label2id":LABEL2ID,"id2label":ID2LABEL})
            save_json(model_dir/"run_manifest.json",spec)
            (model_dir/"inference.py").write_text(INFERENCE_TEMPLATE.replace("__ENCODER__",ENCODER_SOURCE),encoding="utf-8")
            save_json(model_dir/"api_contract.json",{"input_variant":trial["input_variant"],
                "required_input":["context","title","abstract"] if trial["input_variant"]=="base" else ["context","chunks: 3 objetos {text, section}"],
                "context_target":"Un marcador [[TARGET]]", "output":"Una clase y nueve probabilidades sin calibrar"})
            metadata = {"best_checkpoint":checkpoint,"best_epoch":best_epoch,
                "epochs_completed":trainer.state.epoch,"best_trainer_f1":trainer.state.best_metric,
                "elapsed_session_seconds":elapsed,"peak_gpu_allocated_gib":torch.cuda.max_memory_allocated()/2**30,
                "train_metrics":trained_result.metrics}
            save_json(workdir/"training_metrics.json",metadata)
            save_json(workdir/"training_log.json",trainer.state.log_history)
            save_json(trained,{"model_hashes":tree_hashes(model_dir),"attempt_id":attempt_id})
            del trainer,model
            gc.collect()
            torch.cuda.empty_cache()
        result = evaluate_final_trial(trial,workdir,attempt_id)
        tracking.client.log_artifacts(attempt_id,str(workdir/"evaluation"),artifact_path="validation")
        tracking.client.log_artifact(attempt_id,str(workdir/"trial_spec.json"),artifact_path="provenance")
        tracking.client.set_tag(parent,"model_drive",str(workdir/"model"))
        return result


def evaluate_final_trial(trial, workdir, attempt_id):
    import matplotlib.pyplot as plt
    workdir = Path(workdir)
    directory = workdir/"evaluation"
    directory.mkdir(exist_ok=True)
    train_info = json.loads((workdir/"training_metrics.json").read_text())
    clf = load_trial_export(workdir/"model")
    try:
        data = encoded[trial["input_variant"]]["validation"]
        sample = clf.predict(texts[val_rows[0]["inst_key"]])
        one = predict_export_fp32(clf,data.select([0]),EVAL_BATCH)[0]
        if not np.allclose(one,[sample["scores"][k] for k in LABELS],atol=2e-5):
            raise ValueError("La preparación de entradas exportada difiere del entrenamiento.")
        probs,replay,audit = audit_export(clf,data,[r["inst_key"] for r in val_rows],train_info["best_checkpoint"],
            directory,EVAL_BATCH,trial["seed"],"bf16" if USE_BF16 else "fp32")
        if audit["export_check"] != "passed_full_validation":
            raise ValueError("La evaluación requiere un checkpoint verificable.")
        y = np.asarray([LABEL2ID[r["label"]] for r in val_rows])
        predicted = probs.argmax(-1)
        report = classification_report(y,predicted,labels=list(ID2LABEL),target_names=LABELS,output_dict=True,zero_division=0)
        result = {**trial,"trial_id":workdir.name,"evaluation_policy":"v2_fp32","n":len(y),
            **probability_metrics(y,probs),"precision_micro":float(accuracy_score(y,predicted)),
            "recall_micro":float(accuracy_score(y,predicted)),"best_epoch":train_info["best_epoch"],
            "epochs_completed":train_info["epochs_completed"],"elapsed_session_seconds":train_info["elapsed_session_seconds"],
            "peak_gpu_allocated_gib":train_info["peak_gpu_allocated_gib"],"model_dir":str(workdir/"model"),
            "model_marker_sha256":sha256(workdir/"TRAINING_COMPLETE.json")}
        audit.update(split_hashes=split_hashes,trial_id=workdir.name,label_sources=dict(collections.Counter(r["label_source"] for r in val_rows)))
        save_json(directory/"export_precision_audit.json",audit)
        save_json(directory/"classification_report.json",report)
        per_class = pd.DataFrame([{"label":label,**report[label]} for label in LABELS])
        per_class.to_csv(directory/"per_class.csv",index=False)
        predictions = pd.DataFrame({"inst_key":[r["inst_key"] for r in val_rows],"reference":[r["label"] for r in val_rows],
            "label_source":[r["label_source"] for r in val_rows],"predicted_label":[ID2LABEL[int(i)] for i in predicted]})
        for i,label in ID2LABEL.items():
            predictions[f"p_{label}"] = probs[:,i]
        predictions.to_csv(directory/"predictions.csv",index=False)
        predictions.loc[predictions.reference!=predictions.predicted_label].to_csv(directory/"errors.csv",index=False)
        cm = confusion_matrix(y,predicted,labels=list(ID2LABEL))
        pd.DataFrame(cm,index=LABELS,columns=LABELS).to_csv(directory/"confusion.csv")
        fig,ax=plt.subplots(figsize=(8,7))
        ax.imshow(cm,cmap="Blues")
        short=["BG","Gap","Basis","Comp","App","I/M","Evid","Origin","FR"]
        ax.set(xticks=range(9),yticks=range(9),xticklabels=short,yticklabels=short,
            xlabel="Predicción",ylabel="Referencia",title=workdir.name)
        for i in range(9):
            for j in range(9):
                ax.text(j,i,str(cm[i,j]),ha="center",va="center",fontsize=8,color="white" if cm[i,j]>cm.max()/2 else "black")
        fig.tight_layout()
        fig.savefig(directory/"confusion.png",dpi=150)
        plt.close(fig)
        save_json(directory/"result.json",result)
        for rid in [attempt_id,tracking.parent(workdir.name)]:
            tracking.metrics(rid,{f"validation_fp32_{k}":v for k,v in result.items()})
            tracking.metrics(rid,{"precision_label_disagreements":audit["trainer_vs_export_fp32"]["label_disagreements"]})
            tracking.client.set_tag(rid,"export_check",audit["export_check"])
            for index,label in ID2LABEL.items():
                tracking.metrics(rid,{f"validation/class_{index}/{k}":v for k,v in report[label].items()})
        save_json(workdir/"EVALUATION_COMPLETE.json",{"files":tree_hashes(directory)})
        print(workdir.name, f"F1 macro: {result['f1_macro']:.6f}")
        return result
    finally:
        del clf
        gc.collect()
        torch.cuda.empty_cache()


def run_final_plan(plan, filename):
    results=[]
    for number,spec in enumerate(plan,1):
        print(f"Ensayo {number}/{len(plan)}: {trial_id(spec)}")
        results.append(run_final_trial(spec))
        pd.DataFrame(results).to_csv(OUTPUT_ROOT/filename,index=False)
    tracking.backup(force=True)
    return results


def final_conclusions(winners, stability, counts, token_audit, per_class_reports, grid_size):
    base,top = winners["base"],winners["fragmentos"]
    delta=(top["f1_macro"]-base["f1_macro"])*100
    relation="por encima" if delta>0 else "por debajo" if delta<0 else "al mismo nivel"
    im="Improvement/Modification"
    truncated=float(token_audit.loc[(token_audit.config=="fragmentos")&(token_audit.split=="validation"),"evidence_truncated"].mean())*100
    support = int(counts.loc[im,'validation'])
    im_scores="; ".join(f"{'base' if c=='base' else 'Top-3'}: {round(per_class_reports[c][im]['recall']*support)}/{support} citas recuperadas" for c in ["base","fragmentos"])
    seed_text="; ".join(f"{c}: {r.mean_f1:.4f} ± {r.std_f1:.4f}" for c,r in stability.iterrows())
    return f'''## Conclusiones

Entrenamos con {int(counts.train.sum()):,} ejemplos y validamos con {int(counts.validation.sum()):,}. Comparamos {grid_size} combinaciones y añadimos {int(stability.n.sum())-len(winners)} entrenamientos para medir la variación entre semillas. En la evaluación FP32, base obtuvo **F1 macro {base['f1_macro']:.4f}** y Top-3 **{top['f1_macro']:.4f}**: Top-3 quedó {abs(delta):.2f} puntos porcentuales {relation} de base. Los ajustes elegidos fueron ritmo {base['learning_rate']:g} y regularización {base['weight_decay']:g} para base; ritmo {top['learning_rate']:g} y regularización {top['weight_decay']:g} para Top-3.

Con {int(stability.n.iloc[0])} semillas, el F1 macro medio y su desviación fueron **{seed_text}**. La clase Improvement/Modification contó con {int(counts.loc[im,'train'])} ejemplos de entrenamiento y {support} de validación; {im_scores}. Ese soporte reducido limita cuánto podemos generalizar el resultado de esta clase.

Top-3 recortó texto en el **{truncated:.2f}%** de los ejemplos de validación. Ese dato describe la información que llegó al modelo; por sí solo no demuestra la causa de la diferencia de desempeño. Los modelos principales conservan la semilla 42 y quedaron guardados con sus reportes y verificaciones. Todas estas cifras corresponden a validación interna; el conjunto humano de test permanece separado del entrenamiento y de la selección de parámetros.
'''
