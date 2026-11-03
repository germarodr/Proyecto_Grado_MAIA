"""Genera el notebook autónomo A4; no requiere este script en Colab."""
from pathlib import Path
import json
import textwrap

CELLS = []


def step(description, code):
    for kind, source in (("markdown", description), ("code", code)):
        cell = {"cell_type": kind, "metadata": {},
                "source": textwrap.dedent(source).strip() + "\n"}
        if kind == "code":
            cell.update(execution_count=None, outputs=[])
        CELLS.append(cell)


step(r'''
# A4 · Fine-tuning de SciBERT — Grupo 15

**Objetivo:** clasificar una cita en una de las nueve funciones de la guía rev3.1 y
comparar dos modelos ajustados desde el mismo SciBERT:

| Configuración | Información del artículo citado, además del contexto citante |
|---|---|
| `base` | Título y abstract |
| `fragmentos` | Tres fragmentos recuperados por A1 y sus secciones |

La propuesta y el plan dicen **SciBERT**, `allenai/scibert_scivocab_uncased`.
Se ajustan todos sus parámetros y una cabeza de nueve salidas mediante entropía
cruzada. No se vuelve a ejecutar A1 ni los jueces de A2.

**Orden:** leer cada explicación y ejecutar la celda siguiente. Seleccionar
*Entorno de ejecución → Cambiar tipo → A100*. El notebook conserva PyTorch/CUDA
de Colab y fija versiones de las bibliotecas de entrenamiento. Si ya se habían
importado versiones diferentes, reiniciar la sesión después de esta celda.
No hay entrenamiento ejecutado ni resultados precargados en este archivo.

Fuentes: propuesta, plan de trabajo, informe al 23-oct, contrato al 28-oct y
presentación de la ronda 1 al 27-oct; se excluyó `entrega1/`.
''', r'''
import subprocess
import sys

PINNED = [
    "transformers==4.57.1", "accelerate==1.11.0", "datasets==4.3.0",
    "scikit-learn==1.7.2", "matplotlib==3.10.7", "safetensors==0.6.2", "mlflow==3.17.2",
]
subprocess.check_call([sys.executable, "-m", "pip", "install", "-q", *PINNED])
print("Instalación terminada. Continúa si estas bibliotecas aún no estaban importadas.")
''')

step(r'''
## 1. Montar Drive y fijar las decisiones del experimento

En Mi unidad ya están el acceso directo **`MAIA_PROYECTO`**, usado como origen de
datos, y la carpeta propia **`MAIA_TESIS`**, usada para las salidas. `DATA_ROOT` apunta
al acceso directo y `RESULTS_ROOT` a la carpeta propia. No se escriben resultados
en el origen compartido. Los lotes se leen de `MAIA_PROYECTO/a2/batches_norw/`.

Copia los archivos pequeños de `TrainingData_Grupo15/` del repositorio a
`MAIA_TESIS/TrainingData_Grupo15/`, directamente en tu carpeta propia, como ya la
subiste a Drive. No hace falta duplicar los lotes de A2.
El manifiesto original conserva sus rutas históricas como procedencia; estas
variables determinan las rutas de esta ejecución.

Los ocho lotes requeridos se comprueban más adelante. Los archivos gigantes de
`inputs/` no son necesarios si los lotes ya contienen los textos de A2.

**Decisiones propuestas, modificables aquí antes de entrenar:** V0, validación
aproximada del 10% agrupada por citante, semilla 42, 4 épocas máximas, LR 2e-5,
batch efectivo 32 y CE sin ponderar. V0 permite compartir citados entre particiones;
V1 separa los citados y V2 también los roles inversos. Se medirá el impacto de las tres.
No se usa un corte temporal: T_B ya está congelado y esta ejecución no mide generalización
temporal. Tampoco se fuerza estratificación por sección; se auditará su distribución.

`RUN_ID` identifica una ejecución: usar un nombre nuevo para un nuevo experimento.
`RESUME=True` permite retomar únicamente checkpoints compatibles de ese directorio.
Los resultados se guardan en Drive privado. Primero se libera `base` como v0.
''', r'''
from pathlib import Path
try:
    from google.colab import drive
    drive.mount("/content/drive")
except ImportError:
    print("Fuera de Colab: configura rutas locales y REQUIRE_A100=False para pruebas.")

DATA_ROOT = Path("/content/drive/MyDrive/MAIA_PROYECTO")  # acceso directo: solo lectura
RESULTS_ROOT = Path("/content/drive/MyDrive/MAIA_TESIS")  # carpeta propia: resultados
assert DATA_ROOT.is_dir(), f"No se encuentra el acceso directo: {DATA_ROOT}"
assert RESULTS_ROOT.is_dir(), f"No se encuentra la carpeta de resultados: {RESULTS_ROOT}"
if RESULTS_ROOT.resolve().is_relative_to(DATA_ROOT.resolve()):
    raise ValueError("RESULTS_ROOT debe estar fuera del origen compartido DATA_ROOT.")
IDS_DIR = RESULTS_ROOT / "TrainingData_Grupo15"
BATCH_DIR = DATA_ROOT / "a2/batches_norw"
POOL_PATH = DATA_ROOT / "a2/pool_v11.1_ext/prelabels_pool.jsonl"  # opcional
GOLD_FILES = []  # rutas explícitas a gold_round1.jsonl, gold_round2.jsonl o test_set_gold.jsonl
GOLD_FINAL = False  # True solo tras confirmar adjudicación y liberaciones cerradas
RUN_TEST = False  # True únicamente para la evaluación final acordada; no para elegir modelos

VARIANT = "V0"  # V0, V1 o V2; conservar el mismo valor para ambas configuraciones
RUN_ID = "g15_a4_v0_seed42_mlflow_01"
OUTPUT_ROOT = RESULTS_ROOT / "a4" / RUN_ID
CONFIGS = ["base"]  # primera corrida; después ["base", "fragmentos"] con RESUME=True
SEED = 42
SPLIT_SEED = "G15-A4-split-v1"
VAL_FRAC = 0.10
MAX_LENGTH = 512
CONTEXT_BUDGET = 192
EPOCHS = 4
LEARNING_RATE = 2e-5
TRAIN_BATCH = 16
GRAD_ACCUM = 2
EVAL_BATCH = 32
REQUIRE_A100 = True
RESUME = False
SNAPSHOT_INTERVAL_SECONDS = 300
LABELS = ["Background", "Gap", "Basis", "Comparison", "Application",
          "Improvement/Modification", "Evidence", "Identification of the Originator",
          "Further Reading"]
LABEL2ID = {v: k for k, v in enumerate(LABELS)}
ID2LABEL = dict(enumerate(LABELS))
assert VARIANT in {"V0", "V1", "V2"}
assert set(CONFIGS) <= {"base", "fragmentos"} and CONFIGS
assert 0 < VAL_FRAC < 1 and 32 <= CONTEXT_BUDGET < MAX_LENGTH - 3
if RUN_TEST and (not GOLD_FILES or not GOLD_FINAL):
    raise ValueError("La prueba requiere gold final explícito. No usar pre-etiquetas como gold.")
''')

