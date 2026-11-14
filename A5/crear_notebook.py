"""Regenera únicamente el notebook A5, sin ejecutar celdas ni usar la API."""
from pathlib import Path
import json
import textwrap

CELLS = []


def block(title, description, code):
    CELLS.append({"cell_type": "markdown", "metadata": {}, "source": f"## {title}\n\n{description}\n"})
    CELLS.append({"cell_type": "code", "metadata": {}, "execution_count": None, "outputs": [],
                  "source": textwrap.dedent(code).strip() + "\n"})


CELLS.append({"cell_type": "markdown", "metadata": {}, "source": """# A5 · Modelo comercial — Grupo 15

Este notebook usa únicamente **contexto de cita + título + resumen del artículo citado**. Compara instrucciones genéricas/específicas y zero-shot/few-shot: cuatro condiciones por modelo comercial. Se basa en el prompt v11.1 del equipo y lo adapta a nueve puntuaciones. No utiliza chunks ni Top-3.

**Primera ejecución:** mantén `DEMO=True` y `ENABLE_API=False`. Se usarán textos inventados y respuestas simuladas para comprobar el flujo. Sus métricas no son resultados científicos ni provienen de un modelo.

En Colab se monta Drive, el bloque 3.1 reconstruye T_B y el bloque 3.2 prepara el recorte equivalente a **SciBERT base** y candidatos humanos para desarrollo/few-shot. Guarda archivos privados en `MAIA_TESIS/A5/prepared`, sin inferir. Estos pasos son independientes de DEMO: la inferencia posterior sigue siendo sintética hasta configurarla explícitamente.

Necesitas Python 3.10+ y, junto al notebook, `a5_runtime.py`, `a5_drive.py`, `a5_alignment.py` y `prompt_v11_1_snapshot.json`. La demostración usa solo la biblioteca estándar; para el recorte real el bloque 3.2 instala Transformers 4.57.1 si hace falta y descarga únicamente el tokenizador SciBERT fijado. No necesita GPU. Lee [Notebook_Explain.md](Notebook_Explain.md).

Los parámetros editables tienen comentarios **AQUÍ**. No escribas la clave API en una celda ni en un archivo del proyecto. Ninguna celda enviará solicitudes mientras `ENABLE_API=False`.
"""})

block("1. Preparar Python y montar Drive en Colab", "Detecta Colab y monta tu Drive con tu autorización. En una sesión local no intenta conectarse a Google. El acceso directo debe llamarse MAIA_PROYECTO y tu carpeta propia MAIA_TESIS.", r'''
from pathlib import Path
import getpass
import importlib.util
import json
import os
import sys

try:
    from google.colab import drive
except ImportError:
    drive = None
USE_DRIVE = drive is not None  # AQUÍ: False si prefieres una demostración sin montar Drive.
if USE_DRIVE:
    drive.mount("/content/drive")
assert sys.version_info >= (3, 10), "Se requiere Python 3.10 o superior"
print("Python listo. Todavía no se ha solicitado ninguna credencial.")
''')

block("2. Indicar dónde está la carpeta A5", "Localiza el módulo y la copia del prompt. En Colab copia estos archivos a Drive o súbelos a la sesión; abrir solo el notebook no descarga sus archivos auxiliares.", r'''
# AQUÍ: cambia esta ruta si A5 está en otra carpeta.
# Windows: Path(r"D:\...\Proyecto_Grado\A5")
# Colab con Drive: Path("/content/drive/MyDrive/MAIA_TESIS/A5")
A5_DIR = Path.cwd()
if not (A5_DIR / "a5_runtime.py").is_file() and (A5_DIR / "A5/a5_runtime.py").is_file():
    A5_DIR = A5_DIR / "A5"
if not (A5_DIR / "a5_runtime.py").is_file() and USE_DRIVE:
    A5_DIR = Path("/content/drive/MyDrive/MAIA_TESIS/A5")
for name in ("a5_runtime.py", "a5_drive.py", "a5_alignment.py", "prompt_v11_1_snapshot.json"):
    assert (A5_DIR / name).is_file(), f"Falta {name}. Configura A5_DIR o copia los archivos auxiliares."
if str(A5_DIR) not in sys.path:
    sys.path.insert(0, str(A5_DIR))
spec = importlib.util.spec_from_file_location("a5_runtime", A5_DIR / "a5_runtime.py")
a5 = importlib.util.module_from_spec(spec)
spec.loader.exec_module(a5)
drive_spec = importlib.util.spec_from_file_location("a5_drive", A5_DIR / "a5_drive.py")
a5_drive = importlib.util.module_from_spec(drive_spec)
drive_spec.loader.exec_module(a5_drive)
alignment_spec = importlib.util.spec_from_file_location("a5_alignment", A5_DIR / "a5_alignment.py")
a5_alignment = importlib.util.module_from_spec(alignment_spec)
alignment_spec.loader.exec_module(a5_alignment)
snapshot = json.loads((A5_DIR / "prompt_v11_1_snapshot.json").read_text(encoding="utf-8"))
print("Módulo:", a5.VERSION, "| prompt:", snapshot["version"])
''')

