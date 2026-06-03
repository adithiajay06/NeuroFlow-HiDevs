from pydantic import BaseModel, Field, validator
from typing import List, Dict, Optional

class IngestionConfig(BaseModel):
    chunking_strategy: str
    chunk_size_tokens: int
    chunk_overlap_tokens: int
    extractors_enabled: List[str]

class RetrievalConfig(BaseModel):
    dense_k: int
    sparse_k: int
    reranker: str
    top_k_after_rerank: int
    query_expansion: bool
    metadata_filters_enabled: bool

class GenerationConfig(BaseModel):
    model_routing: Dict[str, str]
    max_context_tokens: int
    temperature: float
    system_prompt_variant: str

class EvaluationConfig(BaseModel):
    auto_evaluate: bool
    training_threshold: float

class PipelineConfig(BaseModel):
    name: str
    description: str
    ingestion: IngestionConfig
    retrieval: RetrievalConfig
    generation: GenerationConfig
    evaluation: EvaluationConfig

    @validator("*", pre=True)
    def no_extra_keys(cls, v, field):
        if isinstance(v, dict):
            allowed = set(field.type_.__fields__.keys())
            extra = set(v.keys()) - allowed
            if extra:
                raise ValueError(f"Unknown keys in {field.name}: {extra}")
        return v