step(r'''
## 2. Verificar GPU, reproducibilidad y versiones

Se usa BF16 en A100, padding dinámico y batches de 16 con dos pasos de acumulación.
El batch efectivo es 32. Cada configuración reinicia SciBERT y la cabeza con la
misma semilla. La reproducibilidad numérica puede variar entre versiones de CUDA
y hardware; se registran el entorno y la revisión exacta del modelo.
''', r'''
import os
os.environ["TOKENIZERS_PARALLELISM"] = "false"
os.environ["CUBLAS_WORKSPACE_CONFIG"] = ":4096:8"
import collections
import gc
import hashlib
import importlib.metadata
import json
import random
import shutil
import time
import numpy as np
import pandas as pd
import torch
from datasets import Dataset
from sklearn.metrics import (accuracy_score, classification_report, confusion_matrix,
                             precision_recall_fscore_support, f1_score)
from transformers import (AutoTokenizer, AutoModelForSequenceClassification,
                          DataCollatorWithPadding, Trainer, TrainingArguments,
                          EarlyStoppingCallback, set_seed)
from huggingface_hub import HfApi
from IPython.display import display

set_seed(SEED)
if not torch.cuda.is_available():
    raise RuntimeError("Activa GPU A100 en Colab antes de entrenar.")
GPU_NAME = torch.cuda.get_device_name(0)
if REQUIRE_A100 and "A100" not in GPU_NAME:
    raise RuntimeError(f"GPU asignada: {GPU_NAME}. Cambia a A100 o ajusta REQUIRE_A100.")
USE_BF16 = torch.cuda.is_bf16_supported()
torch.backends.cuda.matmul.allow_tf32 = False
torch.backends.cudnn.allow_tf32 = False
OUTPUT_ROOT.mkdir(parents=True, exist_ok=True)

def save_json(path, value):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2, ensure_ascii=False, default=str) + "\n", encoding="utf-8")

def sha256(path):
    h = hashlib.sha256()
    with Path(path).open("rb") as f:
        for block in iter(lambda: f.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()

def freeze_json(path, value):
    path = Path(path)
    if path.exists() and json.loads(path.read_text(encoding="utf-8")) != value:
        raise ValueError(f"RUN_ID ya tiene otra configuración o datos: {path.name}. Usa otro RUN_ID.")
    save_json(path, value)

def read_jsonl(path):
    with Path(path).open(encoding="utf-8-sig") as f:
        for n, line in enumerate(f, 1):
            if line.strip():
                try:
                    row = json.loads(line)
                except json.JSONDecodeError as e:
                    raise ValueError(f"JSON inválido: {path}:{n}") from e
                if not isinstance(row, dict):
                    raise ValueError(f"Se esperaba un objeto: {path}:{n}")
                yield row

def unique_index(rows, name):
    index = {}
    for row in rows:
        key = row["inst_key"]
        if key in index:
            raise ValueError(f"inst_key repetida en {name}: {key}")
        index[key] = row
    return index

ENVIRONMENT = {"python": sys.version, "torch": torch.__version__,
               "cuda": torch.version.cuda, "gpu": GPU_NAME,
               "gpu_memory_gib": torch.cuda.get_device_properties(0).total_memory / 2**30,
               "bf16": USE_BF16,
               "packages": {p.split("==")[0]: importlib.metadata.version(p.split("==")[0]) for p in PINNED}}
freeze_json(OUTPUT_ROOT / "request_manifest.json", {
    "variant": VARIANT, "seed": SEED, "split_seed": SPLIT_SEED, "val_frac": VAL_FRAC,
    "max_length": MAX_LENGTH, "context_budget": CONTEXT_BUDGET, "epochs": EPOCHS,
    "lr": LEARNING_RATE, "train_batch": TRAIN_BATCH, "grad_accum": GRAD_ACCUM,
    "eval_batch": EVAL_BATCH, "gold_final": GOLD_FINAL, "run_test": RUN_TEST,
    "ids_dir": str(IDS_DIR), "batch_dir": str(BATCH_DIR), "labels": LABELS,
    "gold_hashes": {str(p): sha256(p) for p in GOLD_FILES},
    "metadata_hashes": {p.name: sha256(p) for p in sorted(IDS_DIR.glob("*.json*"))},
    "environment": ENVIRONMENT,
})
save_json(OUTPUT_ROOT / "environment.json", ENVIRONMENT)
print(json.dumps(ENVIRONMENT, indent=2))
''')

step(r'''
## 3. Verificar los archivos de G15 y sus hashes

El manifiesto declara 31.265 filas V0 y 3.510 paquetes propios de prueba contando
activos, reserva y colchón. **No son 3.510 etiquetas humanas finales.** Todos sus
citantes se excluyen antes del split, aunque algún paquete nunca llegue a anotarse.
Los archivos de calibración eval60/calib30/calib2 no son entrenamiento ni prueba.

Esta celda verifica todos los hashes locales declarados. El pool completo es
opcional: aporta votos, licencias y localizadores, pero no sustituye los lotes con texto.
Si está presente, se comprueba contra su hash de origen. Los cuatro muestreos de A3
no se exigen porque aquí se consume su derivado congelado `test_set_ids_G15`.
''', r'''
manifest_path = IDS_DIR / "manifest_training_v1_G15.json"
if not manifest_path.exists():
    raise FileNotFoundError(f"Sube TrainingData_Grupo15 y ajusta IDS_DIR: {manifest_path}")
manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
assert manifest["group"] == "G15" and manifest["test_set"] == "B"
assert manifest["variant"] == "V0"
input_hashes = {}
for filename, expected in manifest["files"].items():
    path = IDS_DIR / filename
    actual = sha256(path)
    if actual != expected:
        raise ValueError(f"Hash distinto al manifiesto: {filename}")
    input_hashes[str(path)] = actual
input_hashes[str(manifest_path)] = sha256(manifest_path)
if POOL_PATH.is_file():
    actual = sha256(POOL_PATH)
    if actual != manifest["pool_sha256"]:
        raise ValueError("El pool no corresponde al manifiesto de entrenamiento.")
    input_hashes[str(POOL_PATH)] = actual

train_v0 = list(read_jsonl(IDS_DIR / "training_v1_G15.jsonl"))
test_ids = list(read_jsonl(IDS_DIR / "test_set_ids_G15.jsonl"))
train_index = unique_index(train_v0, "training_v1_G15")
test_index = unique_index(test_ids, "test_set_ids_G15")
assert len(train_v0) == manifest["rows_kept"]
assert len(test_ids) == manifest["test_set_ids"]
assert not (train_index.keys() & test_index.keys())
for row in train_v0 + test_ids:
    citing, para, span, cited = row["inst_key"].split("|")
    assert citing == row["citing_paper_id"] and cited == row["cited_paper_id"]
    assert citing != cited
    assert row["group_key"].startswith(f"{citing}|{para}|")
assert all(r["high_confidence"] and r["primary_pre_label"] in LABEL2ID for r in train_v0)
assert all(r["set"] == "B" for r in test_ids)
print(f"V0: {len(train_v0):,} filas; paquetes propios excluidos: {len(test_ids):,}.")
''')