block("3. Señalar los archivos de datos", "Configura origen compartido y destino privado. El gold A3 ya está adjudicado; el bloque 3.1 lo verifica por manifiesto. Las rutas de desarrollo y few-shot siguen siendo independientes del test.", r'''
DEMO = True  # AQUÍ: False cuando tengas los JSONL reales. Demo nunca consume API.
SPLIT = "dev"  # AQUÍ: "dev" para piloto; "test" únicamente para evaluación final.
# AQUÍ: el enlace identifica el origen; se accede mediante Drive montado, no como descarga pública.
SHARED_FOLDER_URL = "https://drive.google.com/drive/u/0/folders/11RYKPpKDissDfgVTvdXWLJekbZabRK1U"
SHARED_DATA_ROOT = Path("/content/drive/MyDrive/MAIA_PROYECTO")  # AQUÍ: acceso directo compartido, SOLO LECTURA.
RESULTS_ROOT = Path("/content/drive/MyDrive/MAIA_TESIS")  # AQUÍ: tu carpeta propia.
A5_PRIVATE_DIR = RESULTS_ROOT / "A5" if USE_DRIVE else A5_DIR
DATA_DIR = A5_PRIVATE_DIR / "data"  # AQUÍ: desarrollo/few-shot o exportaciones A4 que recibas.
OUTPUT_DIR = A5_PRIVATE_DIR / "outputs"
RUN_ID = "a5_base_only_demo_01"  # AQUÍ: nombre NUEVO; no reutilizar runs de la variante anterior.
PREPARE_DRIVE_DATA = USE_DRIVE  # AQUÍ: en Colab True; localmente False salvo que tengas el Drive montado.
EXPECTED_A3_MANIFEST_SHA256 = a5_drive.EXPECTED_METRICS_SHA256  # Huella usada por Sebastián; revisar si cambia la entrega.
PREPARE_ALIGNED_DATA = PREPARE_DRIVE_DATA  # AQUÍ: True para ejecutar el bloque 3.2 después del 3.1.
PILOT_PER_CLASS = 5  # AQUÍ: 5 por función = 45 casos T_A, separados del banco few-shot y T_B.
DEVELOPMENT_SELECTION_SEED = "G15-A5-fewshot-v1"  # AQUÍ: fijar antes de consultar resultados.
FEWSHOT_REVIEWED = False  # AQUÍ: True SOLO tras revisar los nueve candidatos; bloquea API few-shot si False.
DEVELOPMENT_EXCLUDED_KEYS = [
    "2211.09791|48|203-252|1809.04427",  # MOT17: el recurso mencionado no coincide con título/resumen citados.
]  # Exclusión del banco y piloto; no cambia el gold ni elimina casos de T_B.
TOKENIZER_LOCAL_PATH = None  # AQUÍ: carpeta de vocabulario/tokenizador SciBERT si ya lo tienes; None descarga la revisión fijada.

PATHS = {
    "cases": str(DATA_DIR / "dev_cases.jsonl"),  # AQUÍ: test_cases.jsonl al usar SPLIT="test".
    "gold": str(DATA_DIR / "dev_gold.jsonl"),  # AQUÍ: gold adjudicado. Se lee para evaluar, no se envía.
    "heldout": str(DATA_DIR / "tb_reserved_ids.jsonl"),  # AQUÍ: TODOS los IDs reservados de T_B.
    "exclusions": str(DATA_DIR / "exclusion_list.jsonl"),  # AQUÍ: exclusiones por ID/citante.
    "examples": str(DATA_DIR / "fewshot_cases.jsonl"),  # AQUÍ: nueve casos dev, uno por categoría.
    "example_gold": str(DATA_DIR / "fewshot_gold.jsonl"),  # AQUÍ: sus nueve soluciones humanas.
}
DATASET_VERSION = "training_v2+A3_gold_2026-11-09"  # AQUÍ: verificar con el manifiesto de la entrega final.
GUIDE_VERSION = "rev3.1"
VARIANT = "V2"  # AQUÍ: la entrega final recibida de Sebastián usa aislamiento V2.
GOLD_FINAL = False  # AQUÍ: True solo tras cerrar adjudicación, reservas y exclusiones.
PROTOCOL_FROZEN = False  # AQUÍ: True tras elegir prompts/ejemplos/modelo usando desarrollo.
MIN_GOLD_PER_CLASS = 300
QUOTA_DEVIATION_REASON = "Cierre A3 sin ola 4 acordado por G14/G15: T_B conserva 268 Improvement/Modification."
''')

