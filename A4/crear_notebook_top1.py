"""Una sola prueba de ablación: primer fragmento de A1, mismo split y entrenamiento."""
import ast
import copy
import json
from pathlib import Path
import textwrap

ROOT = Path(__file__).resolve().parent
nb = copy.deepcopy(json.loads((ROOT / "A4_SciBERT_G15_Colab_A100.ipynb").read_text(encoding="utf-8")))
cells = {c["id"]: c for c in nb["cells"]}


def replace(cell_id, old, new):
    if cells[cell_id]["source"].count(old) != 1:
        raise ValueError(f"Cambio no localizado en {cell_id}: {old[:60]}")
    cells[cell_id]["source"] = cells[cell_id]["source"].replace(old, new)


cells["a4-000"]["source"] = '''# A4 · Prueba controlada: primer fragmento (Top-1)

Se entrena **un modelo nuevo** usando el primer elemento de la lista Top-3 entregada
por A1, en su orden original. No se recalcula ni reordena la recuperación.
Se conserva V0, semilla 42, split, contexto, 512 tokens, LR 2e-5, batch efectivo 32,
cuatro épocas máximas y selección por F1 macro. Se usa la revisión exacta de SciBERT
del experimento original. Se verifica la igualdad de datos, split e hiperparámetros
antes de entrenar. Los pesos y resultados van a un RUN_ID nuevo.

Esta prueba reduce de tres a uno los fragmentos: cambia tanto la selección de
evidencia como el espacio disponible para ese pasaje. No permite atribuir por
separado esos dos efectos. El test humano sigue desactivado.

Antes de entrenar se prepara un paquete diagnóstico ciego de 20 citas de validación
para revisar Evidence e Improvement/Modification. No es anotación formal de A3 ni
gold final de T_B. Ejecuta las parejas explicación/código en orden sobre A100.
'''
cells["a4-001"]["source"] = '''import google.colab as _top1_colab
import torch as _top1_torch
if not _top1_torch.cuda.is_available() or "A100" not in _top1_torch.cuda.get_device_name(0):
    raise RuntimeError("Selecciona el servidor Colab A100 existente para esta prueba controlada.")
print("GPU de la prueba Top-1:", _top1_torch.cuda.get_device_name(0))
''' + cells["a4-001"]["source"]
replace("a4-003", 'RUN_ID = "g15_a4_v0_seed42_mlflow_01"', 'RUN_ID = "g15_a4_v0_seed42_top1_01"')
replace("a4-003", 'CONFIGS = ["base"]', 'CONFIGS = ["fragmentos_top1"]')
replace("a4-003", 'assert set(CONFIGS) <= {"base", "fragmentos"} and CONFIGS', 'assert CONFIGS == ["fragmentos_top1"]')
replace("a4-003", 'OUTPUT_ROOT = RESULTS_ROOT / "a4" / RUN_ID', '''OUTPUT_ROOT = RESULTS_ROOT / "a4" / RUN_ID
BASELINE_ROOT = RESULTS_ROOT / "a4/g15_a4_v0_seed42_mlflow_01"
BASELINE_EVALUATION_ROOT = BASELINE_ROOT / "evaluations/v2_fp32_37dc6f909cde"
import json as _baseline_json
BASELINE_SPEC = _baseline_json.loads((BASELINE_ROOT / "run_manifest.json").read_text(encoding="utf-8"))''')
replace("a4-019", 'previous_spec = OUTPUT_ROOT / "run_manifest.json"', 'previous_spec = BASELINE_ROOT / "run_manifest.json"')
replace("a4-019", 'elif config == "fragmentos":', 'elif config in {"fragmentos", "fragmentos_top1"}:')
replace("a4-019", '        sections = [ids(f"Section: {ch[\'section\']} Passage: ")[:24] for ch in example["chunks"]]', '''        chunks = example["chunks"][:1] if config == "fragmentos_top1" else example["chunks"]
        sections = [ids(f"Section: {ch['section']} Passage: ")[:24] for ch in chunks]''')