step(r'''
## 4. Cuantificar V0/V1/V2 y aplicar el aislamiento elegido

Se interpretan literalmente las listas por `role`: `citing` comprueba el citante y
`cited` el citado. V2 ya contiene las reglas para ambos papeles. No se simplifica a
una lista genérica que cambie el significado de V0 o V1.

Se registra la pérdida por clase antes de elegir. V0 permite más datos y requiere
reportar después el rendimiento sobre citados vistos/no vistos. V1/V2 sacrifican
datos, especialmente de las clases escasas. La comparación de configuraciones
usa siempre la misma variante y las mismas instancias.
''', r'''
def exclusion_rules(rows):
    rules = {"citing": set(), "cited": set()}
    for row in rows:
        if row["group"] != "G15" or row["role"] not in rules:
            raise ValueError(f"Regla de exclusión inesperada: {row}")
        rules[row["role"]].add(row["paper_id"])
    return rules

def excluded(row, rules):
    return (row["citing_paper_id"] in rules["citing"] or
            row["cited_paper_id"] in rules["cited"])

RULES = {v: exclusion_rules(read_jsonl(IDS_DIR / f"exclusion_list_G15_{v}.jsonl"))
         for v in ("V0", "V1", "V2")}
assert not any(excluded(r, RULES["V0"]) for r in train_v0)
variant_rows = {v: [r for r in train_v0 if not excluded(r, rules)] for v, rules in RULES.items()}
impact = pd.DataFrame({v: collections.Counter(r["primary_pre_label"] for r in rows)
                       for v, rows in variant_rows.items()}).reindex(LABELS).fillna(0).astype(int)
impact.loc["TOTAL"] = impact.sum()
impact.to_csv(OUTPUT_ROOT / "isolation_impact.csv")
display(impact)
eligible = [dict(r) for r in variant_rows[VARIANT]]
assert not ({r["citing_paper_id"] for r in eligible} & {r["citing_paper_id"] for r in test_ids})
save_json(OUTPUT_ROOT / "isolation_summary.json", {
    "variant": VARIANT, "pool_high_conf_rows": manifest["high_conf_rows"],
    "removed_to_v0": manifest["rows_removed"], "v0_rows": len(train_v0),
    "removed_beyond_v0": len(train_v0) - len(eligible), "eligible_rows": len(eligible),
})
''')

step(r'''
## 5. Incorporar gold humano disponible sin usar T_B para entrenamiento

Se acepta `gold_primary` unido exclusivamente por `inst_key`. Si no hay archivos
gold, entrenamiento y validación usan las pre-etiquetas de A2, incluido T_A.
Cuando hay gold final de T_A se reemplaza su pre-etiqueta; `unclear` se elimina.
Las secundarias no se usan para esta clasificación de etiqueta única.

Los archivos gold pueden contener ambos conjuntos: las claves de T_B jamás se
añaden a train/val. Un `gold_primary=null` significa aún sin resolver y mantiene
la pre-etiqueta en train/val. Un archivo con correcciones conflictivas requiere
consolidación explícita; no se resuelve por orden de lectura. Cambiar gold exige
otro `RUN_ID` y reentrenar las dos configuraciones para compararlas.
''', r'''
gold = {}
for filename in GOLD_FILES:
    path = Path(filename)
    input_hashes[str(path)] = sha256(path)
    for row in read_jsonl(path):
        key = row["inst_key"]
        label = row.get("gold_primary")
        if label is None:
            continue
        if label not in LABEL2ID and label != "unclear":
            raise ValueError(f"Gold desconocido: {key}: {label}")
        if key in gold and gold[key] != label:
            raise ValueError(f"Gold conflictivo; consolida versiones: {key}")
        gold[key] = label

removed_unclear = []
labeled = []
for row in eligible:
    key = row["inst_key"]
    label = gold.get(key, row["primary_pre_label"])
    if label == "unclear":
        removed_unclear.append(key)
        continue
    row["label"] = label
    row["label_source"] = "human_gold" if key in gold else "pre_label"
    labeled.append(row)
test_rows = []
if RUN_TEST:
    for row in test_ids:
        label = gold.get(row["inst_key"])
        if label in LABEL2ID:
            test_rows.append({**row, "label": label, "label_source": "human_gold"})
    counts = collections.Counter(r["label"] for r in test_rows)
    if any(counts[label] < 300 for label in LABELS):
        raise ValueError(f"T_B no alcanza 300 gold válidos por clase: {dict(counts)}. Cierra A3.")
save_json(OUTPUT_ROOT / "label_provenance.json", {
    "train_val_sources": dict(collections.Counter(r["label_source"] for r in labeled)),
    "removed_unclear_keys": removed_unclear, "final_test_enabled": RUN_TEST,
    "human_test_rows": len(test_rows),
})
print("Fuentes train/val:", collections.Counter(r["label_source"] for r in labeled))
print("Test humano habilitado:", RUN_TEST, "filas:", len(test_rows))
''')

step(r'''
## 6. Crear una sola partición train/val y auditarla

El hash del citante, con semilla fija, asigna aproximadamente el 10% a validación.
La proporción exacta por clase puede variar; se exige presencia de las nueve clases
en ambas particiones y se publican sus conteos. Esta asignación no depende de los
textos ni de predicciones. El grupo de citas y el par citante–citado quedan juntos.

En V1 se purga además de train todo citado presente en val; en V2 se purgan ambos
roles de cualquier documento de val. La val no se modifica para favorecer resultados.
Si el suministro resulta insuficiente, se revisa el diseño antes de entrenar.
Los archivos de partición exportados contienen claves, etiquetas y procedencia, sin texto.
''', r'''
def validation_citing(citing_id):
    digest = hashlib.sha256(f"{SPLIT_SEED}|val|{citing_id}".encode()).hexdigest()
    return int(digest[:16], 16) / 2**64 < VAL_FRAC

val_rows = [r for r in labeled if validation_citing(r["citing_paper_id"])]
tr_before_purge = [r for r in labeled if not validation_citing(r["citing_paper_id"])]
val_citing = {r["citing_paper_id"] for r in val_rows}
val_cited = {r["cited_paper_id"] for r in val_rows}
if VARIANT == "V0":
    train_rows = tr_before_purge
elif VARIANT == "V1":
    train_rows = [r for r in tr_before_purge if r["cited_paper_id"] not in val_cited]
else:
    val_docs = val_citing | val_cited
    train_rows = [r for r in tr_before_purge if r["citing_paper_id"] not in val_docs
                  and r["cited_paper_id"] not in val_docs]
assert train_rows and val_rows
splits = {"train": train_rows, "validation": val_rows}
if RUN_TEST:
    splits["test"] = test_rows
for a, ar in splits.items():
    assert all(r["label"] in LABEL2ID for r in ar)
    if a != "test":
        assert not any(excluded(r, RULES[VARIANT]) for r in ar)
    for b, br in splits.items():
        if a >= b:
            continue
        for key in ("inst_key", "group_key", "citing_paper_id"):
            assert not ({r[key] for r in ar} & {r[key] for r in br}), (a, b, key)
        if VARIANT == "V1":
            assert not ({r["cited_paper_id"] for r in ar} & {r["cited_paper_id"] for r in br})
        if VARIANT == "V2":
            da = {r[k] for r in ar for k in ("citing_paper_id", "cited_paper_id")}
            db = {r[k] for r in br for k in ("citing_paper_id", "cited_paper_id")}
            assert not da & db
counts = pd.DataFrame({s: collections.Counter(r["label"] for r in rows)
                       for s, rows in splits.items()}).reindex(LABELS).fillna(0).astype(int)
if (counts[["train", "validation"]] == 0).any().any():
    raise ValueError("Alguna clase está ausente en train o val. Revisa el diseño del split.")
display(counts)
counts.to_csv(OUTPUT_ROOT / "split_class_counts.csv")
KEY_FIELDS = ["inst_key", "group_key", "citing_paper_id", "cited_paper_id", "label", "label_source", "source_batch"]
split_hashes = {}
for name, rows in splits.items():
    rows.sort(key=lambda r: r["inst_key"])
    path = OUTPUT_ROOT / f"split_{name}_ids.jsonl"
    content = "".join(json.dumps({k: r[k] for k in KEY_FIELDS}, ensure_ascii=False, sort_keys=True) + "\n" for r in rows)
    split_hashes[name] = hashlib.sha256(content.encode()).hexdigest()
    path.write_text(content, encoding="utf-8")
save_json(OUTPUT_ROOT / "split_summary.json", {
    "split_seed": SPLIT_SEED, "validation_fraction_target": VAL_FRAC,
    "removed_for_validation_isolation": len(tr_before_purge) - len(train_rows),
    "rows": {k: len(v) for k, v in splits.items()}, "hashes": split_hashes,
    "temporal_split": False, "section_stratification": False,
})
''')

