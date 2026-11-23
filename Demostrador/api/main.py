import importlib.util
import json
import os
import re
import time
import urllib.request
from concurrent.futures import ThreadPoolExecutor
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import BackgroundTasks, Depends, FastAPI, HTTPException, Response
from sqlalchemy import text
from sqlalchemy.orm import Session

import a5_alignment
import a5_drive
import a5_providers
import a5_runtime
from database import Base, InferenceLog, SessionLocal, engine, get_db
from schemas import CitationFunction, Example, HealthResponse, ModelInfo, ModelType, PredictionRequest, PredictionResponse, Status

APP_DIR = Path(__file__).parent
ENCODER_DIR = Path(os.getenv("ENCODER_DIR", "/app/models/top3"))
ENCODER_NAME = os.getenv("ENCODER_NAME", "SciBERT Top-3 (grid_fragmentos_contexto_192_lr3em05_wd0p1_s42)")
EXAMPLES_FILE = APP_DIR / "examples_TB_con_resumen.jsonl"
SNAPSHOT_FILE = APP_DIR / "prompt_v11_1_snapshot.json"
OLLAMA_URL = os.getenv("OLLAMA_URL", "http://ollama:11434")

CONDITION = {"id": "base-specific-zero", "representation": "base", "style": "specific", "shot": "zero"}
A5_PARAMS = {"temperature": None, "max_output_tokens": 2048, "response_format": "json_schema", "extra_body": {}}
GEMINI = a5_providers.profile("gemini", "gemini-3.5-flash-lite")
LLMS = {
    ModelType.COMMERCIAL: {
        "key": os.getenv(GEMINI["api_key_env"], ""), "key_name": GEMINI["api_key_env"],
        "cfg": {**A5_PARAMS, "provider": "gemini", "endpoint": GEMINI["endpoint"], "model": GEMINI["model"],
                "output_token_parameter": GEMINI["output_token_parameter"], "timeout_seconds": 90,
                "input_usd_per_million": 0.30, "output_usd_per_million": 2.50},
    },
    ModelType.OPEN_WEIGHT: {
        "key": "ollama", "key_name": None,
        "cfg": {**A5_PARAMS, "endpoint": f"{OLLAMA_URL}/v1/chat/completions",
                "model": os.getenv("OPEN_WEIGHT_MODEL", "hf.co/bartowski/Meta-Llama-3.1-8B-Instruct-GGUF:Q4_K_M"),
                "output_token_parameter": "max_tokens", "timeout_seconds": int(os.getenv("OPEN_WEIGHT_TIMEOUT", "600")),
                "input_usd_per_million": 0.0, "output_usd_per_million": 0.0},
    },
}
RAW_MARKER = re.compile(r"\{\{(cite|formula|table|figure):[^}]*\}\}")

examples = {}
raw_rows = {}
encoder = {}
snapshot = {}
probe_pool = ThreadPoolExecutor(max_workers=4)


def render_markers(text):
    return RAW_MARKER.sub(lambda m: f"[{m.group(1).upper()}]", text)


def load_examples():
    for line in EXAMPLES_FILE.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        row = json.loads(line)
        raw_rows[row["example_id"]] = row
        top3 = sorted(row["top3"], key=lambda c: c["rank"])
        examples[row["example_id"]] = Example(
            example_id=row["example_id"], citing_title=row["citing_title"], cited_title=row["cited_title"],
            citing_url=row["citing_url"], cited_url=row["cited_url"], citing_license=row["citing_license"],
            cited_license=row["cited_license"], context=row["context"],
            cited_abstract=" ".join(row["cited_abstract"].split()), label=row["label"],
            top3=[{"rank": c["rank"], "section": c["section"], "text": render_markers(c["text"])} for c in top3],
        )


