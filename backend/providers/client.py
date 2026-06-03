import time
import aioredis
from opentelemetry import trace

from .base import ChatMessage, GenerationResult
from .openai_provider import OpenAIProvider
from .anthropic_provider import AnthropicProvider
from .router import ModelRouter, RoutingCriteria

class NeuroFlowClient:
    _instance = None

    def __init__(self, redis_url: str, openai_key: str, anthropic_key: str):
        self.redis = aioredis.from_url(redis_url, decode_responses=True)
        self.providers = {
            "openai": OpenAIProvider(api_key=openai_key),
            "anthropic": AnthropicProvider(api_key=anthropic_key),
        }
        self.router = ModelRouter(redis_url, openai_key, anthropic_key)
        self.tracer = trace.get_tracer("neuroflow.providers")

    @classmethod
    def get_instance(cls, redis_url: str, openai_key: str, anthropic_key: str):
        if cls._instance is None:
            cls._instance = NeuroFlowClient(redis_url, openai_key, anthropic_key)
        return cls._instance

    async def chat(self, messages: list[ChatMessage], criteria: RoutingCriteria) -> GenerationResult:
        provider, model = await self.router.route(criteria)
        start = time.time()
        with self.tracer.start_as_current_span("llm.complete") as span:
            result = await provider.complete(messages, model=model)
            latency = (time.time() - start) * 1000
            span.set_attribute("model", model)
            span.set_attribute("input_tokens", result.input_tokens)
            span.set_attribute("output_tokens", result.output_tokens)
            span.set_attribute("cost_usd", result.cost_usd)
            span.set_attribute("latency_ms", latency)
            # Track metrics in Redis
            await self.redis.incr(f"metrics:model:{model}:calls")
            await self.redis.incrbyfloat(f"metrics:model:{model}:cost_usd", result.cost_usd)
            return result

    async def embed(self, texts: list[str], criteria: RoutingCriteria) -> list[list[float]]:
        provider, model = await self.router.route(criteria)
        with self.tracer.start_as_current_span("llm.embed") as span:
            embeddings = await provider.embed(texts)
            span.set_attribute("model", model)
            span.set_attribute("
