"use client";
import { useEffect, useMemo, useState } from "react";
import Link from "next/link";
import { AlertTriangle, BookOpen, Boxes, ChevronLeft, ChevronRight, Cloud, Cpu, ExternalLink, Layers, ScanSearch, Shuffle, Trophy } from "lucide-react";
import { ProbabilityBars } from "@/components/probability-bars";
import { MatchBadge, PageHeading, Panel } from "@/components/ui";
import { createPrediction, getHealth, listExamples, listPredictions } from "@/lib/api-client";
import type { ApiExample, ApiHealth, ModelType } from "@/lib/api-types";
import { cleanSection, findFunction, functionName, licenseLabel, MODEL_TYPES, modelLabel, percentage, predictionDetail } from "@/lib/prediction-data";

type Result = ReturnType<typeof predictionDetail> | { error: string };
const MODEL_ICONS = { encoder: Cpu, open_weight: Boxes, commercial: Cloud };
const POLL_MS = 3000;
const MARKERS = /(\[\[TARGET\]\]|\[CITE\]|\[FORMULA\]|\[FIGURE\]|\[TABLE\])/;

function MarkedText({ text }: { text: string }) {
  return <>{text.split(MARKERS).map((part, i) =>
    part === "[[TARGET]]" ? <mark key={i} className="target-mark">[[TARGET]]</mark>
      : MARKERS.test(part) ? <span key={i} className="marker">{part}</span> : part)}</>;
}

