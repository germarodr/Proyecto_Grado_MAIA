"""Comparación controlada de un fragmento con los tres de la primera iteración."""
import json
import math
from pathlib import Path

import numpy as np
import pandas as pd


def encode_top1(example, config, tok, max_length=512, context_budget=192):
    if config != "top1":
        return encode_example_reference(example, config, tok, max_length, context_budget)
    chunks = list(example.get("chunks", []))
    if not chunks:
        raise ValueError("La entrada necesita al menos el primer fragmento recuperado.")
    selected = dict(example, chunks=chunks[:1])
    features, stats = encode_example_reference(selected, "fragmentos", tok, max_length, context_budget)
    _, available = encode_example_reference(example, "fragmentos", tok, max_length, context_budget)
    stats.update(selected_chunks=1, available_chunks=len(chunks), omitted_chunks=len(chunks)-1,
        available_evidence_tokens=available["evidence_original"],
        omitted_evidence_tokens=available["evidence_original"]-stats["evidence_original"],
        retained_fraction_of_available=stats["evidence_kept"]/max(1, available["evidence_original"]))
    return features, stats


def top1_plan(seeds, parameters):
    if len(seeds)!=3 or len(set(seeds))!=3 or 42 not in seeds:
        raise ValueError("Usamos tres semillas distintas y conservamos 42 como principal.")
    if parameters["learning_rate"]<=0 or parameters["weight_decay"]<0 or parameters["max_epochs"]<1:
        raise ValueError("Los parámetros fijados no son válidos.")
    return [{"stage":"top1","input_variant":"top1","seed":int(seed),**parameters} for seed in seeds]


def acquire_tracking_writer(root):
    import fcntl
    import os
    state = globals().get("_TOP1_WRITER_LOCK")
    if state is not None and not state.closed:
        return state
    root = Path(root)
    root.mkdir(parents=True,exist_ok=True)
    handle = (root/"writer.lock").open("a+")
    try:
        fcntl.flock(handle,fcntl.LOCK_EX|fcntl.LOCK_NB)
    except BlockingIOError:
        handle.close()
        raise RuntimeError("Otra sesión conserva la escritura del historial. Recupera esa ejecución antes de continuar.")
    handle.seek(0)
    handle.truncate()
    handle.write(str(os.getpid()))
    handle.flush()
    globals()["_TOP1_WRITER_LOCK"] = handle
    return handle


def release_tracking_writer():
    import fcntl
    handle = globals().get("_TOP1_WRITER_LOCK")
    if handle is not None and not handle.closed:
        fcntl.flock(handle,fcntl.LOCK_UN)
        handle.close()
    globals()["_TOP1_WRITER_LOCK"] = None