block("3.1. Verificar Drive y reconstruir T_B en la carpeta propia", "Lee el manifiesto y el gold de a3, comprueba sus hashes y selecciona set B con in_eval=true. De los lotes A2 toma solo contexto, título y resumen; descarta otros campos. No usa API, no puntúa el test y no escribe en MAIA_PROYECTO. Los textos exportados aún no están recortados como SciBERT base.", r'''
drive_preparation = None
if PREPARE_DRIVE_DATA:
    drive_preparation = a5_drive.prepare_tb(SHARED_DATA_ROOT, RESULTS_ROOT, EXPECTED_A3_MANIFEST_SHA256)
    audit = drive_preparation["audit"]
    print("T_B humano evaluable:", audit["evaluable_tb"], "| unclear excluidos:", audit["excluded_unclear_tb"])
    print("Textos reconstruidos:", audit["reconstructed_tb"], "| lotes leídos:", len(audit["batch_hashes"]))
    print("Preparación privada:", drive_preparation["prepared_dir"])
    print("Estado de entradas:", audit["input_state"], "| API:", audit["api_called"])
    PATHS["heldout"] = drive_preparation["heldout"]  # También protege el piloto contra fuga hacia T_B.
    if SPLIT == "test":
        # AQUÍ se conectan las exportaciones del origen real; nunca se usa T_B como desarrollo.
        PATHS.update({key: drive_preparation[key] for key in ("cases", "gold", "heldout")})
    print("Falta alinear el recorte A4 y preparar desarrollo/few-shot antes de la evaluación final.")
else:
    print("Preparación de Drive desactivada. En Colab se activa tras montar Drive; localmente se mantiene la demo.")
''')

block("3.2. Preparar contexto, título y resumen y seleccionar desarrollo/few-shot", "Reproduce únicamente la política SciBERT base: 512 tokens totales, hasta 192 de contexto, título y resumen. Conserva IDs de tokens como auditoría. Selecciona nueve candidatos humanos de T_A y un piloto separado de 45 casos, aplicando V2 frente a T_B y entre banco y piloto. No consulta predicciones ni puntúa el test. Este bloque puede instalar/descargar el tokenizador, sin clave comercial ni GPU.", r'''
aligned_preparation = None
if PREPARE_ALIGNED_DATA:
    if drive_preparation is None:
        raise ValueError("Primero ejecuta 3.1 correctamente.")
    import importlib.metadata
    import subprocess
    try:
        version = importlib.metadata.version("transformers")
    except importlib.metadata.PackageNotFoundError:
        version = None
    if version != "4.57.1":
        if "transformers" in sys.modules:
            raise RuntimeError("Reinicia el entorno antes de instalar Transformers 4.57.1.")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-q", "transformers==4.57.1"])
    tokenizer = a5_alignment.load_tokenizer(TOKENIZER_LOCAL_PATH)
    aligned_preparation = a5_alignment.prepare_aligned(
        SHARED_DATA_ROOT, RESULTS_ROOT, drive_preparation, tokenizer,
        per_class=PILOT_PER_CLASS, seed=DEVELOPMENT_SELECTION_SEED,
        expected_manifest_sha256=EXPECTED_A3_MANIFEST_SHA256,
        excluded_keys=DEVELOPMENT_EXCLUDED_KEYS)
    PATHS.update(aligned_preparation["paths"])
    if SPLIT == "test":
        PATHS.update(aligned_preparation["test_paths"])
    selection = aligned_preparation["manifest"]
    print("T_B alineado:", selection["test_cases"], "| entrada: contexto + título + resumen")
    print("Candidatos few-shot:", selection["fewshot_n"], "| piloto T_A:", selection["pilot_n"])
    print("Aislamiento:", selection["isolated_from_tb"], "| banco/piloto:", selection["bank_pilot_isolation"])
    print("Carpeta privada:", aligned_preparation["prepared_dir"])
    print("Revisa fewshot_cases.jsonl junto a fewshot_gold.jsonl antes de activar FEWSHOT_REVIEWED.")
    print("API:", selection["api_called"], "| test evaluado:", selection["test_scored"])
else:
    print("Alineación real desactivada; la demo puede continuar sin Transformers.")
''')