def load_encoder():
    spec = importlib.util.spec_from_file_location("inference_top3", ENCODER_DIR / "inference.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    clf = module.CitationClassifier(ENCODER_DIR, device="cpu")
    clf.model.float()
    if clf.policy["config"] != "fragmentos":
        raise RuntimeError(f"Se esperaba el modelo Top-3 ('fragmentos') y se encontró '{clf.policy['config']}'.")
    encoder["clf"] = clf


@asynccontextmanager
async def lifespan(app: FastAPI):
    Base.metadata.create_all(bind=engine)
    with engine.begin() as conn:
        conn.execute(text("ALTER TYPE status_enum ADD VALUE IF NOT EXISTS 'pending'"))
    with SessionLocal() as db:
        db.query(InferenceLog).filter(InferenceLog.status == Status.PENDING).update(
            {"status": Status.ERROR, "error_detail": "Inferencia interrumpida por un reinicio de la API."})
        db.commit()
    load_examples()
    load_encoder()
    snapshot.update(json.loads(SNAPSHOT_FILE.read_text(encoding="utf-8")))
    yield


app = FastAPI(title="CiteScope API", lifespan=lifespan)


def encoder_input(ex):
    return {"context": ex.context, "chunks": [{"text": c.text, "section": c.section} for c in ex.top3]}


def a5_messages(ex):
    row = raw_rows[ex.example_id]
    case = {"inst_key": row["inst_key"], "citing_id": row["citing_paper_id"], "cited_id": row["cited_paper_id"],
            "context": row["context"].strip(), "target_sentence": a5_drive.target_sentence(row["context"].strip()),
            "split": "test", "cited_title": row["cited_title"].strip(), "cited_abstract": row["cited_abstract"].strip()}
    case = a5_runtime.normalize_cases([case], "test")[0]
    aligned, audits = a5_alignment.align_case(case, encoder["clf"].tokenizer)
    a5_runtime.normalize_cases([aligned], "test")
    return a5_runtime.build_messages(aligned, CONDITION, snapshot, [], {}, aligned=True), audits[0]


def classify_llm(ex, llm, log):
    if not llm["key"]:
        raise ValueError(f"Configura {llm['key_name']} en .env.")
    messages, audit = a5_messages(ex)
    log.token_audit = {k: v for k, v in audit.items() if isinstance(v, int)}
    log.llm_input = "\n\n".join(f"[{m['role'].upper()}]\n{m['content']}" for m in messages)
    cfg = llm["cfg"]
    result = a5_runtime.http_call(a5_runtime.payload_for({"messages": messages}, cfg), cfg, llm["key"])
    parsed = a5_runtime.unpack_response(result, cfg)
    log.raw_response = parsed["response_text"] or result.get("raw_body")
    if not result["ok"]:
        raise ConnectionError(f"HTTP {result['status_code']} ({result.get('error_type')}) de {cfg['model']}")
    if not parsed["valid"]:
        raise ValueError(f"Respuesta inválida según A5: {parsed['error']}")
    return parsed["scores"], parsed["predicted_label"]


def classify(ex, model_type, log):
    if model_type != ModelType.ENCODER:
        return classify_llm(ex, LLMS[model_type], log)
    result = encoder["clf"].predict(encoder_input(ex))
    log.token_audit = result["token_audit"]
    return result["scores"], result["label"]


def fetch_ollama_models():
    with urllib.request.urlopen(f"{OLLAMA_URL}/v1/models", timeout=3) as resp:
        return [m["id"] for m in json.load(resp)["data"]]


def open_weight_info():
    name = LLMS[ModelType.OPEN_WEIGHT]["cfg"]["model"]
    try:
        ids = probe_pool.submit(fetch_ollama_models).result(timeout=3)
    except Exception:
        return ModelInfo(name=name, available=False, detail="Servidor Ollama no disponible")
    ok = name in ids
    return ModelInfo(name=name, available=ok, detail=f"Listo · A5 {CONDITION['id']}" if ok else "Modelo aún no descargado en Ollama")


@app.get("/health", response_model=HealthResponse)
def health():
    commercial = LLMS[ModelType.COMMERCIAL]
    return HealthResponse(status="ok" if encoder else "sin_modelo", models={
        ModelType.ENCODER: ModelInfo(name=ENCODER_NAME, available=bool(encoder), detail="Listo" if encoder else "No cargado"),
        ModelType.OPEN_WEIGHT: open_weight_info(),
        ModelType.COMMERCIAL: ModelInfo(name=commercial["cfg"]["model"], available=bool(commercial["key"]),
                                        detail=f"Listo · A5 {CONDITION['id']}" if commercial["key"] else f"Falta {commercial['key_name']}"),
    })


@app.get("/examples", response_model=list[Example])
def list_examples():
    return list(examples.values())


def run_inference(ex, model_type, log):
    start = time.perf_counter()
    error_code = None
    try:
        scores, best = classify(ex, model_type, log)
        log.predicted_label, log.confidence, log.class_scores = CitationFunction(best), scores[best], scores
        log.is_correct, log.status = log.predicted_label == ex.label, Status.SUCCESS
    except ValueError as exc:
        log.status, log.error_detail, error_code = Status.ERROR, str(exc), 422
    except Exception as exc:
        log.status, log.error_detail, error_code = Status.ERROR, f"Error al consultar el modelo: {exc!r}", 502
    log.latency_ms = (time.perf_counter() - start) * 1000
    return error_code


def run_in_background(prediction_id, model_type):
    with SessionLocal() as db:
        log = db.get(InferenceLog, prediction_id)
        run_inference(examples[log.example_id], model_type, log)
        db.commit()


@app.post("/predictions", response_model=PredictionResponse, status_code=201)
def create_prediction(payload: PredictionRequest, background: BackgroundTasks, response: Response, db: Session = Depends(get_db)):
    ex = examples.get(payload.example_id)
    if ex is None:
        raise HTTPException(status_code=404, detail=f"No existe el ejemplo '{payload.example_id}'.")
    name = ENCODER_NAME if payload.model_type == ModelType.ENCODER else f"{LLMS[payload.model_type]['cfg']['model']} (A5 {CONDITION['id']})"
    log = InferenceLog(example_id=ex.example_id, model_type=payload.model_type, model_name=name, human_label=ex.label,
                       status=Status.PENDING, latency_ms=0)

    error_code = run_inference(ex, payload.model_type, log) if payload.model_type == ModelType.ENCODER else None
    db.add(log)
    db.commit()
    db.refresh(log)

    if error_code:
        raise HTTPException(status_code=error_code, detail=log.error_detail)
    if log.status == Status.PENDING:
        background.add_task(run_in_background, log.prediction_id, payload.model_type)
        response.status_code = 202
    return log


@app.get("/predictions", response_model=list[PredictionResponse])
def list_predictions(db: Session = Depends(get_db)):
    return db.query(InferenceLog).order_by(InferenceLog.timestamp.desc()).all()