def load_top3_reference(root, current_spec, seeds, reference_encoder_sha256):
    root = Path(root)
    release = json.loads((root/"study_manifest.json").read_text(encoding="utf-8"))
    complete = json.loads((root/"STUDY_COMPLETE.json").read_text(encoding="utf-8"))
    if release["study_id"] != "g15_scibert_final_v2_grid_01" or complete["study_id"] != release["study_id"]:
        raise ValueError("La referencia no corresponde a la primera iteración.")
    if complete["grid_trials"] != 12 or complete["additional_seed_trials"] != 4 or complete["test_scored"] is not False:
        raise ValueError("La referencia necesita su cierre completo y el test separado.")
    for key in ["model_id", "model_revision", "input_hashes", "split_hashes", "label_mapping",
                "train_batch", "gradient_accumulation", "eval_batch", "warmup_ratio", "lr_scheduler",
                "loss", "precision", "checkpoint_selection", "canonical_evaluation", "early_stopping_patience"]:
        if release[key] != current_spec[key]:
            raise ValueError(f"La comparación cambió {key}; requiere otra referencia.")
    if release["token_policy"]["encoder_sha256"] != reference_encoder_sha256:
        raise ValueError("La preparación de Top-3 difiere de la referencia prevista.")
    for key in ["max_length", "context_budget", "title_budget", "section_budget"]:
        if release["token_policy"][key] != current_spec["token_policy"][key]:
            raise ValueError("Los presupuestos de texto no coinciden.")
    verify_files(root, complete["report_hashes"])
    selected = json.loads((root/"selected_grid_trials.json").read_text(encoding="utf-8"))["fragmentos"]
    if selected["trial_id"] != "grid_fragmentos_lr3em05_wd0p01_s42":
        raise ValueError("Cambió el modelo Top-3 fijado en la primera iteración.")
    repeated = json.loads((root/"repetition_plan.json").read_text(encoding="utf-8"))
    plan = [{k:selected[k] for k in ["stage","input_variant","learning_rate","weight_decay","seed","max_epochs"]}]
    plan += [p for p in repeated if p["input_variant"] == "fragmentos"]
    if len(plan) != len(seeds) or {p["seed"] for p in plan} != set(seeds):
        raise ValueError("La referencia no contiene exactamente las tres semillas requeridas.")
    rows, markers = [], {}
    for trial in plan:
        if any(trial[k] != current_spec["fixed_parameters"][k] for k in ["learning_rate","weight_decay","max_epochs"]):
            raise ValueError("Top-1 y Top-3 deben usar los mismos parámetros.")
        name = trial_id(trial)
        directory = root/"trials"/name
        stored_spec = json.loads((directory/"trial_spec.json").read_text(encoding="utf-8"))
        if stored_spec != {"study":release,"trial":trial}:
            raise ValueError("Un ensayo de referencia no pertenece al estudio fijado.")
        result = completed_trial(directory, stored_spec)
        if result is None or result["evaluation_policy"] != "v2_fp32":
            raise ValueError("Falta un resultado Top-3 completo y verificado.")
        audit = json.loads((directory/"evaluation/export_precision_audit.json").read_text(encoding="utf-8"))
        if audit["export_check"] != "passed_full_validation" or audit["split_hashes"] != current_spec["split_hashes"]:
            raise ValueError("La auditoría de Top-3 no corresponde a estas particiones.")
        report = json.loads((directory/"evaluation/classification_report.json").read_text(encoding="utf-8"))
        im = report["Improvement/Modification"]
        rows.append(dict(result, comparison_variant="Top-3", im_recall=im["recall"], im_support=im["support"]))
        markers[name] = {"training":sha256(directory/"TRAINING_COMPLETE.json"),
                         "evaluation":sha256(directory/"EVALUATION_COMPLETE.json")}
    token_audit = pd.read_csv(root/"token_budget_audit.csv")
    token_audit = token_audit.loc[(token_audit.config=="fragmentos") & (token_audit.split=="validation")].copy()
    expected_n = int(json.loads((root/"data_manifest.json").read_text())["rows"]["validation"])
    if len(token_audit) != expected_n or any(r["n"] != expected_n for r in rows):
        raise ValueError("El número de citas de referencia cambió.")
    metadata = {"study_id":release["study_id"],"study_manifest_sha256":sha256(root/"study_manifest.json"),
        "completion_sha256":sha256(root/"STUDY_COMPLETE.json"),"trial_markers":markers,
        "token_audit_sha256":sha256(root/"token_budget_audit.csv"),"test_scored":False}
    return sorted(rows,key=lambda r:r["seed"]), token_audit, metadata


def compare_top1(top1, reference, seeds):
    columns = ["learning_rate","weight_decay","max_epochs","n"]
    for rows in [top1,reference]:
        if len(rows)!=len(seeds) or {r["seed"] for r in rows}!=set(seeds):
            raise ValueError("La comparación requiere una medición por semilla y entrada.")
        if any(r["evaluation_policy"]!="v2_fp32" or not math.isfinite(r["f1_macro"]) for r in rows):
            raise ValueError("Solo se comparan métricas FP32 verificadas.")
    left, right = {r["seed"]:r for r in top1}, {r["seed"]:r for r in reference}
    for seed in seeds:
        if any(left[seed][k]!=right[seed][k] for k in columns):
            raise ValueError("Las parejas de semillas cambiaron parámetros o ejemplos.")
    paired = pd.DataFrame([{"seed":s,"top1_f1":left[s]["f1_macro"],"top3_f1":right[s]["f1_macro"],
        "difference_pp":100*(left[s]["f1_macro"]-right[s]["f1_macro"])} for s in seeds])
    rows = [dict(r,comparison_variant="Top-1") for r in top1] + [dict(r,comparison_variant="Top-3") for r in reference]
    stability = pd.DataFrame(rows).groupby("comparison_variant").agg(n=("f1_macro","size"),
        mean_f1=("f1_macro","mean"),std_f1=("f1_macro","std"),min_f1=("f1_macro","min"),max_f1=("f1_macro","max"))
    return paired, stability


