"use client";
import Link from "next/link";
import { useEffect, useMemo, useState } from "react";
import { AlertTriangle, CircleCheck, Clock3, FileStack, Search } from "lucide-react";
import { MonitoringCharts } from "@/components/monitoring-charts";
import { KpiCard, MatchBadge, PageHeading, Panel, StatusBadge } from "@/components/ui";
import functions from "../../../data/functions.json";
import { listPredictions } from "@/lib/api-client";
import type { ApiPrediction } from "@/lib/api-types";
import { functionName, localDate, MODEL_TYPES, modelTypeName, monitoringSummary, percentage } from "@/lib/prediction-data";

const initial = { label: "all", model: "all", status: "all", from: "", to: "" };

export default function MonitoringPage() {
  const [predictions, setPredictions] = useState<ApiPrediction[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [attempt, setAttempt] = useState(0);
  const [draft, setDraft] = useState(initial);
  const [filters, setFilters] = useState(initial);
  useEffect(() => {
    const controller = new AbortController();
    listPredictions(controller.signal).then(setPredictions)
      .catch(error => { if (!controller.signal.aborted) setError(error instanceof Error ? error.message : "No se pudo cargar el historial."); })
      .finally(() => { if (!controller.signal.aborted) setLoading(false); });
    return () => controller.abort();
  }, [attempt]);
  const filtered = useMemo(() => predictions.filter(p => {
    const date = localDate(p.timestamp);
    return (filters.label === "all" || p.predicted_label === filters.label) && (filters.model === "all" || p.model_type === filters.model)
      && (filters.status === "all" || p.status === filters.status) && (!filters.from || date >= filters.from) && (!filters.to || date <= filters.to);
  }), [predictions, filters]);
  const monitoring = useMemo(() => monitoringSummary(filtered), [filtered]);
  const set = (key: keyof typeof initial, value: string) => setDraft(d => ({ ...d, [key]: value }));

  return <div className="shell page"><PageHeading title="Monitoreo" subtitle="Trazabilidad de cada inferencia: modelo, predicción, acierto frente a la etiqueta humana, latencia y errores de formato."/>
    <Panel className="filter-bar wide">
      <div className="filter-field"><label>Desde</label><input type="date" aria-label="Desde" value={draft.from} max={draft.to || undefined} onChange={e => set("from", e.target.value)}/></div>
      <div className="filter-field"><label>Hasta</label><input type="date" aria-label="Hasta" value={draft.to} min={draft.from || undefined} onChange={e => set("to", e.target.value)}/></div>
      <div className="filter-field"><label>Modelo</label><select aria-label="Modelo" value={draft.model} onChange={e => set("model", e.target.value)}><option value="all">Todos</option>{MODEL_TYPES.map(m => <option key={m.id} value={m.id}>{m.name}</option>)}</select></div>
      <div className="filter-field"><label>Función predicha</label><select aria-label="Función" value={draft.label} onChange={e => set("label", e.target.value)}><option value="all">Todas</option>{functions.map(f => <option key={f.code} value={f.code}>{f.nameEs}</option>)}</select></div>
      <div className="filter-field"><label>Estado</label><select aria-label="Estado" value={draft.status} onChange={e => set("status", e.target.value)}><option value="all">Todos</option><option value="success">Éxito</option><option value="error">Error</option><option value="pending">En curso</option></select></div>
      <button className="btn primary" disabled={!!draft.from && !!draft.to && draft.from > draft.to} onClick={() => setFilters(draft)}><Search size={18}/>Aplicar filtros</button>
    </Panel>
    {loading && <p role="status">Cargando historial...</p>}
    {error && <div className="notice" role="alert">{error}<button className="btn" onClick={() => { setError(""); setLoading(true); setAttempt(value => value + 1); }}>Reintentar</button></div>}
    {!loading && !error && <><div className="kpi-grid">
      <KpiCard label="Inferencias" value={monitoring.requests.toLocaleString("es-CO")} icon={FileStack}/>
      <KpiCard label="Exactitud vs. etiqueta humana" value={percentage(monitoring.accuracy)} icon={CircleCheck} tone="green"/>
      <KpiCard label="Latencia p95" value={monitoring.p95LatencyMs === null ? "—" : `${Math.round(monitoring.p95LatencyMs)} ms`} icon={Clock3}/>
      <KpiCard label="Tasa de error" value={monitoring.errorRate === null ? "—" : `${(monitoring.errorRate * 100).toFixed(1)}%`} note="Con base en las respuestas sin formato válido" icon={AlertTriangle} tone="red"/>
    </div>
    <MonitoringCharts daily={monitoring.dailyVolume} distribution={monitoring.labelDistribution}/>
    <Panel className="table-panel"><h2>Historial de inferencias</h2><div className="table-scroll"><table className="data-table">
      <thead><tr><th>Fecha y hora</th><th>ID</th><th>Ejemplo</th><th>Modelo</th><th>Predicción</th><th>Etiqueta humana</th><th>Acierto</th><th>Puntaje</th><th>Latencia</th><th>Estado</th></tr></thead>
      <tbody>{filtered.map(p => <tr key={p.prediction_id}>
        <td>{new Date(p.timestamp).toLocaleString("es-CO")}</td>
        <td><Link href={`/monitoreo/${p.prediction_id}`}>{p.prediction_id.slice(0, 8)}</Link></td>
        <td>{p.example_id}</td>
        <td>{modelTypeName(p.model_type)}<small className="cell-sub">{p.model_name}</small></td>
        <td><strong>{functionName(p.predicted_label)}</strong></td>
        <td>{functionName(p.human_label)}</td>
        <td><MatchBadge ok={p.is_correct}/></td>
        <td>{percentage(p.confidence)}</td>
        <td>{p.status === "pending" ? "—" : `${Math.round(p.latency_ms)} ms`}</td>
        <td><StatusBadge status={p.status}/></td>
      </tr>)}</tbody></table></div>{filtered.length === 0 && <p className="no-results">No hay inferencias para los filtros seleccionados.</p>}</Panel></>}
  </div>;
}