step(r'''
## 7. Localizar los lotes y revisar su esquema real

Se necesitan estos ocho archivos en `a2/batches_norw/`:
`pilot_random_1500`, `pool_single_7000`, `pool_cue_eg`, `pool_cue_cmp`,
`pool_cue_rare`, `pool_cue_yield`, `pool_cue_basis`, `pool_ext_cue_rare` (todos `.jsonl`).

El esquema se verificó con los ocho lotes locales de `A4/a2/batches_norw/`:
el contexto está en `context` y los fragmentos en `top3`. Esta celda vuelve a mostrar
claves y tipos sin imprimir textos. Si se utiliza una nueva versión con otro esquema,
editar `BATCH_FIELDS`/`CHUNK_FIELDS` con los nombres reales antes de continuar.
Para campos anidados usar puntos, p. ej. `cited.title`.
No se inventan textos ni se cruzan filas por orden o por parecido.

Si los lotes no llevan `inst_key`, se necesita el adaptador original de A2 que la
construya a partir de sus localizadores; el notebook se detiene para evitar uniones falsas.
''', r'''
BATCH_FIELDS = {
    "inst_key": "inst_key", "context": "context",
    "title": "cited_title", "abstract": "cited_abstract", "chunks": "top3",
}
CHUNK_FIELDS = {"text": "text", "section": "section"}

def field_at(row, dotted):
    value = row
    for part in dotted.split("."):
        if not isinstance(value, dict) or part not in value:
            raise KeyError(f"Campo '{dotted}' ausente. Ajusta el adaptador con el esquema real.")
        value = value[part]
    return value

required_batches = sorted({r["source_batch"] for rows in splits.values() for r in rows})
batch_paths = {name: BATCH_DIR / f"{name}.jsonl" for name in required_batches}
missing = [str(p) for p in batch_paths.values() if not p.is_file()]
if missing:
    raise FileNotFoundError("Faltan lotes con texto; descárgalos de a2/batches_norw/:\n" + "\n".join(missing))
for name, path in batch_paths.items():
    first = next(read_jsonl(path), None)
    if first is None:
        raise ValueError(f"Lote vacío: {name}")
    print(name, {k: type(v).__name__ for k, v in first.items()})
    chunks = field_at(first, BATCH_FIELDS["chunks"])
    if isinstance(chunks, list) and chunks:
        print("  primer chunk:", {k: type(v).__name__ for k, v in chunks[0].items()})
freeze_json(OUTPUT_ROOT / "batch_manifest.json", {
    "hashes": {name: sha256(path) for name, path in batch_paths.items()},
    "batch_fields": BATCH_FIELDS, "chunk_fields": CHUNK_FIELDS,
})
print("Si el esquema coincide, continúa. Si difiere, corrige el adaptador y repite esta celda.")
''')

step(r'''
## 8. Reconstruir texto por clave y controlar calidad

Se leen secuencialmente solo los ocho lotes y se conservan en memoria las instancias
requeridas. Cada fila debe tener un único `[[TARGET]]`, título, resumen y exactamente
tres fragmentos en el orden de recuperación. Los lotes reales contienen algunas
secciones vacías: se representan como `Unknown` y se cuentan en la auditoría, sin
inventar una sección retórica ni eliminar la instancia. Un texto faltante o una
clave duplicada detiene la ejecución. No se descartan silenciosamente filas distintas
en cada configuración. La etiqueta, los votos y los identificadores no forman parte
del texto de entrada del modelo.

Los datos reconstruidos permanecen en memoria; no se exporta el corpus textual.
''', r'''
def require_text(value, name):
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"Texto vacío o tipo incorrecto: {name}")
    return value.strip()

def normalize_batch(row):
    out = {k: require_text(field_at(row, BATCH_FIELDS[k]), k)
           for k in ("inst_key", "context", "title", "abstract")}
    if out["context"].count("[[TARGET]]") != 1:
        raise ValueError(f"Se requiere un [[TARGET]] por contexto: {out['inst_key']}")
    if "{{cite:" in out["context"]:
        raise ValueError("Quedan marcadores crudos. Usa el renderizador congelado de A2.")
    raw_chunks = field_at(row, BATCH_FIELDS["chunks"])
    if not isinstance(raw_chunks, list) or len(raw_chunks) != 3:
        raise ValueError(f"Top-3 incompleto: {out['inst_key']}")
    out["chunks"] = []
    for ch in raw_chunks:
        text = require_text(field_at(ch, CHUNK_FIELDS["text"]), "chunk.text")
        section = field_at(ch, CHUNK_FIELDS["section"])
        if section is not None and not isinstance(section, str):
            raise ValueError(f"Tipo incorrecto de sección: {out['inst_key']}")
        missing_section = section is None or not section.strip()
        out["chunks"].append({"text": text, "section": "Unknown" if missing_section else section.strip(),
                              "section_missing": missing_section})
    return out

needed = {r["inst_key"]: r["source_batch"] for rows in splits.values() for r in rows}
texts = {}
for batch, path in batch_paths.items():
    input_hashes[str(path)] = sha256(path)
    seen_batch = set()
    for raw in read_jsonl(path):
        key = field_at(raw, BATCH_FIELDS["inst_key"])
        if key in seen_batch:
            raise ValueError(f"Clave duplicada en {batch}: {key}")
        seen_batch.add(key)
        if key in needed and needed[key] == batch:
            texts[key] = normalize_batch(raw)
missing_keys = sorted(needed.keys() - texts.keys())
if missing_keys:
    raise ValueError(f"Sin reconstruir: {len(missing_keys)}. Primeras claves: {missing_keys[:5]}")
assert len(texts) == len(needed)
save_json(OUTPUT_ROOT / "reconstruction_audit.json", {
    "required_rows": len(needed), "reconstructed_rows": len(texts),
    "batches": required_batches, "adapter": BATCH_FIELDS, "chunk_adapter": CHUNK_FIELDS,
    "rows_with_missing_section": sum(any(ch["section_missing"] for ch in ex["chunks"]) for ex in texts.values()),
    "chunks_with_missing_section": sum(ch["section_missing"] for ex in texts.values() for ch in ex["chunks"]),
})
section_rows = []
for split, rows in splits.items():
    cnt = collections.Counter(ch["section"] for r in rows for ch in texts[r["inst_key"]]["chunks"])
    section_rows.extend({"split": split, "section": sec, "chunks": n} for sec, n in cnt.items())
pd.DataFrame(section_rows).to_csv(OUTPUT_ROOT / "section_distribution.csv", index=False)
print(f"Reconstruidas {len(texts):,} instancias con ambas configuraciones completas.")
''')

