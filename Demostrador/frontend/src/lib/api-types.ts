export type ModelType = "encoder" | "open_weight" | "commercial";
export type Chunk = { rank: number; section: string; text: string };

export type ApiExample = {
  example_id: string;
  citing_title: string;
  cited_title: string;
  citing_url: string;
  cited_url: string;
  citing_license: string;
  cited_license: string;
  context: string;
  cited_abstract: string;
  top3: Chunk[];
  label: string;
};

export type ApiPrediction = {
  prediction_id: string;
  timestamp: string;
  example_id: string;
  model_type: ModelType;
  model_name: string;
  predicted_label: string | null;
  confidence: number | null;
  class_scores: Record<string, number> | null;
  human_label: string;
  is_correct: boolean | null;
  latency_ms: number;
  status: "success" | "error" | "pending";
  error_detail: string | null;
  token_audit: Record<string, number> | null;
  llm_input: string | null;
  raw_response: string | null;
};

export type ModelInfo = { name: string | null; available: boolean; detail: string };
export type ApiHealth = { status: string; models: Record<ModelType, ModelInfo> };
