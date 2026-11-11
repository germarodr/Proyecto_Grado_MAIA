"""Genera una variante autónoma de evaluación, compatible con T4 y sin entrenamiento."""
import ast
import copy
import json
from pathlib import Path
import textwrap

ROOT = Path(__file__).resolve().parent
nb = json.loads((ROOT / "A4_SciBERT_G15_Colab_A100.ipynb").read_text(encoding="utf-8"))
nb = copy.deepcopy(nb)
cells = {c["id"]: c for c in nb["cells"]}


def replace(cell_id, old, new):
    source = cells[cell_id]["source"]
    if source.count(old) != 1:
        raise ValueError(f"No se encontró un único bloque esperado en {cell_id}: {old[:70]}")
    cells[cell_id]["source"] = source.replace(old, new)


cells["a4-000"]["source"] = """# A4 · Evaluación de los modelos existentes en T4

Esta variante ejecuta la preparación y evaluación del proyecto en FP32, con batch 8.
Requiere las exportaciones terminadas de **base y fragmentos** en Drive. No contiene
llamadas de entrenamiento ni guarda pesos. La selección original de checkpoints en
A100/BF16 se conserva; aquí no se intenta reproducir BF16 en T4.

Las auditorías de preparación se guardan en un directorio nuevo y los reportes de
validación en `evaluations/v2_fp32_<id>/`. El entorno y el batch de esta evaluación
quedan documentados. T_B permanece desactivado.

Ejecuta cada pareja explicación/código en orden en un servidor Colab con GPU.
"""
cells["a4-001"]["source"] = '''# Confirmar Colab con GPU antes de instalar dependencias.
try:
    import google.colab as _probe_colab
    import torch as _probe_torch
except ImportError as error:
    raise RuntimeError("Selecciona el kernel remoto de Colab antes de ejecutar.") from error
if not _probe_torch.cuda.is_available():
    raise RuntimeError("Selecciona un servidor Colab con GPU CUDA.")
print("GPU de evaluación:", _probe_torch.cuda.get_device_name(0))
''' + cells["a4-001"]["source"]
replace("a4-003", 'OUTPUT_ROOT = RESULTS_ROOT / "a4" / RUN_ID', '''import uuid as _evaluation_uuid
import json as _evaluation_json
MODEL_ROOT = RESULTS_ROOT / "a4" / RUN_ID
PREPARATION_ROOT = MODEL_ROOT / "evaluation_preparation" / ("t4_" + _evaluation_uuid.uuid4().hex[:12])
OUTPUT_ROOT = PREPARATION_ROOT
SOURCE_RUN_SPEC = _evaluation_json.loads((MODEL_ROOT / "run_manifest.json").read_text(encoding="utf-8"))
for _config in ["base", "fragmentos"]:
    if not (MODEL_ROOT / _config / "TRAINING_COMPLETE.json").is_file():
        raise FileNotFoundError(f"Falta el modelo terminado {_config}. Esta variante solo evalúa modelos existentes.")''')