step(r'''
## 9. Resolver el límite de 512 tokens sin perder la cita objetivo

SciBERT admite 512 tokens incluyendo `[CLS]` y los dos `[SEP]` del par. Se reserva
una ventana de hasta **192 tokens del contexto**, centrada en `[[TARGET]]`; es idéntica
en las dos configuraciones. El resto del presupuesto se usa para el citado:

- Base: título (hasta 64 tokens) y abstract con el espacio restante.
- Fragmentos: presupuesto repartido entre los tres, con sección (hasta 24 tokens)
  y texto de cada uno; el espacio sobrante se redistribuye.

Es una decisión de A4: A1 evitaba truncar contextos, pero concatenar toda la evidencia
supera el límite. Aquí se registra cuánto se recorta y siempre se conserva el marcador.
Se añaden cinco marcadores al vocabulario, cuyas representaciones se aprenden en el
ajuste. La política y el tokenizador se exportan juntos para inferencia idéntica.
''', r'''
MODEL_ID = "allenai/scibert_scivocab_uncased"
previous_spec = OUTPUT_ROOT / "run_manifest.json"
MODEL_REVISION = (json.loads(previous_spec.read_text(encoding="utf-8"))["model_revision"]
                  if previous_spec.exists() else HfApi().model_info(MODEL_ID).sha)
tokenizer = AutoTokenizer.from_pretrained(MODEL_ID, revision=MODEL_REVISION, use_fast=True)
MARKERS = ["[[TARGET]]", "[CITE]", "[FORMULA]", "[FIGURE]", "[TABLE]"]
tokenizer.add_special_tokens({"additional_special_tokens": MARKERS})
TARGET_ID = tokenizer.convert_tokens_to_ids("[[TARGET]]")

def fair_caps(lengths, budget):
    caps = [0] * len(lengths)
    remaining = budget
    while remaining and any(c < n for c, n in zip(caps, lengths)):
        for i, n in enumerate(lengths):
            if remaining and caps[i] < n:
                caps[i] += 1
                remaining -= 1
    return caps

def encode_example(example, config, tok, max_length=512, context_budget=192):
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
    elif config == "fragmentos":
        sections = [ids(f"Section: {ch['section']} Passage: ")[:24] for ch in example["chunks"]]
        bodies = [ids(ch["text"]) for ch in example["chunks"]]
        caps = fair_caps([len(h) + len(b) for h, b in zip(sections, bodies)], budget)
        evidence = []
        for i, (head, body, cap) in enumerate(zip(sections, bodies, caps), 1):
            kept = (head + body)[:cap]
            if len(kept) <= len(head):
                raise ValueError("Presupuesto insuficiente para conservar texto de cada chunk.")
            evidence.extend(kept)
            stats[f"chunk{i}_original"] = len(head) + len(body)
            stats[f"chunk{i}_kept"] = len(kept)
        stats.update(evidence_original=sum(len(h) + len(b) for h, b in zip(sections, bodies)),
                     evidence_kept=len(evidence))
    else:
        raise ValueError(config)
    input_ids = [tok.cls_token_id] + context_cut + [tok.sep_token_id] + evidence + [tok.sep_token_id]
    token_types = [0] * (len(context_cut) + 2) + [1] * (len(evidence) + 1)
    assert len(input_ids) <= max_length and len(token_types) == len(input_ids)
    stats["total_tokens"] = len(input_ids)
    return {"input_ids": input_ids, "attention_mask": [1] * len(input_ids),
            "token_type_ids": token_types}, stats

encoded = {}
audit_rows = []
for config in CONFIGS:
    encoded[config] = {}
    for split, rows in splits.items():
        features = []
        for row in rows:
            features_row, stats = encode_example(texts[row["inst_key"]], config, tokenizer,
                                                  MAX_LENGTH, CONTEXT_BUDGET)
            features.append({**features_row, "labels": LABEL2ID[row["label"]]})
            audit_rows.append({"config": config, "split": split, "inst_key": row["inst_key"], **stats})
        encoded[config][split] = Dataset.from_list(features)
audit = pd.DataFrame(audit_rows)
audit["context_truncated"] = audit.context_kept < audit.context_original
audit["evidence_truncated"] = audit.evidence_kept < audit.evidence_original
audit.to_csv(OUTPUT_ROOT / "token_budget_audit.csv", index=False)
display(audit.groupby(["config", "split"])[["total_tokens", "context_truncated", "evidence_truncated"]].mean())
''')

step(r'''
## 10. Congelar el experimento y medir una referencia simple

Se guarda la revisión de SciBERT, versiones, hashes de datos y particiones, adaptador
y parámetros. Una ejecución existente con otra configuración se rechaza: cambiar
`RUN_ID`. Este manifiesto permite retomar entrenamiento sin mezclar datasets.

La referencia mayoritaria se aprende en train y se evalúa en val. Val contiene
principalmente etiquetas de jueces: sus métricas sirven para seleccionar checkpoints,
no equivalen a desempeño humano sobre T_B. El test no participa en selección de
épocas, variantes, learning rate ni política de tokens.
''', r'''
run_spec = {
    "group": "G15", "test_set": "B", "isolation": VARIANT,
    "model_id": MODEL_ID, "model_revision": MODEL_REVISION, "seed": SEED,
    "split_seed": SPLIT_SEED, "split_hashes": split_hashes, "input_hashes": input_hashes,
    "labels": LABELS, "markers": MARKERS, "max_length": MAX_LENGTH,
    "context_budget": CONTEXT_BUDGET, "title_budget": 64, "section_budget": 24,
    "epochs": EPOCHS, "learning_rate": LEARNING_RATE, "train_batch": TRAIN_BATCH,
    "gradient_accumulation": GRAD_ACCUM, "eval_batch": EVAL_BATCH,
    "weight_decay": 0.01, "warmup_ratio": 0.1, "early_stopping_patience": 2,
    "loss": "unweighted_cross_entropy", "gold_final": GOLD_FINAL, "run_test": RUN_TEST,
    "batch_fields": BATCH_FIELDS, "chunk_fields": CHUNK_FIELDS, "environment": ENVIRONMENT,
}
spec_path = OUTPUT_ROOT / "run_manifest.json"
if spec_path.exists():
    old_spec = json.loads(spec_path.read_text(encoding="utf-8"))
    if old_spec != run_spec:
        raise ValueError("RUN_ID ya existe con otro manifiesto. Usa otro RUN_ID.")
save_json(spec_path, run_spec)
majority = collections.Counter(r["label"] for r in train_rows).most_common(1)[0][0]
y_val = [LABEL2ID[r["label"]] for r in val_rows]
baseline_metrics = {"class": majority,
    "validation_macro_f1": f1_score(y_val, [LABEL2ID[majority]] * len(y_val),
                                     labels=list(ID2LABEL), average="macro", zero_division=0)}
save_json(OUTPUT_ROOT / "majority_baseline.json", baseline_metrics)
print(baseline_metrics)
''')

