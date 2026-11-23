import os
import uuid

from sqlalchemy import Boolean, Column, DateTime, Enum as SAEnum, Float, String, Text, create_engine
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import DeclarativeBase, sessionmaker
from sqlalchemy.sql import func

from schemas import CitationFunction, ModelType, Status

DATABASE_URL = os.getenv("DATABASE_URL", "postgresql+psycopg://citas:citas@db:5432/citas")

engine = create_engine(DATABASE_URL, pool_pre_ping=True)
SessionLocal = sessionmaker(bind=engine)


class Base(DeclarativeBase):
    pass


def _enum(enum_cls, name):
    return SAEnum(enum_cls, name=name, values_callable=lambda e: [i.value for i in e])


function_enum = _enum(CitationFunction, "citation_function_enum")
model_type_enum = _enum(ModelType, "model_type_enum")
status_enum = _enum(Status, "status_enum")


class InferenceLog(Base):
    __tablename__ = "inference_logs"

    prediction_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    timestamp = Column(DateTime(timezone=True), server_default=func.now())
    example_id = Column(String, nullable=False)
    model_type = Column(model_type_enum, nullable=False)
    model_name = Column(String, nullable=False)
    predicted_label = Column(function_enum)
    confidence = Column(Float)
    class_scores = Column(JSONB)
    human_label = Column(function_enum, nullable=False)
    is_correct = Column(Boolean)
    latency_ms = Column(Float, nullable=False)
    status = Column(status_enum, nullable=False)
    error_detail = Column(String)
    token_audit = Column(JSONB)
    llm_input = Column(Text)
    raw_response = Column(Text)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
