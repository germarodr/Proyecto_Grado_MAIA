"""Evaluación del modelo exportado; se incrusta en la sección 12 del notebook."""
from pathlib import Path
from types import SimpleNamespace
import gc
import numpy as np
import torch
from sklearn.metrics import accuracy_score, precision_recall_fscore_support, f1_score
from transformers import AutoModelForSequenceClassification, DataCollatorWithPadding, Trainer, TrainingArguments


def probability_metrics(labels, probabilities):
    labels = np.asarray(labels)
    probabilities = np.asarray(probabilities)
    predictions = probabilities.argmax(axis=-1)
    classes = list(range(probabilities.shape[1]))
    precision, recall, f1, _ = precision_recall_fscore_support(
        labels, predictions, labels=classes, average="macro", zero_division=0)
    return {"accuracy": float(accuracy_score(labels, predictions)),
            "precision_macro": float(precision), "recall_macro": float(recall),
            "f1_macro": float(f1), "f1_micro": float(f1_score(
                labels, predictions, labels=classes, average="micro", zero_division=0))}


def compare_probabilities(reference, actual, keys, atol=2e-5, rtol=1e-4):
    reference, actual = np.asarray(reference), np.asarray(actual)
    if reference.shape != actual.shape or reference.ndim != 2 or len(keys) != len(actual) or not len(actual):
        raise ValueError("Las predicciones no tienen las mismas filas y clases")
    for values in [reference, actual]:
        if not np.isfinite(values).all() or (values < 0).any() or (values > 1).any():
            raise ValueError("Probabilidades inválidas")
        if not np.allclose(values.sum(axis=1), 1, atol=1e-5):
            raise ValueError("Las probabilidades no suman uno")
    changed = reference.argmax(-1) != actual.argmax(-1)
    return {"n": len(keys), "atol": atol, "rtol": rtol,
            "probabilities_close": bool(np.allclose(reference, actual, atol=atol, rtol=rtol)),
            "max_absolute_difference": float(np.abs(reference - actual).max()),
            "label_disagreements": int(changed.sum()),
            "changed_inst_keys": [key for key, differs in zip(keys, changed) if differs]}


def predict_export_fp32(classifier, data, batch_size):
    classifier.model.float().eval()
    collator = DataCollatorWithPadding(classifier.tokenizer, pad_to_multiple_of=8)
    probabilities = []
    for start in range(0, len(data), batch_size):
        items = [{k: v for k, v in data[i].items() if k != "labels"}
                 for i in range(start, min(start + batch_size, len(data)))]
        batch = {k: v.to(classifier.device) for k, v in collator(items).items()}
        # Explícito incluso si el llamador usa un contexto autocast externo.
        with torch.inference_mode(), torch.autocast(device_type=torch.device(classifier.device).type, enabled=False):
            probabilities.extend(classifier.model(**batch).logits.float().softmax(-1).cpu().tolist())
    return np.asarray(probabilities)


def audit_export(classifier, data, keys, checkpoint, output_dir, batch_size, seed, mixed_precision):
    """Compara checkpoint/exportación en FP32 y reproduce la ruta de Trainer.

    Nunca entrena ni modifica el checkpoint o la exportación existente.
    Si falta el checkpoint, la auditoría de exportación queda explícitamente pendiente.
    """
    if mixed_precision not in {"bf16", "fp16", "fp32"}:
        raise ValueError("Precisión de Trainer no reconocida")
    if classifier.model.config._attn_implementation != "eager":
        raise ValueError("La comparación requiere atención eager en ambas rutas")
    probabilities = predict_export_fp32(classifier, data, batch_size)
    has_checkpoint = bool(checkpoint and Path(checkpoint).is_dir())
    source = Path(checkpoint) if has_checkpoint else classifier.root
    reference_model = AutoModelForSequenceClassification.from_pretrained(
        source, local_files_only=True, attn_implementation="eager").float().to(classifier.device).eval()
    try:
        audit = {"evaluation_policy": "v2_fp32", "canonical_precision": "fp32", "attention_implementation": "eager",
                 "trainer_precision": mixed_precision, "reference_source": str(source),
                 "export_check": "pending_checkpoint_missing"}
        if has_checkpoint:
            reference = SimpleNamespace(model=reference_model, tokenizer=classifier.tokenizer, device=classifier.device)
            expected = predict_export_fp32(reference, data, batch_size)
            comparison = compare_probabilities(expected, probabilities, keys)
            audit["checkpoint_vs_export_fp32"] = comparison
            if not comparison["probabilities_close"] or comparison["label_disagreements"]:
                raise ValueError(f"La exportación no reproduce el checkpoint: {comparison}")
            audit["export_check"] = "passed_full_validation"
        args = TrainingArguments(output_dir=str(Path(output_dir) / "trainer_prediction"),
            per_device_eval_batch_size=batch_size, report_to="none", seed=seed,
            use_cpu=torch.device(classifier.device).type == "cpu",
            bf16=mixed_precision == "bf16", fp16=mixed_precision == "fp16", tf32=False,
            dataloader_num_workers=0, disable_tqdm=False)
        trainer = Trainer(model=reference_model, args=args, processing_class=classifier.tokenizer,
            data_collator=DataCollatorWithPadding(classifier.tokenizer, pad_to_multiple_of=8))
        prediction = trainer.predict(data)
        logits = prediction.predictions[0] if isinstance(prediction.predictions, tuple) else prediction.predictions
        trainer_probabilities = torch.as_tensor(logits).float().softmax(-1).numpy()
        audit["trainer_vs_export_fp32"] = compare_probabilities(trainer_probabilities, probabilities, keys)
        return probabilities, trainer_probabilities, audit
    finally:
        del reference_model
        gc.collect()
        if torch.cuda.is_available():
            torch.cuda.empty_cache()