step(r'''
## 10.1. Activar MLflow y recuperar el historial de Drive

Se restaura el último snapshot completo antes de abrir la base SQLite local.
Se conserva MLflow 3.17.2, compatible con el visor instalado en AWS.
**Ejecutar una sola sesión escritora de Colab a la vez**, incluido el notebook de instalación.
El experimento real se llama `G15_A4_SciBERT`; cada configuración tiene un padre y
cada intento de entrenamiento un hijo. El experimento de instalación queda separado.

Se publican snapshots verificados al iniciar, cada 300 segundos comprobados al
terminar un paso de optimización, en cada checkpoint y al cerrar cada intento.
La copia pausa brevemente el entrenamiento; no es un temporizador independiente.
Durante preparación/evaluaciones largas no se promete una copia cada cinco minutos.
Una desconexión brusca puede perder métricas posteriores al último snapshot;
la recuperación del entrenamiento parte del último checkpoint de época completo.
Los fallos de respaldo detienen el entrenamiento para evitar continuar sin protección.

Pesos, optimizador y ZIP de modelos quedan en Drive; MLflow guarda reportes,
manifiestos, curvas y referencias. Los snapshots no duplican los pesos.
`report_to="none"` desactiva integraciones automáticas: el callback propio registra
en MLflow los intentos sin duplicar runs ni cargar los modelos como artefactos.
''', Path(__file__).with_name("tracking_runtime.py").read_text(encoding="utf-8") + r'''

import re
assert re.fullmatch(r"[A-Za-z0-9_-]+", RUN_ID), "RUN_ID: usa letras, números, _ y -."
tracking = A4Tracking(Path("/opt/maia/a4_tracking"), RESULTS_ROOT / "a4/_tracking/snapshots",
                      OUTPUT_ROOT, RUN_ID, SNAPSHOT_INTERVAL_SECONDS)
print("MLflow listo:", tracking.experiment, "en", mlflow.get_tracking_uri())
''')

step(r'''
## 11. Entrenar primero base y después fragmentos

Cada configuración parte otra vez del encoder preentrenado; **fragmentos no continúa
el modelo base**. Se elige el mejor checkpoint por F1 macro en la misma validación,
con hasta cuatro épocas y parada temprana de paciencia dos. CE sin ponderar sigue
la propuesta; no se recorta Background ni se duplica la minoría. Cualquier experimento
con pesos por clase deberá usar otro RUN_ID y decidirse con val.

Los checkpoints de cada época quedan en Drive para recuperar una sesión de Colab.
`save_total_limit=2` limita espacio. Si hay OOM, bajar TRAIN_BATCH y subir GRAD_ACCUM
para mantener batch efectivo 32, con una nueva ejecución documentada.

Al terminar cada modelo se exportan encoder+cabeza, tokenizador, contrato de entrada,
política de tokens y código de inferencia. La exportación base sirve para integrar v0.
La probabilidad softmax se presenta como puntaje **sin calibrar**.
''', r'''
import inspect
from transformers.trainer_utils import get_last_checkpoint

def compute_metrics(prediction):
    logits = prediction.predictions
    if isinstance(logits, tuple):
        logits = logits[0]
    pred = np.asarray(logits).argmax(axis=-1)
    y = prediction.label_ids
    p, r, f, _ = precision_recall_fscore_support(y, pred, labels=list(ID2LABEL),
                                               average="macro", zero_division=0)
    return {"accuracy": accuracy_score(y, pred), "precision_macro": p,
            "recall_macro": r, "f1_macro": f,
            "f1_micro": f1_score(y, pred, labels=list(ID2LABEL), average="micro", zero_division=0)}

INFERENCE_TEMPLATE = """import json
from pathlib import Path
import torch
from transformers import AutoTokenizer, AutoModelForSequenceClassification

__ENCODER__

class CitationClassifier:
    def __init__(self, model_dir, device=None):
        self.root = Path(model_dir)
        self.policy = json.loads((self.root / "input_policy.json").read_text(encoding="utf-8"))
        self.tokenizer = AutoTokenizer.from_pretrained(self.root, local_files_only=True)
        self.device = device or ("cuda" if torch.cuda.is_available() else "cpu")
        self.model = AutoModelForSequenceClassification.from_pretrained(self.root, local_files_only=True).to(self.device).eval()

    def predict(self, example):
        features, stats = encode_example(example, self.policy["config"], self.tokenizer,
                                         self.policy["max_length"], self.policy["context_budget"])
        batch = {k: torch.tensor([v], device=self.device) for k, v in features.items()}
        with torch.inference_mode():
            probs = self.model(**batch).logits.float().softmax(-1)[0].cpu().tolist()
        best = max(range(len(probs)), key=probs.__getitem__)
        return {"label": self.model.config.id2label[best], "score": probs[best],
                "scores": {self.model.config.id2label[i]: p for i, p in enumerate(probs)},
                "score_calibrated": False, "token_audit": stats}
"""

# IPython conserva el código fuente de funciones definidas en sus celdas.
ENCODER_SOURCE = inspect.getsource(fair_caps) + "\n" + inspect.getsource(encode_example)
validation_results = []
for config in CONFIGS:
    workdir = OUTPUT_ROOT / config
    checkpoint_dir = workdir / "checkpoints"
    if RESUME and (workdir / "TRAINING_COMPLETE.json").exists():
        manifest = json.loads((workdir / "TRAINING_COMPLETE.json").read_text())
        for name, digest in manifest["model_hashes"].items():
            assert sha256(workdir / "model" / name) == digest
        validation_results.append(json.loads((workdir / "validation_metrics.json").read_text()))
        parent_id = tracking.parent(config)
        tracking.client.set_tag(parent_id, "drive_output", str(workdir))
        tracking.reports(config)
        tracking.client.set_terminated(parent_id, "FINISHED")
        tracking.backup(force=True)
        print(config, "ya entrenado y verificado; se omite entrenamiento.")
        continue
    last = verified_checkpoint(checkpoint_dir) if checkpoint_dir.exists() else None
    if (last or (workdir / "model/config.json").exists()) and not RESUME:
        raise ValueError(f"{config} ya tiene entrenamiento. Usa otro RUN_ID o RESUME=True.")
    with tracking.attempt(config, run_spec, last) as attempt_id:
        set_seed(SEED)
        model = AutoModelForSequenceClassification.from_pretrained(
            MODEL_ID, revision=MODEL_REVISION, num_labels=len(LABELS),
            id2label=ID2LABEL, label2id=LABEL2ID, problem_type="single_label_classification",
            attn_implementation="eager",
        )
        model.resize_token_embeddings(len(tokenizer), mean_resizing=False)
        args = TrainingArguments(
            output_dir=str(checkpoint_dir), num_train_epochs=EPOCHS,
            learning_rate=LEARNING_RATE, per_device_train_batch_size=TRAIN_BATCH,
            gradient_accumulation_steps=GRAD_ACCUM, per_device_eval_batch_size=EVAL_BATCH,
            weight_decay=0.01, warmup_ratio=0.1, lr_scheduler_type="linear",
            eval_strategy="epoch", save_strategy="epoch", logging_strategy="steps", logging_steps=50,
            load_best_model_at_end=True, metric_for_best_model="f1_macro", greater_is_better=True,
            save_total_limit=2, save_safetensors=True, seed=SEED, data_seed=SEED,
            restore_callback_states_from_checkpoint=True,
            bf16=USE_BF16, fp16=not USE_BF16, tf32=False, full_determinism=True,
            dataloader_num_workers=2, dataloader_pin_memory=True,
            optim="adamw_torch", report_to="none", push_to_hub=False,
        )
        trainer = Trainer(model=model, args=args, train_dataset=encoded[config]["train"],
            eval_dataset=encoded[config]["validation"], processing_class=tokenizer,
            data_collator=DataCollatorWithPadding(tokenizer, pad_to_multiple_of=8),
            compute_metrics=compute_metrics,
            callbacks=[EarlyStoppingCallback(early_stopping_patience=2), A4MLflowCallback(tracking, attempt_id)])
        torch.cuda.reset_peak_memory_stats()
        started = time.perf_counter()
        train_result = trainer.train(resume_from_checkpoint=last if RESUME and last else None)
        torch.cuda.synchronize()
        elapsed = time.perf_counter() - started
        val_metrics = trainer.evaluate()
        export_dir = workdir / "model"
        trainer.save_model(str(export_dir))
        tokenizer.save_pretrained(export_dir)
        policy = {"config": config, "max_length": MAX_LENGTH, "context_budget": CONTEXT_BUDGET,
                  "markers": MARKERS, "model_revision": MODEL_REVISION, "score_calibrated": False}
        save_json(export_dir / "input_policy.json", policy)
        save_json(export_dir / "label_mapping.json", {"label2id": LABEL2ID, "id2label": ID2LABEL})
        save_json(export_dir / "run_manifest.json", run_spec)
        (export_dir / "inference.py").write_text(INFERENCE_TEMPLATE.replace("__ENCODER__", ENCODER_SOURCE), encoding="utf-8")
        contract = {"config": config, "required_input": ["context", "title", "abstract"] if config == "base"
                    else ["context", "chunks: lista de 3 objetos {text, section}"],
                    "context_target": "Exactamente un [[TARGET]]; otros marcadores según guía rev3.1",
                    "output": {"label": "una de 9 clases", "score": "softmax sin calibrar", "scores": "9 probabilidades"}}
        save_json(export_dir / "api_contract.json", contract)
        result = {"config": config, **val_metrics, "elapsed_session_seconds": elapsed,
                  "peak_gpu_allocated_gib": torch.cuda.max_memory_allocated() / 2**30,
                  "best_checkpoint": trainer.state.best_model_checkpoint,
                  "best_validation_macro_f1": trainer.state.best_metric,
                  "train_metrics": train_result.metrics}
        save_json(workdir / "validation_metrics.json", result)
        save_json(workdir / "training_log.json", trainer.state.log_history)
        model_hashes = {p.relative_to(export_dir).as_posix(): sha256(p)
                        for p in export_dir.rglob("*") if p.is_file()}
        save_json(workdir / "TRAINING_COMPLETE.json", {"model_hashes": model_hashes,
                  "model_dir": str(export_dir), "attempt_id": attempt_id})
        tracking.metrics(attempt_id, val_metrics, trainer.state.global_step)
        tracking.metrics(attempt_id, {"elapsed_session_seconds": elapsed,
            "peak_gpu_allocated_gib": result["peak_gpu_allocated_gib"]}, trainer.state.global_step)
        validation_results.append(result)
        print(config, "exportado en", export_dir, "F1 macro val:", val_metrics["eval_f1_macro"])
        del trainer, model
        gc.collect()
        torch.cuda.empty_cache()
display(pd.DataFrame(validation_results).drop(columns=["train_metrics"]))
''')