def compare_reading(current, reference):
    current = current.loc[(current.config=="top1") & (current.split=="validation")].copy()
    if current.inst_key.duplicated().any() or reference.inst_key.duplicated().any() or set(current.inst_key)!=set(reference.inst_key):
        raise ValueError("La auditoría de lectura debe comparar exactamente las mismas citas.")
    paired = current.merge(reference[["inst_key","evidence_original","evidence_kept"]],on="inst_key",
        suffixes=("_top1","_top3"),validate="one_to_one")
    if not np.array_equal(paired.available_evidence_tokens,paired.evidence_original_top3):
        raise ValueError("El texto disponible antes de elegir Top-1 no coincide con Top-3.")
    table = pd.DataFrame([
        {"input":"Top-1","n":len(current),"selected_fragments":1,
         "selected_text_truncated_pct":100*float(current.evidence_truncated.mean()),
         "mean_selected_tokens":float(current.evidence_original.mean()),"mean_kept_tokens":float(current.evidence_kept.mean()),
         "fraction_of_original_top3_kept":float((paired.evidence_kept_top1/paired.evidence_original_top3).mean()),
         "omitted_fragments":2},
        {"input":"Top-3","n":len(reference),"selected_fragments":3,
         "selected_text_truncated_pct":100*float(reference.evidence_truncated.mean()),
         "mean_selected_tokens":float(reference.evidence_original.mean()),"mean_kept_tokens":float(reference.evidence_kept.mean()),
         "fraction_of_original_top3_kept":float((reference.evidence_kept/reference.evidence_original).mean()),
         "omitted_fragments":0}])
    return table


def review_top1_outputs(output, top1, reference, train_rows, val_rows, test_ids, labels, tracking):
    """Comprueba las predicciones guardadas sin volver a entrenar ni inferir."""
    import sqlite3
    import contextlib
    output = Path(output)
    seeds = {42,17,73}
    if len(top1)!=3 or len(reference)!=3 or any({r['seed'] for r in rows}!=seeds for rows in [top1,reference]):
        raise ValueError("La revisión necesita tres semillas por variante.")
    audit_release_splits(train_rows,val_rows,test_ids)
    expected = {r['inst_key']:r for r in val_rows}
    if len(expected)!=len(val_rows):
        raise ValueError("Hay citas de validación duplicadas.")
    label_ids = {name:i for i,name in enumerate(labels)}
    audits = []
    for row in [*top1,*reference]:
        directory = Path(row['model_dir']).parent
        if not (directory/'TRAINING_COMPLETE.json').is_file() or not (directory/'EVALUATION_COMPLETE.json').is_file():
            raise ValueError("Falta el cierre de un modelo o de su evaluación.")
        verify_files(directory/'evaluation',json.loads((directory/'EVALUATION_COMPLETE.json').read_text())['files'])
        frame = pd.read_csv(directory/'evaluation/predictions.csv')
        if frame.inst_key.duplicated().any() or set(frame.inst_key)!=set(expected):
            raise ValueError("Las predicciones no corresponden a las mismas citas de validación.")
        frame = frame.set_index('inst_key').loc[[r['inst_key'] for r in val_rows]]
        if frame.reference.tolist()!=[r['label'] for r in val_rows] or frame.label_source.tolist()!=[r['label_source'] for r in val_rows]:
            raise ValueError("Cambiaron las etiquetas de referencia o su procedencia.")
        probs = frame[[f'p_{name}' for name in labels]].to_numpy()
        if not np.isfinite(probs).all() or (probs<0).any() or (probs>1).any() or not np.allclose(probs.sum(axis=1),1,atol=2e-6):
            raise ValueError("Hay probabilidades inválidas.")
        if frame.predicted_label.tolist()!=[labels[int(i)] for i in probs.argmax(axis=1)]:
            raise ValueError("Una clase guardada no es la de mayor probabilidad.")
        metrics = probability_metrics(np.asarray([label_ids[r['label']] for r in val_rows]),probs)
        for key in ['f1_macro','accuracy']:
            if not math.isclose(float(metrics[key]),float(row[key]),abs_tol=1e-12):
                raise ValueError("Las métricas guardadas no coinciden con las predicciones.")
        audits.append({'trial_id':row['trial_id'],'seed':row['seed'],'n':len(frame),
                       'recomputed_f1_macro':float(metrics['f1_macro']),'recomputed_accuracy':float(metrics['accuracy'])})
    manifest = json.loads((output/'selected_models.json').read_text())
    package = manifest['models']['top1']
    main = next(r for r in top1 if r['seed']==42)
    if package['primary_seed']!=42 or package['trial_id']!=main['trial_id'] or sha256(package['archive'])!=package['archive_sha256']:
        raise ValueError("El paquete principal no corresponde al modelo fijado.")
    parents = tracking.client.search_runs([tracking.experiment],filter_string=f"tags.a4_run_id = '{manifest['study_id']}' and tags.kind = 'configuration'")
    if len(parents)!=3 or any(r.info.status!='FINISHED' for r in parents):
        raise ValueError("Los tres ensayos deben estar cerrados correctamente en MLflow.")
    parent_ids = {r.info.run_id for r in parents}
    attempts = [r for r in tracking.client.search_runs([tracking.experiment]) if r.data.tags.get('mlflow.parentRunId') in parent_ids]
    if any(r.info.status=='RUNNING' for r in attempts) or any(not any(r.data.tags.get('mlflow.parentRunId')==pid and r.info.status=='FINISHED' for r in attempts) for pid in parent_ids):
        raise ValueError("Falta cerrar un intento de entrenamiento.")
    with contextlib.closing(sqlite3.connect('file:'+str(tracking.root/'mlflow.db')+'?mode=ro',uri=True)) as db:
        if db.execute('PRAGMA integrity_check').fetchone()[0]!='ok':
            raise ValueError("La base de seguimiento no pasó la revisión de integridad.")
    result = {'study_id':manifest['study_id'],'new_models':3,'reference_models':3,'validation_rows':len(val_rows),
              'primary_seed':42,'test_scored':False,'document_isolation':'passed','prediction_audits':audits,
              'main_package_sha256':package['archive_sha256'],'mlflow_parents_finished':len(parents),
              'mlflow_attempts_total':len(attempts),'mlflow_attempts_finished':sum(r.info.status=='FINISHED' for r in attempts),
              'sqlite_integrity':'ok'}
    save_json(output/'validation_review.json',result)
    return result