replace("a4-003", 'CONFIGS = ["base"]', 'CONFIGS = ["base", "fragmentos"]')
replace("a4-003", "EVAL_BATCH = 32", "EVAL_BATCH = 8")
replace("a4-003", "REQUIRE_A100 = True", "REQUIRE_A100 = False")
replace("a4-003", "RESUME = False", "RESUME = True")
cells["a4-004"]["source"] = "## 2. Registrar el entorno de evaluación\n\nSe requiere GPU CUDA. FP32 y batch 8 permiten evaluar los modelos existentes en T4. El entorno se guarda en la preparación de esta sesión, sin reemplazar el entorno de entrenamiento.\n"
replace("a4-005", '(OUTPUT_ROOT / "base/TRAINING_COMPLETE.json")', '(MODEL_ROOT / "base/TRAINING_COMPLETE.json")')
replace("a4-005", 'raise RuntimeError("Activa GPU A100 en Colab antes de entrenar.")', 'raise RuntimeError("Selecciona un servidor Colab con GPU CUDA para evaluar.")')
replace("a4-017", 'for rows in splits.values() for r in rows}', 'for rows in [splits["validation"]] for r in rows}')
replace("a4-017", 'for split, rows in splits.items():\n', 'for split, rows in splits.items():\n    if split != "validation":\n        continue\n')
cells["a4-016"]["source"] = "## 8. Reconstruir únicamente los textos de validación\n\nSe conservan los hashes de los lotes y la partición original, pero solo se retienen los textos de validación para reducir memoria.\n"
replace("a4-019", 'previous_spec = OUTPUT_ROOT / "run_manifest.json"', 'previous_spec = MODEL_ROOT / "run_manifest.json"')
replace("a4-019", '    for split, rows in splits.items():\n', '    for split, rows in splits.items():\n        if split != "validation":\n            continue\n')
replace("a4-021", 'spec_path = OUTPUT_ROOT / "run_manifest.json"', '''# El batch de evaluación y el entorno pueden cambiar sin alterar los pesos.
scientific_keys = set(SOURCE_RUN_SPEC) | set(run_spec)
scientific_keys -= {"environment", "eval_batch"}
differences = [key for key in sorted(scientific_keys) if SOURCE_RUN_SPEC.get(key) != run_spec.get(key)]
if differences:
    raise ValueError(f"Datos o decisiones diferentes del entrenamiento original: {differences}")
save_json(PREPARATION_ROOT / "evaluation_context.json", {
    "purpose": "evaluation_only", "source_model_root": str(MODEL_ROOT),
    "source_training_environment": SOURCE_RUN_SPEC["environment"],
    "evaluation_environment": ENVIRONMENT, "evaluation_batch": EVAL_BATCH,
    "precision": "fp32", "trainer_replay_precision": "fp32",
})
spec_path = OUTPUT_ROOT / "run_manifest.json"''')
replace("a4-023", '                      OUTPUT_ROOT, RUN_ID, SNAPSHOT_INTERVAL_SECONDS)', '                      MODEL_ROOT, RUN_ID, SNAPSHOT_INTERVAL_SECONDS)')
compute_source = cells["a4-025"]["source"].split("INFERENCE_TEMPLATE =", 1)[0]
cells["a4-025"]["source"] = compute_source + textwrap.dedent('''
OUTPUT_ROOT = MODEL_ROOT
validation_results = []
for config in CONFIGS:
    workdir = MODEL_ROOT / config
    manifest = json.loads((workdir / "TRAINING_COMPLETE.json").read_text(encoding="utf-8"))
    for name, digest in manifest["model_hashes"].items():
        if sha256(workdir / "model" / name) != digest:
            raise ValueError(f"Hash del modelo alterado: {config}/{name}")
    validation_results.append(json.loads((workdir / "validation_metrics.json").read_text(encoding="utf-8")))
    print(config, "modelo existente verificado; solo evaluación FP32.")
display(pd.DataFrame(validation_results).drop(columns=["train_metrics"]))
''')
cells["a4-024"]["source"] = "## 11. Verificar los modelos guardados\n\nSe verifican todos los hashes de las exportaciones de base y fragmentos. Esta celda no entrena ni modifica los pesos. La tabla mostrada corresponde a las métricas históricas de A100/BF16; la evaluación nueva aparece en la sección 12.\n"
replace("a4-027", 'precision = "bf16" if USE_BF16 else "fp16"', 'precision = "fp32"')
replace("a4-027", '"model_revision": MODEL_REVISION, "split_hashes": split_hashes, "labels": LABELS,', '''"model_revision": MODEL_REVISION, "split_hashes": split_hashes, "labels": LABELS,
                "purpose": "evaluation_only", "environment": ENVIRONMENT, "evaluation_batch": EVAL_BATCH,
                "source_training_environment": SOURCE_RUN_SPEC["environment"],
                "replay_matches_original_training_precision": False,
                "preparation_directory": str(PREPARATION_ROOT),''')
replace("a4-027", '"cambios de etiqueta por precisión:"', '"desacuerdos Trainer FP32 / exportación FP32:"')
cells["a4-026"]["source"] = "## 12. Evaluar en FP32 y comprobar la exportación\n\nSe compara toda la validación entre checkpoint y exportación, usando FP32 y atención eager. Trainer también predice en FP32. No se reproduce BF16 de A100 en esta T4. Cada evaluación crea reportes e hijos de MLflow nuevos, con su entorno y batch registrados.\n"
cells["a4-029"]["source"] = 'test_summary = []\ntest_probabilities = {}\nif RUN_TEST or GOLD_FINAL:\n    raise ValueError("Esta variante solo permite validación; el test humano requiere el protocolo final.")\nprint("T_B humano no ejecutado: esta sesión solo evalúa validación.")\n'
cells["a4-028"]["source"] = "## 13. Mantener reservado el test humano\n\nLa variante de evaluación conserva T_B desactivado. Se utilizan los mismos 3.226 ejemplos de validación; las etiquetas siguen siendo las preetiquetas disponibles.\n"
cells["a4-031"]["source"] = '''for config in CONFIGS:
    tracking.client.set_tag(tracking.parent(config), "latest_evaluation_drive", str(EVALUATION_ROOT / config))
    for path in sorted(EVALUATION_ROOT.glob("*.csv")) + sorted(EVALUATION_ROOT.glob("*.json")):
        tracking.client.log_artifact(tracking.parent(config), str(path), artifact_path="evaluation_comparisons/" + EVALUATION_ROOT.name)
tracking.backup(force=True)
print("Evaluación FP32 completada:", EVALUATION_ROOT)
print("Preparación de esta sesión:", PREPARATION_ROOT)
print("Los modelos entrenados y los ZIP originales se conservan en:", MODEL_ROOT)
'''
cells["a4-030"]["source"] = "## 14. Publicar el respaldo final\n\nSe guardan las referencias a las nuevas evaluaciones y un snapshot completo de MLflow. Los modelos y sus ZIP existentes se usan como referencia.\n"
for cell in nb["cells"]:
    if cell["cell_type"] == "code":
        cell["execution_count"], cell["outputs"] = None, []
        tree = ast.parse(cell["source"])
        if any(isinstance(n, ast.Call) and isinstance(n.func, ast.Attribute) and n.func.attr in {"train", "save_model", "save_pretrained"} for n in ast.walk(tree)):
            raise ValueError("Se encontró una operación de entrenamiento o escritura de pesos")
nb["metadata"]["colab"]["name"] = "A4_SciBERT_G15_Evaluacion_T4.ipynb"
target = ROOT / nb["metadata"]["colab"]["name"]
target.write_text(json.dumps(nb, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
print(target)
