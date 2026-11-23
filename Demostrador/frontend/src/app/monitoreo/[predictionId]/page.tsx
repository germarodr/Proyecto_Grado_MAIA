"use client";
import { use, useEffect, useState } from "react";
import Link from "next/link";
import { ArrowLeft, Gauge } from "lucide-react";
import { ProbabilityBars } from "@/components/probability-bars";
import { MatchBadge, Panel, StatusBadge } from "@/components/ui";
import { listPredictions } from "@/lib/api-client";
import { functionName, modelTypeName, percentage, predictionDetail } from "@/lib/prediction-data";

export default function PredictionDetailPage({params}:{params:Promise<{predictionId:string}>}) {
  const {predictionId} = use(params);
  const [item, setItem] = useState<ReturnType<typeof predictionDetail> | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [attempt, setAttempt] = useState(0);
  useEffect(() => {
    const controller = new AbortController();
    listPredictions(controller.signal).then(items => {
      const found = items.find(item => item.prediction_id === predictionId);
      setItem(found ? predictionDetail(found) : null);
    }).catch(error => { if (!controller.signal.aborted) setError(error instanceof Error ? error.message : "No se pudo cargar la inferencia."); })
      .finally(() => { if (!controller.signal.aborted) setLoading(false); });
    return () => controller.abort();
  }, [predictionId, attempt]);
  if (loading) return <div className="shell page" role="status">Cargando inferencia...</div>;
  if (error || !item) return <div className="shell page"><Panel className="form-panel"><h1>{error ? "No se pudo cargar la inferencia" : "Inferencia no encontrada"}</h1>{error && <p role="alert">{error}</p>}{error && <button className="btn" onClick={() => { setLoading(true); setError(""); setAttempt(value => value + 1); }}>Reintentar</button>}<Link className="btn" href="/monitoreo">Volver al historial</Link></Panel></div>;
  const audit = item.tokenAudit;
  return <div className="shell page"><div className="breadcrumb">Monitoreo / Detalle de inferencia</div>
    <div className="detail-heading"><div><h1>Inferencia {item.predictionId.slice(0, 8)} · {item.exampleId}</h1><StatusBadge status={item.status}/></div><Link className="btn" href="/monitoreo"><ArrowLeft size={18}/>Volver al historial</Link></div>
    <div className="summary-grid">
      <Panel className="summary-card"><span>Predicción</span><strong>{item.predictedName}</strong><small>{item.predictedLabel ?? "—"}</small></Panel>
      <Panel className="summary-card"><span>{item.modelType === "encoder" ? "Probabilidad" : "Puntaje"}</span><strong>{percentage(item.confidence)}</strong></Panel>
      <Panel className="summary-card"><span>Latencia</span><strong>{item.latencyMs} ms</strong></Panel>
      <Panel className="summary-card"><span>Modelo</span><strong>{modelTypeName(item.modelType)}</strong><small>{item.modelName}</small></Panel>
    </div>
    {item.errorDetail && <div className="notice" role="alert">{item.errorDetail}</div>}
    <div className="detail-grid">
      <Panel><h2>Puntajes por función</h2>{item.probabilities.length ? <ProbabilityBars items={item.probabilities}/> : <p>No hay puntajes para esta inferencia.</p>}</Panel>
      <Panel><h2>Comparación con la etiqueta humana</h2><div className="meta-list">
        <div className="meta-item"><span>Etiqueta humana</span><strong>{functionName(item.humanLabel)}</strong></div>
        <div className="meta-item"><span>Acierto</span><MatchBadge ok={item.isCorrect}/></div>
        {audit && <>
          <div className="meta-item"><span>Tokens de contexto conservados</span><strong>{audit.context_kept} de {audit.context_original}</strong></div>
          <div className="meta-item"><span>Tokens {item.modelType === "encoder" ? "de fragmentos" : "de título y resumen"} conservados</span><strong>{audit.evidence_kept} de {audit.evidence_original}</strong></div>
          <div className="meta-item"><span>Total de la secuencia</span><strong>{audit.total_tokens} / 512</strong></div>
        </>}
        <div className="meta-item"><span>Fecha y hora</span><strong>{new Date(item.timestamp).toLocaleString("es-CO")}</strong></div>
      </div></Panel>
    </div>
    {item.llmInput && <Panel className="table-panel"><h2>Prompt enviado al LLM</h2><pre className="raw-box">{item.llmInput}</pre></Panel>}
    {item.rawResponse && <Panel className="table-panel"><h2>Respuesta cruda del LLM</h2><pre className="raw-box">{item.rawResponse}</pre></Panel>}
    <div className="notice"><Gauge size={20}/>La probabilidad del encoder es softmax sin calibrar y el puntaje del LLM es el valor que el modelo asignó; ninguno equivale a exactitud validada.</div>
  </div>;
}