replace("a4-019", '        bodies = [ids(ch["text"]) for ch in example["chunks"]]', '        bodies = [ids(ch["text"]) for ch in chunks]')
replace("a4-021", 'spec_path = OUTPUT_ROOT / "run_manifest.json"', '''controlled_keys = set(BASELINE_SPEC) | set(run_spec)
controlled_keys -= {"environment"}
changed = [key for key in sorted(controlled_keys) if BASELINE_SPEC.get(key) != run_spec.get(key)]
if changed:
    raise ValueError(f"La prueba Top-1 cambió otra decisión además de la evidencia: {changed}")
run_spec.update(evidence_policy="first_of_original_top3", baseline_run_id=BASELINE_ROOT.name,
                baseline_evaluation=str(BASELINE_EVALUATION_ROOT))
spec_path = OUTPUT_ROOT / "run_manifest.json"''')
replace("a4-025", '"markers": MARKERS, "model_revision": MODEL_REVISION, "score_calibrated": False}', '"markers": MARKERS, "model_revision": MODEL_REVISION, "score_calibrated": False, "evidence_policy": "first_of_original_top3"}')
cells["a4-024"]["source"] = '''## 11. Entrenar una sola variante Top-1

El modelo parte del mismo SciBERT preentrenado, con cabeza nueva y semilla 42.
Se mantienen los hiperparámetros de las corridas anteriores. Un RUN_ID nuevo separa
sus parámetros, checkpoints y métricas. No se modifican las etiquetas con la revisión manual.
'''
manual_code = (ROOT / "revision_manual_runtime.py").read_text(encoding="utf-8") + '''
manual_review_root = RESULTS_ROOT / "a4/revision_manual" / ("evidence_im_" + uuid.uuid4().hex[:10])
manual_review_root = create_manual_review(manual_review_root, BASELINE_EVALUATION_ROOT,
                                        val_rows, texts, LABELS, seed=42)
save_json(OUTPUT_ROOT / "manual_review_reference.json", {"directory": str(manual_review_root),
    "scope": "diagnostic_validation_only", "not_final_gold": True})
'''
position = next(i for i, c in enumerate(nb["cells"]) if c["id"] == "a4-024")
nb["cells"][position:position] = [
    {"cell_type": "markdown", "metadata": {}, "id": "top1-review-description", "source": '''## 10.2. Preparar la revisión manual

Se seleccionan 20 citas de validación: 10 alrededor de cada categoría objetivo,
mezclando discrepancias y controles. Las referencias automáticas solo se usan para
muestrear; no se muestran en el paquete de revisión. Guarda tus decisiones en el
XLSX o CSV y consulta los textos en el HTML. No abras `_analisis` antes de terminar.
El paquete queda en Drive privado y sus textos no se envían a los artefactos de MLflow.
'''.strip() + "\n"},
    {"cell_type": "code", "metadata": {}, "id": "top1-review-code", "source": manual_code,
     "execution_count": None, "outputs": []}]
comparison = textwrap.dedent('''
baseline_comparison = pd.read_csv(BASELINE_EVALUATION_ROOT / "validation_comparison.csv")
comparison = pd.concat([baseline_comparison, pd.DataFrame(val_summary)], ignore_index=True)
comparison.to_csv(EVALUATION_ROOT / "validation_comparison_with_baseline.csv", index=False)
display(comparison[["config", "n", "precision", "f1_macro", "accuracy", "recall_macro"]])
reference_scores = baseline_comparison.set_index("config").f1_macro.to_dict()
top1_score = val_summary[0]["f1_macro"]
for reference_config in ["base", "fragmentos"]:
    print("Delta Top-1 menos", reference_config, ":", top1_score - reference_scores[reference_config])
''')
position = next(i for i, c in enumerate(nb["cells"]) if c["id"] == "a4-028")
nb["cells"][position:position] = [
    {"cell_type": "markdown", "metadata": {}, "id": "top1-comparison-description", "source": '''## 12.1. Comparar con las dos referencias congeladas

La tabla utiliza F1 macro FP32 sobre la misma validación. No selecciona por T_B
ni vuelve a ajustar el modelo después de ver el resultado. Es una prueba de esta
semilla; una diferencia pequeña no demuestra una mejora estable.
'''},
    {"cell_type": "code", "metadata": {}, "id": "top1-comparison-code", "source": comparison,
     "execution_count": None, "outputs": []}]
for i, cell in enumerate(nb["cells"]):
    if cell["cell_type"] != ("markdown" if i % 2 == 0 else "code"):
        raise ValueError("Se perdió la alternancia explicación/código")
    if cell["cell_type"] == "code":
        ast.parse(cell["source"])
        cell.update(execution_count=None, outputs=[])
nb["metadata"]["colab"]["name"] = "A4_SciBERT_G15_Top1_Colab_A100.ipynb"
target = ROOT / nb["metadata"]["colab"]["name"]
target.write_text(json.dumps(nb, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
print(target)
