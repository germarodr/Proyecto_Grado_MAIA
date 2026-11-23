import type { ApiExample, ApiHealth, ApiPrediction, ModelType } from "./api-types";

async function request<T>(path: string, init?: RequestInit): Promise<T> {
  const response = await fetch(`/api/${path}`, { ...init, cache: "no-store" });
  const body = await response.json();
  if (!response.ok) {
    const detail = typeof body.detail === "string" ? body.detail
      : Array.isArray(body.detail) ? body.detail.map((d: { msg: string }) => d.msg).join(" ")
      : "No se pudo completar la solicitud.";
    throw new Error(detail);
  }
  return body as T;
}

export const getHealth = (signal?: AbortSignal) => request<ApiHealth>("health", { signal });
export const listExamples = (signal?: AbortSignal) => request<ApiExample[]>("examples", { signal });
export const listPredictions = (signal?: AbortSignal) => request<ApiPrediction[]>("predictions", { signal });
export const createPrediction = (example_id: string, model_type: ModelType) => request<ApiPrediction>("predictions", {
  method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify({ example_id, model_type }),
});