step(r'''
## 12. Comprobar la exportación y guardar predicciones de validación

Se recarga el artefacto desde disco con su módulo de inferencia y se verifica que las
predicciones coincidan con la entrada tokenizada usada al entrenar. Las predicciones
se guardan por `inst_key`, sin texto, con probabilidades para las nueve clases.

Solo se procesa validación aquí. Sus matrices de confusión y métricas por clase
permiten revisar si el desbalance afecta a las minoritarias. Para un resultado final
sobre funciones de cita hace falta el gold humano de T_B.
''', r'''
import importlib.util
import matplotlib.pyplot as plt

def load_export(config):
    root = OUTPUT_ROOT / config / "model"
    spec = importlib.util.spec_from_file_location(f"a4_inference_{config}", root / "inference.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module.CitationClassifier(root)

def predict_encoded(classifier, data):
    collator = DataCollatorWithPadding(classifier.tokenizer, pad_to_multiple_of=8)
    probabilities = []
    for start in range(0, len(data), EVAL_BATCH):
        items = [{k: v for k, v in data[i].items() if k != "labels"}
                 for i in range(start, min(start + EVAL_BATCH, len(data)))]
        batch = {k: v.to(classifier.device) for k, v in collator(items).items()}
        with torch.inference_mode():
            probabilities.extend(classifier.model(**batch).logits.float().softmax(-1).cpu().tolist())
    return np.asarray(probabilities)

def report_predictions(config, split, rows, probs):
    y = np.asarray([LABEL2ID[r["label"]] for r in rows])
    pred = probs.argmax(-1)
    report = classification_report(y, pred, labels=list(ID2LABEL), target_names=LABELS,
                                   output_dict=True, zero_division=0)
    root = OUTPUT_ROOT / config
    save_json(root / f"{split}_classification_report.json", report)
    metrics = {"config": config, "split": split, "n": len(rows),
               **compute_metrics(type("Prediction", (), {"predictions": probs, "label_ids": y})())}
    save_json(root / f"{split}_scores.json", metrics)
    frame = pd.DataFrame({"inst_key": [r["inst_key"] for r in rows],
                          "gold_or_prelabel": [r["label"] for r in rows],
                          "label_source": [r["label_source"] for r in rows],
                          "predicted_label": [ID2LABEL[int(x)] for x in pred]})
    for i, label in ID2LABEL.items():
        frame[f"p_{label}"] = probs[:, i]
    frame.to_csv(root / f"{split}_predictions.csv", index=False)
    cm = confusion_matrix(y, pred, labels=list(ID2LABEL))
    pd.DataFrame(cm, index=LABELS, columns=LABELS).to_csv(root / f"{split}_confusion.csv")
    short = ["BG", "Gap", "Basis", "Comp", "App", "I/M", "Evid", "Origin", "FR"]
    fig, ax = plt.subplots(figsize=(9, 8))
    im = ax.imshow(cm, cmap="Blues")
    ax.set(xticks=range(9), yticks=range(9), xticklabels=short, yticklabels=short,
           xlabel="Predicción", ylabel="Referencia", title=f"{config} · {split}")
    for i in range(9):
        for j in range(9):
            ax.text(j, i, str(cm[i, j]), ha="center", va="center",
                    color="white" if cm[i, j] > cm.max() / 2 else "black", fontsize=8)
    fig.colorbar(im, ax=ax)
    fig.tight_layout()
    fig.savefig(root / f"{split}_confusion.png", dpi=160)
    plt.show()
    plt.close(fig)
    tracking.metrics(tracking.parent(config), {f"{split}_{k}": v for k, v in metrics.items()})
    tracking.reports(config)
    tracking.backup(force=True)
    return metrics

val_summary = []
for config in CONFIGS:
    clf = load_export(config)
    sample = clf.predict(texts[val_rows[0]["inst_key"]])
    single = predict_encoded(clf, encoded[config]["validation"].select([0]))[0]
    assert np.allclose(single, [sample["scores"][k] for k in LABELS], atol=2e-5)
    probs = predict_encoded(clf, encoded[config]["validation"])
    val_summary.append(report_predictions(config, "validation", val_rows, probs))
    del clf
    gc.collect()
    torch.cuda.empty_cache()
pd.DataFrame(val_summary).to_csv(OUTPUT_ROOT / "validation_comparison.csv", index=False)
display(pd.DataFrame(val_summary))
''')