block("4. Configurar URL, modelo y costo de API", "El adaptador envía JSON no streaming a una URL compatible con Chat Completions y lee choices/message/content y usage. Otras APIs nativas requieren otro adaptador. El límite local usa una reserva por intento; no reemplaza el límite de gasto del proveedor.", r'''
ENABLE_API = False  # AQUÍ: activar solo para una ejecución pagada ya preparada.
# AQUÍ VA LA URL COMPLETA del endpoint de inferencia; no es la página web del modelo.
API_ENDPOINT = "https://REEMPLAZAR_PROVEEDOR/v1/chat/completions"
MODEL_ID = "REEMPLAZAR_MODELO_O_SNAPSHOT"  # AQUÍ: identificador exacto del catálogo de tu proveedor.
API_KEY_ENV = "A5_API_KEY"  # Nombre de variable de entorno; NO pegar aquí el token.
TEMPERATURE = None  # AQUÍ: None omite el parámetro; 0 solo si tu modelo lo admite.
MAX_OUTPUT_TOKENS = 2048  # AQUÍ: medir en piloto; un límite insuficiente genera respuestas inválidas.
OUTPUT_TOKEN_PARAMETER = "max_completion_tokens"  # AQUÍ: algunos proveedores usan "max_tokens".
RESPONSE_FORMAT = "json_object"  # AQUÍ: "none", "json_object" o "json_schema", según soporte.
EXTRA_BODY = {}  # AQUÍ: parámetros públicos adicionales admitidos por el modelo. Nunca credenciales.

BUDGET_USD = 0.0  # AQUÍ: presupuesto máximo reservado para esta ejecución, incluidos reintentos.
RESERVE_PER_ATTEMPT_USD = 0.0  # AQUÍ: reserva conservadora por intento, estimada con el piloto.
INPUT_USD_PER_MILLION = 0.0  # AQUÍ: tarifa vigente de entrada por millón de tokens, sin descuento.
OUTPUT_USD_PER_MILLION = 0.0  # AQUÍ: tarifa vigente de salida por millón de tokens.
PRICING_VERIFIED = False  # AQUÍ: True tras verificar tarifas oficiales del modelo elegido.
PRICING_SOURCE = ""  # AQUÍ: enlace oficial de precios.
PRICING_DATE = ""  # AQUÍ: fecha de consulta, YYYY-MM-DD.
TIMEOUT_SECONDS = 90
MAX_RETRIES = 2  # Solo fallos transitorios; las respuestas JSON inválidas no se repiten para corregirlas.
REQUEST_INTERVAL_SECONDS = 0.5  # Concurrencia secuencial y pausa entre casos.
''')

