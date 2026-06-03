import json
import aioredis
from typing import Optional

from .openai_provider import OpenAIProvider
from .anthropic_provider import AnthropicProvider
from .base import ChatMessage, GenerationResult

class RoutingCriteria:
    def __init__(
        self,
        task_type: str,                # "rag_generation" | "evaluation" | "embedding" | "classification"
        max_cost_per_call: Optional[float] = None,
        require_vision: bool = False,
        require_long_context: bool = False,
        latency_budget_ms: Optional[int] = None,
        prefer_fine_tuned: bool = False,
    ):
        self.task_type = task_type
        self.max_cost_per_call = max_cost_per_call
        self.require_vision = require_vision
        self.require_long_context = require_long_context
        self.latency_budget_ms = latency_budget_ms
        self.prefer_fine_tuned = prefer_fine_tuned


class ModelRouter:
    def __init__(self, redis_url: str, openai_key: str, anthropic_key: str):
        self.redis = aioredis.from_url(redis_url, decode_responses=True)
        self.providers = {
            "openai": OpenAIProvider(api_key=openai_key),
            "anthropic": AnthropicProvider(api_key=anthropic_key),
        }

    async def get_registered_models(self):
        raw = await self.redis.get("router:models")
        if not raw:
            return []
        return json.loads(raw)

    async def route(self, criteria: RoutingCriteria):
        models = await self.get_registered_models()

        # Apply routing rules
        candidates = []
        for m in models:
            if criteria.require_vision and not m.get("vision", False):
                continue
            if criteria.require_long_context and m.get("context_window", 0) < 100_000:
                continue
            if criteria.task_type == "evaluation" and m.get("type") != "judge":
                continue
            if criteria.prefer_fine_tuned and m.get("fine_tuned", False):
                candidates.append(m)
                continue
            if criteria.max_cost_per_call:
                est_cost = m["cost_per_input_token"] * 1000  # rough estimate
                if est_cost > criteria.max_cost_per_call:
                    continue
            candidates.append(m)

        if not candidates:
            raise RuntimeError("No models satisfy routing criteria")

        # Default: cheapest model that satisfies constraints
        chosen = min(candidates, key=lambda m: m["cost_per_input_token"])
        provider = self.providers[chosen["provider"]]
        return provider, chosen["name"]