def top1_conclusions(paired, stability, reading, reports, counts, source_counts=None):
    first, third = stability.loc["Top-1"],stability.loc["Top-3"]
    delta = float(paired.difference_pp.mean())
    relation = "por encima" if delta>0 else "por debajo" if delta<0 else "al mismo nivel"
    text = reading.set_index("input")
    support = int(counts.loc["Improvement/Modification","validation"])
    wins = int((paired.difference_pp>0).sum())
    variation = "mayor" if first.std_f1>third.std_f1 else "menor" if first.std_f1<third.std_f1 else "igual"
    im = "; ".join(f"{name}: {round(value['recall']*support)}/{support} citas recuperadas, F1 {value['f1-score']:.4f} y precisión {value['precision']:.4f}" for name,value in reports.items())
    provenance = (f"La validación reúne {int(source_counts.loc['human_gold','validation'])} etiquetas humanas y "
                  f"{int(source_counts.loc['pre_label','validation'])} automáticas. ") if source_counts is not None else ""
    return f'''## Conclusiones

Comparamos Top-1 y Top-3 sobre las mismas {int(counts.validation.sum()):,} citas de validación, con tres semillas y los mismos parámetros. Top-1 obtuvo F1 macro medio **{first.mean_f1:.4f} ± {first.std_f1:.4f}** y Top-3, **{third.mean_f1:.4f} ± {third.std_f1:.4f}**: la diferencia media fue de {abs(delta):.2f} puntos porcentuales {relation} de Top-3. Top-1 lo superó en **{wins} de {len(paired)} semillas** y tuvo {variation} variación entre corridas; esa comparación describe tanto el promedio como su estabilidad.

El texto elegido necesitó recorte en el **{text.loc['Top-1','selected_text_truncated_pct']:.2f}%** de Top-1 y el **{text.loc['Top-3','selected_text_truncated_pct']:.2f}%** de Top-3. Frente a la evidencia original de los tres fragmentos, Top-1 conservó en promedio el **{100*text.loc['Top-1','fraction_of_original_top3_kept']:.2f}%** de los tokens y Top-3, el **{100*text.loc['Top-3','fraction_of_original_top3_kept']:.2f}%**. Top-1 destinó más espacio al primer fragmento y omitió otros dos; por eso el menor recorte del texto elegido debe leerse junto con la cantidad de evidencia conservada.

Improvement/Modification tuvo {int(counts.loc['Improvement/Modification','train'])} ejemplos de entrenamiento y {support} de validación. En los modelos de semilla 42, {im}. El soporte de esta clase es reducido. {provenance}Conservamos la semilla 42 como modelo principal y guardamos los modelos y sus reportes. Estas cifras corresponden a validación interna; el test propio permanece separado del entrenamiento y de la selección.
'''