block("5. Definir las cuatro comparaciones", "Usa una sola entrada: contexto, título y resumen. Cruza instrucciones genéricas/específicas con zero-shot/few-shot. El piloto puede limitar casos; el test completo no permite ese límite. No se admite una variante con fragmentos.", r'''
REPRESENTATIONS = ["base"]  # FIJO: contexto + título + resumen. No añadir otras variantes.
STYLES = ["generic", "specific"]
SHOTS = ["zero", "few"]
ALIGNED_INPUTS = aligned_preparation is not None and not DEMO  # La demo no contiene entradas SciBERT reales.
INPUT_POLICY_VERSION = aligned_preparation["policy_version"] if ALIGNED_INPUTS else "demo-full-text"
SEED = 42  # Controla orden de casos/condiciones; no hace determinista al modelo comercial.
LIMIT_CASES = None  # AQUÍ: 30–50 para piloto real. None para todos; siempre None en test.
STABILITY_CASES = 0  # AQUÍ: tamaño de submuestra predefinida; 3 solicitudes por caso/condición.
BOOTSTRAP_REPETITIONS = 0 if DEMO else 1000  # Intervalos agrupados por artículo citante.

CFG = {
    "demo": DEMO, "split": SPLIT, "paths": PATHS, "output_dir": str(OUTPUT_DIR), "run_id": RUN_ID,
    "dataset_version": DATASET_VERSION, "guide_version": GUIDE_VERSION, "variant": VARIANT,
    "gold_final": GOLD_FINAL, "protocol_frozen": PROTOCOL_FROZEN,
    "min_gold_per_class": MIN_GOLD_PER_CLASS, "quota_deviation_reason": QUOTA_DEVIATION_REASON,
    "enable_api": ENABLE_API, "endpoint": API_ENDPOINT, "model": MODEL_ID,
    "temperature": TEMPERATURE, "max_output_tokens": MAX_OUTPUT_TOKENS,
    "output_token_parameter": OUTPUT_TOKEN_PARAMETER, "response_format": RESPONSE_FORMAT,
    "extra_body": EXTRA_BODY, "budget_usd": BUDGET_USD,
    "reserve_per_attempt_usd": RESERVE_PER_ATTEMPT_USD,
    "input_usd_per_million": INPUT_USD_PER_MILLION, "output_usd_per_million": OUTPUT_USD_PER_MILLION,
    "pricing_verified": PRICING_VERIFIED, "pricing_source": PRICING_SOURCE, "pricing_date": PRICING_DATE,
    "timeout_seconds": TIMEOUT_SECONDS, "max_retries": MAX_RETRIES,
    "request_interval_seconds": REQUEST_INTERVAL_SECONDS,
    "representations": REPRESENTATIONS, "styles": STYLES, "shots": SHOTS,
    "aligned_inputs": ALIGNED_INPUTS, "input_policy_version": INPUT_POLICY_VERSION,
    "seed": SEED, "limit_cases": LIMIT_CASES, "stability_cases": STABILITY_CASES,
    "shared_folder_url": SHARED_FOLDER_URL,
    "drive_preparation_fingerprint": drive_preparation["fingerprint"] if drive_preparation else None,
    "alignment_fingerprint": aligned_preparation["fingerprint"] if aligned_preparation else None,
    "fewshot_reviewed": FEWSHOT_REVIEWED,
}
print("Modo:", "DEMO SINTÉTICA" if DEMO else SPLIT, "| API:", ENABLE_API)
''')

block("6. Cargar y auditar los datos", "Comprueba identificadores, campos, targets y separación entre ejemplos/desarrollo y T_B. Solo proyecta a la inferencia los campos de texto autorizados; no incorpora votos ni gold del caso objetivo.", r'''
bundle = a5.load_bundle(CFG)
plan = a5.make_plan(CFG, bundle, snapshot)
print("Auditoría:", plan["isolation"])
print("Condiciones:", [c["id"] for c in plan["conditions"]])
if DEMO:
    print("ATENCIÓN: casos y soluciones inventados para verificar software; no anotaciones humanas reales.")
''')