export default function DemoPage() {
  const [examples, setExamples] = useState<ApiExample[]>([]);
  const [health, setHealth] = useState<ApiHealth | null>(null);
  const [index, setIndex] = useState(0);
  const [model, setModel] = useState<ModelType>("encoder");
  const [results, setResults] = useState<Partial<Record<ModelType, Result>>>({});
  const [running, setRunning] = useState<ModelType | null>(null);
  const [elapsed, setElapsed] = useState(0);
  const [expanded, setExpanded] = useState<number[]>([]);
  const [showAbstract, setShowAbstract] = useState(false);
  const [loadError, setLoadError] = useState("");

  useEffect(() => {
    Promise.all([listExamples(), getHealth()]).then(([ex, h]) => { setExamples(ex); setHealth(h); })
      .catch(e => setLoadError(e instanceof Error ? e.message : "No se pudo conectar con la API."));
  }, []);

  const example = examples[index];
  const select = (i: number) => { setIndex((i + examples.length) % examples.length); setResults({}); setExpanded([]); setShowAbstract(false); };
  const result = results[model];
  const ran = useMemo(() => MODEL_TYPES.filter(m => results[m.id]), [results]);

  async function classify() {
    if (!example) return;
    const target = model;
    setRunning(target);
    setElapsed(0);
    const started = Date.now();
    try {
      let response = await createPrediction(example.example_id, target);
      const id = response.prediction_id;
      while (response.status === "pending") {
        await new Promise(resolve => setTimeout(resolve, POLL_MS));
        setElapsed(Math.round((Date.now() - started) / 1000));
        response = (await listPredictions()).find(p => p.prediction_id === id) ?? response;
      }
      setResults(r => ({ ...r, [target]: response.status === "error"
        ? { error: response.error_detail ?? "No se pudo clasificar." } : predictionDetail(response) }));
    } catch (e) {
      setResults(r => ({ ...r, [target]: { error: e instanceof Error ? e.message : "No se pudo clasificar." } }));
    } finally { setRunning(null); }
  }

  if (loadError) return <div className="shell page"><Panel className="form-panel"><div className="notice" role="alert"><AlertTriangle size={20}/>{loadError}</div></Panel></div>;
  if (!example || !health) return <div className="shell page" role="status">Cargando ejemplos y modelos...</div>;

  const steps = ["Elegir ejemplo", "Fragmentos Top-3", "Clasificar", "Resultados"];
  const stepDone = [true, true, ran.length > 0, !!result && !("error" in result)];

  return <div className="shell page">
    <PageHeading title="Demostrador" subtitle="Elija un ejemplo validado por humanos, revise los fragmentos recuperados del artículo citado y compare cómo lo clasifica cada modelo."/>
    <ol className="stepper">{steps.map((s, i) => <li key={s} className={stepDone[i] ? "done" : ""}><span>{i + 1}</span>{s}</li>)}</ol>

    <div className="demo-grid">
      <div className="demo-col">
        <Panel className="form-panel">
          <h2 className="panel-title"><BookOpen/>1 · Ejemplo</h2>
          <div className="example-picker">
            <button className="btn icon" disabled={!!running} onClick={() => select(index - 1)} aria-label="Ejemplo anterior"><ChevronLeft size={18}/></button>
            <select aria-label="Ejemplo" disabled={!!running} value={index} onChange={e => select(Number(e.target.value))}>
              {examples.map((ex, i) => <option key={ex.example_id} value={i}>{ex.example_id} · {ex.citing_title} → {ex.cited_title}</option>)}
            </select>
            <button className="btn icon" disabled={!!running} onClick={() => select(index + 1)} aria-label="Ejemplo siguiente"><ChevronRight size={18}/></button>
            <button className="btn icon" disabled={!!running} onClick={() => select(Math.floor(Math.random() * examples.length))} aria-label="Ejemplo aleatorio" title="Aleatorio"><Shuffle size={18}/></button>
          </div>
          <div className="paper-label">Artículo citante · <a href={example.citing_license} target="_blank" rel="noreferrer">{licenseLabel(example.citing_license)}</a></div>
          <a className="paper-title" href={example.citing_url} target="_blank" rel="noreferrer">{example.citing_title}<ExternalLink size={14}/></a>
          <div className="context-box"><MarkedText text={example.context}/></div>
          <div className="cited-card">
            <div className="paper-label">Artículo citado ([[TARGET]]) · <a href={example.cited_license} target="_blank" rel="noreferrer">{licenseLabel(example.cited_license)}</a></div>
            <a className="paper-title" href={example.cited_url} target="_blank" rel="noreferrer">{example.cited_title}<ExternalLink size={14}/></a>
            <p className={showAbstract ? "abstract" : "abstract clamp"}>{example.cited_abstract}</p>
            <button className="link-btn" onClick={() => setShowAbstract(v => !v)}>{showAbstract ? "Ver menos" : "Ver resumen completo"}</button>
          </div>
        </Panel>

        <Panel className="form-panel">
          <h2 className="panel-title"><Layers/>2 · Fragmentos Top-3 del artículo citado</h2>
          <p className="panel-note">Recuperados previamente con SciBERT por similitud con el párrafo citante; no se calculan en ejecución. Los usa el encoder; los LLM reciben el título y el resumen. Textos de arXiv (unarXive 2022) sin cambios, salvo los marcadores de cita.</p>
          {example.top3.map(c => {
            const open = expanded.includes(c.rank);
            return <div className="chunk-card" key={c.rank}>
              <div className="chunk-head"><span className="rank">#{c.rank}</span><strong>{cleanSection(c.section)}</strong></div>
              <p className={open ? "chunk-text" : "chunk-text clamp"}><MarkedText text={c.text}/></p>
              <button className="link-btn" onClick={() => setExpanded(x => open ? x.filter(r => r !== c.rank) : [...x, c.rank])}>{open ? "Ver menos" : "Ver fragmento completo"}</button>
            </div>;
          })}
        </Panel>
      </div>

      <div className="demo-col sticky">
        <Panel className="form-panel">
          <h2 className="panel-title"><ScanSearch/>3 · Modelo</h2>
          <div className="model-picker">{MODEL_TYPES.map(m => {
            const info = health.models[m.id];
            const Icon = MODEL_ICONS[m.id];
            return <button key={m.id} type="button" disabled={!!running} className={model === m.id ? "model-option active" : "model-option"} onClick={() => setModel(m.id)}>
              <span className="icon-bubble small"><Icon size={20}/></span>
              <span><strong>{m.name}</strong><small>{m.description.replace("{model}", modelLabel(info.name))}</small>
                <em className={info.available ? "ok" : "off"}>{info.name ?? "—"} · {info.detail}</em></span>
            </button>;
          })}</div>
          <button className="btn primary wide" disabled={!!running || !health.models[model].available} onClick={classify}>
            <ScanSearch size={18}/>{running ? `Clasificando... ${elapsed} s` : `Clasificar con ${MODEL_TYPES.find(m => m.id === model)!.name.toLowerCase()}`}
          </button>
          {running === "commercial" && <p className="panel-note">Gemini suele responder en pocos segundos.</p>}
          {running === "open_weight" && <p className="panel-note">Sin GPU, Llama puede tardar varios minutos; el resultado aparece aquí al terminar y también queda en Monitoreo.</p>}
        </Panel>

        <Panel className="result-panel">
          <h2 className="panel-title"><Trophy/>4 · Resultado</h2>
          {result && "error" in result ? <div className="notice" role="alert"><AlertTriangle size={20}/>{result.error}</div>
          : result ? <>
            <div className="prediction-hero" style={{ borderColor: findFunction(result.predictedLabel)?.color }}>
              <div><div className="target">{result.predictedName}</div><h3>{result.predictedLabel} · {result.latencyMs} ms</h3></div>
              <div className="confidence"><span>{result.modelType === "encoder" ? "Probabilidad" : "Puntaje"}</span><strong>{percentage(result.confidence)}</strong></div>
            </div>
            <p className="definition">{findFunction(result.predictedLabel)?.description}</p>
            {result.errorDetail && <div className="notice"><AlertTriangle size={18}/>{result.errorDetail}</div>}
            <div className="human-row"><span>Etiqueta humana: <strong>{functionName(result.humanLabel)}</strong></span><MatchBadge ok={result.isCorrect}/></div>
            <h3>{result.modelType === "encoder" ? "Probabilidades por función (softmax)" : "Puntajes de soporte relativo (suman 1, sin calibrar)"}</h3>
            <ProbabilityBars items={result.probabilities}/>
            <h3>Información del citado usada</h3>
            {result.modelType !== "encoder"
              ? <div className="chip-row"><span className="chip">Título y resumen (A5, recorte SciBERT base)</span></div>
              : <div className="chip-row">{example.top3.map(c => <span className="chip" key={c.rank}><b>#{c.rank}</b>{cleanSection(c.section)}</span>)}</div>}
            <Link className="btn" href={`/monitoreo/${result.predictionId}`}>Ver detalle de la inferencia</Link>
          </> : <div className="empty-result"><ScanSearch size={54}/><h3>Aún sin clasificar</h3><p>Elija un modelo y seleccione “Clasificar” para ver la función predicha.</p></div>}
        </Panel>

        {ran.length > 0 && <Panel className="table-panel">
          <h2>Comparación en {example.example_id}</h2>
          <table className="data-table"><thead><tr><th>Modelo</th><th>Predicción</th><th>Puntaje</th><th>Latencia</th><th>Humana</th></tr></thead>
            <tbody>{ran.map(m => {
              const r = results[m.id]!;
              return "error" in r ? <tr key={m.id}><td>{m.name}</td><td colSpan={4} className="error-cell">{r.error}</td></tr>
                : <tr key={m.id}><td>{m.name}</td><td><strong>{r.predictedName}</strong></td><td>{percentage(r.confidence)}</td><td>{r.latencyMs} ms</td><td><MatchBadge ok={r.isCorrect}/></td></tr>;
            })}</tbody></table>
        </Panel>}
      </div>
    </div>
  </div>;
}