step(r'''
## 13. Evaluación final opcional sobre T_B humano

Esta sección se omite con la configuración inicial. Para la evaluación final, preparar
**una nueva ejecución** con el gold consolidado, `GOLD_FINAL=True` y `RUN_TEST=True`,
congelando antes variante, política de tokens e hiperparámetros mediante validación.
Debe haber al menos 300 referencias humanas válidas por clase; `unclear` y paquetes
sin gold no entran. No se sustituyen por la pre-etiqueta ni se muestrean 300 a conveniencia.

Se exportan métricas macro/micro, métricas por clase, matrices y predicciones.
Con V0, se desglosa el desempeño según si el **citado** fue visto en train.
Un puntaje cero con un subgrupo vacío no se reporta: se deja sin resultado.
''', r'''
test_summary = []
test_probabilities = {}
if not RUN_TEST:
    print("Evaluación final pendiente de gold T_B consolidado. El entrenamiento puede terminar aquí.")
else:
    train_cited = {r["cited_paper_id"] for r in train_rows}
    for config in CONFIGS:
        clf = load_export(config)
        probs = predict_encoded(clf, encoded[config]["test"])
        test_probabilities[config] = probs
        test_summary.append(report_predictions(config, "test", test_rows, probs))
        subgroup_metrics = {}
        for seen in (True, False):
            idx = [i for i, r in enumerate(test_rows) if (r["cited_paper_id"] in train_cited) == seen]
            if not idx:
                subgroup_metrics[str(seen)] = {"n": 0, "f1_macro": None}
                continue
            y = np.array([LABEL2ID[test_rows[i]["label"]] for i in idx])
            pred = probs[idx].argmax(-1)
            subgroup_metrics[str(seen)] = {"n": len(idx), "f1_macro": f1_score(
                y, pred, labels=list(ID2LABEL), average="macro", zero_division=0)}
        save_json(OUTPUT_ROOT / config / "test_cited_seen_unseen.json", subgroup_metrics)
        del clf
        gc.collect()
        torch.cuda.empty_cache()
    display(pd.DataFrame(test_summary))
    pd.DataFrame(test_summary).to_csv(OUTPUT_ROOT / "test_comparison.csv", index=False)
''')

step(r'''
## 14. Comparar el aporte de Top-3 y empaquetar los artefactos

El resultado principal será `F1_macro(fragmentos) - F1_macro(base)` en el mismo T_B.
Se calcula un intervalo bootstrap pareado por **artículo citante**, manteniendo juntas
sus instancias. Es un análisis exploratorio de esta semilla: para sostener una mejora
consistente conviene repetir ambas configuraciones con varias semillas, con split fijo
y sin seleccionar por test. Esta celda no modifica modelos después de ver el test.

Los ZIP contienen pesos, tokenizador, política y módulo de inferencia; no el corpus.
Para integrar: extraer, importar `CitationClassifier` de `inference.py` y llamar
`predict(example)` con el contrato de entrada. Hay nueve puntajes softmax sin calibrar.
Los CSV con claves/etiquetas y el manifiesto quedan fuera de los ZIP de modelos.

Referencias técnicas:
[SciBERT](https://aclanthology.org/D19-1371/),
[modelo publicado](https://huggingface.co/allenai/scibert_scivocab_uncased),
[Trainer 4.57.1](https://huggingface.co/docs/transformers/v4.57.1/en/main_classes/trainer),
[MultiCite](https://aclanthology.org/2022.naacl-main.137/).
''', r'''
if RUN_TEST and {"base", "fragmentos"} <= test_probabilities.keys():
    y = np.asarray([LABEL2ID[r["label"]] for r in test_rows])
    p0 = test_probabilities["base"].argmax(-1)
    p1 = test_probabilities["fragmentos"].argmax(-1)
    by_citing = collections.defaultdict(list)
    for i, row in enumerate(test_rows):
        by_citing[row["citing_paper_id"]].append(i)
    groups = list(by_citing.values())
    rng = np.random.default_rng(SEED)
    score = lambda truth, pred: f1_score(truth, pred, labels=list(ID2LABEL), average="macro", zero_division=0)
    deltas = []
    for _ in range(1000):
        sampled = rng.integers(0, len(groups), len(groups))
        idx = np.concatenate([groups[i] for i in sampled])
        deltas.append(score(y[idx], p1[idx]) - score(y[idx], p0[idx]))
    comparison = {"delta_macro_f1": score(y, p1) - score(y, p0),
                  "cluster_bootstrap_95_ci": np.quantile(deltas, [0.025, 0.975]).tolist(),
                  "cluster_unit": "citing_paper_id", "replicates": 1000, "seed": SEED}
    save_json(OUTPUT_ROOT / "paired_test_comparison.json", comparison)
    print(comparison)
for config in CONFIGS:
    model_dir = OUTPUT_ROOT / config / "model"
    archive = shutil.make_archive(str(OUTPUT_ROOT / f"scibert_g15_{config}"), "zip", model_dir)
    print("Modelo:", archive)
print("Artefactos privados:", OUTPUT_ROOT)
for config in CONFIGS:
    tracking.reports(config)
    tracking.client.set_tag(tracking.parent(config), "model_zip_drive", str(OUTPUT_ROOT / f"scibert_g15_{config}.zip"))
tracking.backup(force=True)
print("A4 entrenado; la evaluación final solo está completa si RUN_TEST=True y el gold pasó los controles.")
''')


def main():
    notebook = {"cells": CELLS, "metadata": {
        "kernelspec": {"display_name": "Python 3", "language": "python", "name": "python3"},
        "language_info": {"name": "python", "version": "3.12"},
        "colab": {"name": "A4_SciBERT_G15_Colab_A100.ipynb", "provenance": [], "gpuType": "A100"},
        "accelerator": "GPU",
    }, "nbformat": 4, "nbformat_minor": 5}
    for i, cell in enumerate(CELLS):
        cell["id"] = f"a4-{i:03d}"
    path = Path(__file__).with_name("A4_SciBERT_G15_Colab_A100.ipynb")
    path.write_text(json.dumps(notebook, indent=1, ensure_ascii=False) + "\n", encoding="utf-8")
    print(path)


if __name__ == "__main__":
    main()