block("7. Revisar un prompt y el volumen de ejecución", "Muestra una solicitud sin token y contabiliza las llamadas. La vista puede contener texto científico: evita compartir la salida si la política del dataset lo restringe. El conteo de bytes no es una estimación de tokens facturados.", r'''
print("Solicitudes principales:", plan["primary_calls"])
print("Solicitudes con estabilidad:", plan["total_calls"])
print("Máximo de intentos con reintentos:", plan["max_attempts"])
print("Máximo de bytes UTF-8 de mensajes:", plan["utf8_bytes_max"])
print("Reserva para un intento por tarea: USD", plan["total_calls"] * RESERVE_PER_ATTEMPT_USD)
print("Reserva para todos los reintentos posibles: USD", plan["max_attempts"] * RESERVE_PER_ATTEMPT_USD)
if ENABLE_API:
    a5.check_api_config(CFG, bundle)
    if DATASET_VERSION.startswith("REEMPLAZAR") or INPUT_POLICY_VERSION.startswith("REEMPLAZAR"):
        raise ValueError("Identifica la versión real de datos y política antes de consumir API")
    print("Configuración API validada; no se ha enviado ninguna solicitud.")
preview = plan["tasks"][0]
print("Vista parcial de", preview["condition"], preview["inst_key"])
for message in preview["messages"]:
    print(message["role"].upper(), message["content"][:1400], "\n")
''')

block("8. Ingresar la credencial de forma oculta", "Este es el lugar del token de permiso. Primero intenta leer A5_API_KEY; si no existe, usa un campo oculto. El token queda solo en memoria y nunca se añade a CFG ni se imprime.", r'''
api_token = None
if ENABLE_API:
    a5.check_api_config(CFG, bundle)
    api_token = os.environ.get(API_KEY_ENV) or getpass.getpass("Token API (entrada oculta): ")
    if not api_token.strip():
        raise ValueError("No se ingresó un token")
    print("Credencial cargada en memoria; valor oculto.")
else:
    print("No se necesita token: API desactivada.")
''')

block("9. Preparar o ejecutar y guardar el experimento", "Con datos reales y API desactivada, guarda solo el plan y las solicitudes. En demo simula las respuestas. En modo real activado ejecuta las llamadas, registra intentos y permite reanudar sin repetir resultados terminales.", r'''
run = a5.run_experiment(CFG, bundle, plan, snapshot, token=api_token)
RUN_DIR = Path(run["output_dir"])
predictions = run["predictions"]
print({k: v for k, v in run.items() if k != "predictions"})
if DEMO:
    print("SIMULACIÓN: las respuestas se construyeron desde soluciones inventadas. No interpretar su F1 como desempeño.")
''')

block("10. Leer el gold para evaluar", "Une las predicciones con las etiquetas por inst_key después de inferir. Nunca envía el gold del caso objetivo al modelo. En demo usa únicamente las soluciones inventadas; si falta gold real, la evaluación queda pendiente.", r'''
gold = None
evaluated_cases = [r for r in bundle["cases"] if r["inst_key"] in {t["inst_key"] for t in plan["tasks"]}]
if predictions:
    if DEMO:
        gold = {r["inst_key"]: bundle["demo_gold"][r["inst_key"]] for r in evaluated_cases}
    elif Path(PATHS["gold"]).is_file():
        gold = a5.normalize_gold(a5.read_jsonl(PATHS["gold"]))
        if SPLIT == "dev":
            # Se acepta un gold de desarrollo mayor que el piloto, conservando todos los IDs evaluados.
            gold = {r["inst_key"]: gold[r["inst_key"]] for r in evaluated_cases}
    else:
        print("Gold no disponible: predicciones guardadas; métricas pendientes.")
else:
    print("No hay predicciones: preparación sin API completada.")
''')

block("11. Calcular métricas y matrices", "Calcula macro/micro, métricas por clase y matrices con una columna para respuestas inválidas. No elimina fallos para mejorar el resultado. Los intervalos usan remuestreo por artículo citante.", r'''
metrics = []
if predictions and gold is not None:
    metrics = a5.evaluate(predictions, gold, evaluated_cases, RUN_DIR,
                          bootstrap_repetitions=BOOTSTRAP_REPETITIONS, seed=SEED)
    for row in metrics:
        print(row["condition"], "F1 macro:", round(row["f1_macro"], 4),
              "F1 micro:", round(row["f1_micro"], 4), "cobertura:", row["valid_coverage"])
    print("Resultados en:", RUN_DIR)
    if DEMO:
        print("MÉTRICAS SINTÉTICAS: prueba del flujo, sin valor experimental.")
else:
    print("Evaluación pendiente de predicciones y gold.")
''')

