import datetime as dt
import uuid
from enum import Enum

from pydantic import BaseModel, ConfigDict


class CitationFunction(str, Enum):
    BACKGROUND = "Background"
    GAP = "Gap"
    BASIS = "Basis"
    COMPARISON = "Comparison"
    APPLICATION = "Application"
    IMPROVEMENT = "Improvement/Modification"
    EVIDENCE = "Evidence"
    ORIGINATOR = "Identification of the Originator"
    FURTHER_READING = "Further Reading"


class ModelType(str, Enum):
    ENCODER = "encoder"
    OPEN_WEIGHT = "open_weight"
    COMMERCIAL = "commercial"


class Status(str, Enum):
    SUCCESS = "success"
    ERROR = "error"
    PENDING = "pending"


class Chunk(BaseModel):
    rank: int
    section: str
    text: str


class Example(BaseModel):
    example_id: str
    citing_title: str
    cited_title: str
    citing_url: str
    cited_url: str
    citing_license: str
    cited_license: str
    context: str
    cited_abstract: str
    top3: list[Chunk]
    label: CitationFunction


class PredictionRequest(BaseModel):
    example_id: str
    model_type: ModelType


class PredictionResponse(BaseModel):
    prediction_id: uuid.UUID
    timestamp: dt.datetime
    example_id: str
    model_type: ModelType
    model_name: str
    predicted_label: CitationFunction | None
    confidence: float | None
    class_scores: dict[str, float] | None
    human_label: CitationFunction
    is_correct: bool | None
    latency_ms: float
    status: Status
    error_detail: str | None
    token_audit: dict | None
    llm_input: str | None
    raw_response: str | None

    model_config = ConfigDict(from_attributes=True, protected_namespaces=())


class ModelInfo(BaseModel):
    name: str | None
    available: bool
    detail: str


class HealthResponse(BaseModel):
    status: str
    models: dict[ModelType, ModelInfo]
