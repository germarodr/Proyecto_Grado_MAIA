"""Genera la comparación exploratoria V2 sin modificar las corridas V0."""
import ast
import copy
import json
from pathlib import Path
import textwrap

ROOT = Path(__file__).resolve().parent


def build():
    nb = copy.deepcopy(json.loads((ROOT / "A4_SciBERT_G15_Colab_A100.ipynb").read_text(encoding="utf-8")))
    cells = {c["id"]: c for c in nb["cells"]}

    def replace(cell_id, old, new):
        if cells[cell_id]["source"].count(old) != 1:
            raise ValueError(f"Cambio no localizado en {cell_id}: {old[:70]}")
        cells[cell_id]["source"] = cells[cell_id]["source"].replace(old, new)

    cells["a4-000"]["source"] = '''# A4 · Comparación exploratoria V2 frente a V0 · Grupo 15

Se entrenan **base y Top-3**, cada uno desde SciBERT preentrenado con cabeza nueva,
semilla 42 y los mismos hiperparámetros de V0. V2 aísla los documentos en ambos
roles entre train, validación y el test propio. No se reutilizan pesos V0.

**Origen:** training v1 actual y preetiquetas A2; **aislamiento:** V2.
V2 no significa una nueva entrega del dataset ni que el 15% humano esté consolidado.
El test T_B permanece cerrado. El paquete manual de 20 casos no se incorpora aquí.

Un RUN_ID nuevo separa modelos, métricas y checkpoints; MLflow conserva el historial
acumulado en Drive. Ejecutar explicación/código en orden con Colab A100.
El EDA inicial compara los conteos V0/V2. Al final se muestran las validaciones
propias y, por separado, las mismas citas comunes para comparar sin mezclar filas.
Cambian el aislamiento y el tamaño de train: el efecto no se atribuye solo al primero.
'''
    cells["a4-001"]["source"] = '''import torch as _v2_torch
if not _v2_torch.cuda.is_available() or "A100" not in _v2_torch.cuda.get_device_name(0):
    raise RuntimeError("Conecta una GPU Colab A100 antes de iniciar esta prueba V2.")
print("GPU V2:", _v2_torch.cuda.get_device_name(0))
''' + cells["a4-001"]["source"]
    replace("a4-003", 'VARIANT = "V0"', 'VARIANT = "V2"')
    replace("a4-003", 'RUN_ID = "g15_a4_v0_seed42_mlflow_01"', 'RUN_ID = "g15_a4_v2_seed42_mlflow_01"')
    replace("a4-003", 'CONFIGS = ["base"]  # primera corrida; después ["base", "fragmentos"] con RESUME=True',
            'CONFIGS = ["base", "fragmentos"]  # ambos modelos se entrenan desde SciBERT preentrenado')
    replace("a4-003", 'OUTPUT_ROOT = RESULTS_ROOT / "a4" / RUN_ID', '''OUTPUT_ROOT = RESULTS_ROOT / "a4" / RUN_ID
BASELINE_ROOT = RESULTS_ROOT / "a4/g15_a4_v0_seed42_mlflow_01"
BASELINE_EVALUATION_ROOT = BASELINE_ROOT / "evaluations/v2_fp32_37dc6f909cde"
assert OUTPUT_ROOT != BASELINE_ROOT''')
    replace("a4-003", 'GOLD_FILES = []  # rutas explícitas a gold_round1.jsonl, gold_round2.jsonl o test_set_gold.jsonl',
            'GOLD_FILES = []  # exploración con las mismas preetiquetas A2 de V0; no cargar T_B')
    replace("a4-003", 'assert VARIANT in {"V0", "V1", "V2"}',
            'assert VARIANT == "V2" and not GOLD_FILES and not GOLD_FINAL and not RUN_TEST')
    replace("a4-003", 'assert set(CONFIGS) <= {"base", "fragmentos"} and CONFIGS',
            'assert CONFIGS == ["base", "fragmentos"]')
    replace("a4-002", '**Decisiones propuestas, modificables aquí antes de entrenar:** V0, validación',
            '**Decisiones de esta prueba:** V2, validación')
    replace("a4-002", 'Los resultados se guardan en Drive privado. Primero se libera `base` como v0.',
            'Los resultados se guardan en Drive privado bajo un RUN_ID V2 nuevo; V0 queda como referencia de lectura.')
    runtime = (ROOT / "v2_comparison_runtime.py").read_text(encoding="utf-8")
    cells["a4-007"]["source"] += "\n" + runtime + '''
BASELINE_SPEC, V0_REFERENCE = load_v0_reference(BASELINE_ROOT, BASELINE_EVALUATION_ROOT, LABELS)
save_json(OUTPUT_ROOT / "v0_reference.json", V0_REFERENCE)
print("Referencia V0 verificada:", V0_REFERENCE["evaluation_root"])
'''
    cells["a4-006"]["source"] += '''
También se verifican el manifiesto y la auditoría de exportación FP32 de V0 y se
registran hashes de los reportes/predicciones usados como referencia. No se reescriben.
'''
    replace("a4-019", 'previous_spec = OUTPUT_ROOT / "run_manifest.json"',
            'previous_spec = BASELINE_ROOT / "run_manifest.json"')
    replace("a4-021", 'spec_path = OUTPUT_ROOT / "run_manifest.json"', '''validate_v2_spec(BASELINE_SPEC, run_spec)
run_spec.update(baseline_run_id=BASELINE_ROOT.name, baseline_reference=V0_REFERENCE,
                purpose="exploratory_isolation_V2", dataset_release="training_v1")
spec_path = OUTPUT_ROOT / "run_manifest.json"''')
    cells["a4-020"]["source"] += '''
Se exige igualdad de datos, etiquetas, revisión del modelo e hiperparámetros con V0;
solo cambian aislamiento, hashes de partición y entorno registrado. Una nueva entrega
de datos requerirá otro RUN_ID y una comparación diseñada para esa entrega.
'''
    cells["a4-023"]["source"] += '''
for config in CONFIGS:
    parent_id = tracking.parent(config)
    tracking.client.set_tag(parent_id, "isolation", "V2")
    tracking.client.set_tag(parent_id, "baseline_run_id", BASELINE_ROOT.name)
    tracking.client.set_tag(parent_id, "dataset_release", "training_v1")
    tracking.client.set_tag(parent_id, "evaluation_scope", "exploratory_validation_prelabels")
'''
    comparison = textwrap.dedent('''
        reference_counts = pd.read_csv(BASELINE_ROOT / "split_class_counts.csv", index_col=0)
        own_validation, common_validation, common_per_class = compare_v0_v2(
            BASELINE_EVALUATION_ROOT, EVALUATION_ROOT, BASELINE_ROOT.name, RUN_ID, LABELS,
            int(reference_counts["train"].sum()), len(train_rows), EVALUATION_ROOT)
        print("Validaciones propias: tamaños distintos; comparación descriptiva.")
        display(own_validation[["isolation", "config", "train_n", "n", "f1_macro", "accuracy"]])
        print("Mismas citas de validación, alineadas por inst_key; no es el test humano.")
        display(common_validation[["isolation", "config", "train_n", "n", "f1_macro", "accuracy"]])
        display(common_per_class.loc[common_per_class.label.isin(["Evidence", "Improvement/Modification"]),
            ["isolation", "config", "label", "f1_class", "recall_class", "support"]])
        common_scores = common_validation.pivot(index="config", columns="isolation", values="f1_macro")
        ax = common_scores.reindex(["base", "fragmentos"])[["V0", "V2"]].plot.bar(
            figsize=(8, 4), ylim=(0, 1), rot=0, color=["#8fa6be", "#16877c"])
        ax.set(xlabel="Configuración de entrada", ylabel="F1 macro FP32",
               title="V0 frente a V2 · mismas citas de validación")
        for container in ax.containers:
            ax.bar_label(container, fmt="%.4f", padding=3)
        ax.figure.tight_layout()
        ax.figure.savefig(EVALUATION_ROOT / "isolation_common_f1.png", dpi=160)
        plt.show()
        plt.close(ax.figure)
        for config in CONFIGS:
            current = common_validation.loc[(common_validation.config == config) &
                                            (common_validation.isolation == "V2")].iloc[0]
            reference = common_validation.loc[(common_validation.config == config) &
                                              (common_validation.isolation == "V0")].iloc[0]
            delta = float(current.f1_macro - reference.f1_macro)
            print(config, "delta F1 macro V2 - V0 en validación común:", delta)
            tracking.metrics(tracking.parent(config), {
                "common_validation_n": int(current.n), "common_validation_v2_f1_macro": float(current.f1_macro),
                "common_validation_v0_f1_macro": float(reference.f1_macro), "common_validation_delta_f1_macro": delta})
        save_json(EVALUATION_ROOT / "isolation_comparison_notes.json", {
            "baseline_run_id": BASELINE_ROOT.name, "run_id": RUN_ID, "test_used": False,
            "precision": "fp32", "common_validation_n": int(common_validation.n.iloc[0]),
            "interpretation": "Cambian aislamiento y tamaño de train; una semilla, preetiquetas A2.",
            "common_keys_sha256": sha256(EVALUATION_ROOT / "isolation_common_keys.csv")})
    ''')
    position = next(i for i, c in enumerate(nb["cells"]) if c["id"] == "a4-028")
    nb["cells"][position:position] = [
        {"cell_type": "markdown", "metadata": {}, "id": "v2-comparison-description", "source": '''## 12.1. Comparar V2 con las referencias V0 congeladas

Las validaciones propias tienen tamaños distintos. La comparación principal de esta
prueba usa sus citas comunes: exige que toda val V2 esté en val V0, alinea por clave
y verifica las etiquetas antes de calcular métricas. Se muestran las dos entradas,
las categorías escasas, una gráfica y CSV exportables. No se compara con T_B ni se
ajusta nada después de sus resultados. El tamaño de train también cambia.
'''},
        {"cell_type": "code", "metadata": {}, "id": "v2-comparison-code", "source": comparison,
         "execution_count": None, "outputs": []}]
    replace("a4-031", 'sorted(EVALUATION_ROOT.glob("*.json")):',
            'sorted(EVALUATION_ROOT.glob("*.json")) + sorted(EVALUATION_ROOT.glob("*.png")):')
    for i, cell in enumerate(nb["cells"]):
        assert cell["cell_type"] == ("markdown" if i % 2 == 0 else "code")
        if cell["cell_type"] == "code":
            ast.parse(cell["source"])
            cell.update(execution_count=None, outputs=[])
    nb["metadata"]["colab"]["name"] = "A4_SciBERT_G15_V2_Colab_A100.ipynb"
    return nb


if __name__ == "__main__":
    target = ROOT / "A4_SciBERT_G15_V2_Colab_A100.ipynb"
    target.write_text(json.dumps(build(), ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    print(target)