block("12. Revisar estabilidad, tokens y errores", "Resume repeticiones y el diario completo, incluidos reintentos. Los costos de las métricas por caso solo reflejan el último intento; el diario y el resumen de presupuesto incluyen todos los intentos. Contrasta el estimado con la factura del proveedor.", r'''
if predictions:
    stability = a5.stability_report(predictions)
    a5.write_json(RUN_DIR / "stability.json", stability)
    attempts = a5.read_jsonl(RUN_DIR / "attempts.jsonl")
    outcomes = [e for e in attempts if e["event"] == "outcome"]
    print("Intentos:", len(outcomes), "| inválidos principales:", sum(not p["valid"] for p in predictions if p["replicate"] == 0))
    print("Modelos devueltos:", sorted({str(p["returned_model"]) for p in predictions}))
    if not DEMO:
        print("Presupuesto:", a5.ledger_status(attempts, CFG))
    print("Grupos de estabilidad:", len(stability))
else:
    print("Sin ejecución de inferencia todavía.")
''')

block("13. Comparar con SciBERT cuando exista el test final", "Recibe un CSV de SciBERT con inst_key y predicted_label. Exige exactamente los mismos casos de T_B; no compara la validación con preetiquetas de A4 contra el test humano de A5. El contraste de entrada equivalente debe quedar identificado en el reporte.", r'''
SCIBERT_PREDICTIONS = None  # AQUÍ: ruta al CSV de predicciones del test humano final de SciBERT.
SCIBERT_REPRESENTATION = "base"  # FIJO: la referencia comparable es SciBERT base.
SCIBERT_RUN_REFERENCE = ""  # AQUÍ: run_id/hash del artefacto A4 y versión del gold correspondiente.
if SCIBERT_PREDICTIONS and predictions and gold is not None:
    if DEMO or SPLIT != "test":
        raise ValueError("La comparación final se hace con datos reales de T_B")
    if not SCIBERT_RUN_REFERENCE:
        raise ValueError("Identifica el run de SciBERT y su gold")
    matching = [p for p in predictions if p["condition"].startswith(SCIBERT_REPRESENTATION + "-")]
    assert matching, "No hay condiciones con esa entrada"
    comparison = a5.compare_scibert(SCIBERT_PREDICTIONS, matching, gold, SEED, BOOTSTRAP_REPETITIONS)
    a5.write_json(RUN_DIR / f"comparison_scibert_{SCIBERT_REPRESENTATION}.json", {
        "reference": SCIBERT_RUN_REFERENCE, "csv_sha256": a5.file_hash(SCIBERT_PREDICTIONS), "results": comparison})
    for row in comparison:
        print(row)
else:
    print("Comparación pendiente de predicciones finales equivalentes de SciBERT y A5.")
''')

block("14. Cerrar la sesión y dejar evidencia del estado", "Limpia la referencia al token y resume qué se produjo. Las respuestas originales, mensajes y manifiestos quedan en la carpeta del run; evita publicar esos textos si no corresponde. No se guarda el token en ningún artefacto.", r'''
api_token = None  # Borra esta referencia; si existe una variable de entorno, se gestiona fuera del notebook.
print("Estado:", run["status"])
print("Carpeta:", RUN_DIR)
print("Gold final declarado:", GOLD_FINAL, "| test:", SPLIT == "test")
print("Revisa Notebook_Explain.md antes de pasar de demo a piloto o a test.")
''')

if __name__ == "__main__":
    notebook = {"cells": CELLS, "metadata": {"kernelspec": {"display_name": "Python 3", "language": "python", "name": "python3"},
                "language_info": {"name": "python", "version": "3.10"}}, "nbformat": 4, "nbformat_minor": 5}
    # IDs estables para nbformat 4.5; ninguna celda contiene resultados ni secretos.
    for i, cell in enumerate(CELLS):
        cell["id"] = f"a5-cell-{i:02d}"
        if cell["cell_type"] == "code":
            compile(cell["source"], f"cell-{i}", "exec")
    dest = Path(__file__).with_name("A5_Modelo_Comercial_G15.ipynb")
    dest.write_text(json.dumps(notebook, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print("Notebook generado:", dest.name, "| bloques:", sum(c["cell_type"] == "code" for c in CELLS))
