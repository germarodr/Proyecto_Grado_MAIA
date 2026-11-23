import functions from "../../data/functions.json";
import type { ApiPrediction, ModelType } from "./api-types";

export type Probability = { category: string; name: string; color: string; value: number };

export const MODEL_TYPES: { id: ModelType; name: string; description: string }[] = [
  { id: "encoder", name: "Encoder fine-tuned", description: "SciBERT ajustado: contexto + 3 fragmentos con su sección" },
  { id: "open_weight", name: "Modelo open-weight", description: "{model} (Hugging Face) con el prompt de A5: contexto + título y resumen" },
  { id: "commercial", name: "Modelo comercial", description: "Gemini 3.5 Flash-Lite (A5): contexto + título y resumen del citado" },
];

export const modelLabel = (id: string | null) =>
  id ? id.split("/").pop()!.split(":")[0].replace(/-GGUF$/i, "").replace(/^Meta-/, "").replace(/-/g, " ") : "Modelo de pesos abiertos";

export const licenseLabel = (url: string) => {
  const m = url.match(/licenses\/([a-z-]+)\/([\d.]+)/i);
  return m ? `CC ${m[1].toUpperCase()} ${m[2]}` : "Licencia";
};

export const modelTypeName = (id: string) => MODEL_TYPES.find(m => m.id === id)?.name ?? id;
export const findFunction = (code: string | null) => functions.find(f => f.code === code);
export const functionName = (code: string | null) => findFunction(code)?.nameEs ?? code ?? "Sin predicción";

export const cleanSection = (section: string) =>
  section.replace(/\{\{(\w+):[^}]*\}\}/g, (_, kind: string) => `[${kind.toUpperCase()}]`).trim() || "Sin sección";

export function predictionDetail(item: ApiPrediction) {
  return {
    predictionId: item.prediction_id,
    timestamp: item.timestamp,
    exampleId: item.example_id,
    modelType: item.model_type,
    modelName: item.model_name,
    predictedLabel: item.predicted_label,
    predictedName: functionName(item.predicted_label),
    confidence: item.confidence,
    humanLabel: item.human_label,
    isCorrect: item.is_correct,
    latencyMs: Math.round(item.latency_ms),
    status: item.status,
    errorDetail: item.error_detail,
    tokenAudit: item.token_audit,
    llmInput: item.llm_input,
    rawResponse: item.raw_response,
    probabilities: Object.entries(item.class_scores ?? {})
      .map(([category, value]) => ({ category, name: functionName(category), color: findFunction(category)?.color ?? "#1168dc", value }))
      .sort((a, b) => b.value - a.value),
  };
}

export function monitoringSummary(items: ApiPrediction[]) {
  const done = items.filter(item => item.status !== "pending");
  const scored = done.filter(item => item.is_correct !== null);
  const latencies = done.map(item => item.latency_ms).sort((a, b) => a - b);
  const daily = new Map<string, number>();
  for (const item of items) {
    const date = localDate(item.timestamp);
    daily.set(date, (daily.get(date) ?? 0) + 1);
  }
  return {
    requests: items.length,
    accuracy: scored.length ? scored.filter(item => item.is_correct).length / scored.length : null,
    p95LatencyMs: latencies.length ? latencies[Math.ceil(latencies.length * 0.95) - 1] : null,
    errorRate: done.length ? done.filter(item => item.status === "error").length / done.length : null,
    dailyVolume: [...daily].sort(([a], [b]) => a.localeCompare(b)).map(([date, requests]) => ({ date, requests })),
    labelDistribution: functions.map(({ code, nameEs }) => ({
      category: nameEs, count: items.filter(item => item.predicted_label === code).length,
    })),
  };
}

export function localDate(timestamp: string) {
  const date = new Date(timestamp);
  return `${date.getFullYear()}-${String(date.getMonth() + 1).padStart(2, "0")}-${String(date.getDate()).padStart(2, "0")}`;
}

export const percentage = (value: number | null) => value === null ? "—" : `${Math.round(value * 100)}%`;
