import asyncio
import math
from typing import AsyncGenerator
from openai import AsyncOpenAI
from openai.error import RateLimitError

from .base import BaseLLMProvider, ChatMessage, GenerationResult

# Hardcoded price table (USD per million tokens)
PRICE_TABLE = {
    "gpt-4o": {"input": 2.50, "output": 10.00},
    "gpt-4o-mini": {"input": 0.15, "output": 0.60},
}

class OpenAIProvider(BaseLLMProvider):
    def __init__(self, api_key: str, model: str = "gpt-4o-mini"):
        self.client = AsyncOpenAI(api_key=api_key)
        self.model = model

    @property
    def cost_per_input_token(self) -> float:
        return PRICE_TABLE[self.model]["input"] / 1_000_000

    @property
    def cost_per_output_token(self) -> float:
        return PRICE_TABLE[self.model]["output"] / 1_000_000

    @property
    def context_window(self) -> int:
        return 128_000 if self.model == "gpt-4o" else 32_000

    async def complete(self, messages: list[ChatMessage], **kwargs) -> GenerationResult:
        retries = 0
        while retries < 3:
            try:
                response = await self.client.chat.completions.create(
                    model=self.model,
                    messages=[{"role": m.role, "content": m.content} for m in messages],
                    **kwargs
                )
                choice = response.choices[0]
                usage = response.usage
                return GenerationResult(
                    content=choice.message.content,
                    model=self.model,
                    input_tokens=usage.prompt_tokens,
                    output_tokens=usage.completion_tokens,
                    latency_ms=response.response_ms,
                    cost_usd=(usage.prompt_tokens * self.cost_per_input_token +
                              usage.completion_tokens * self.cost_per_output_token),
                    finish_reason=choice.finish_reason,
                )
            except RateLimitError as e:
                retry_after = getattr(e, "retry_after", 1)
                await asyncio.sleep(retry_after * (2 ** retries))
                retries += 1
        raise RuntimeError("OpenAIProvider: Rate limit exceeded after retries")

    async def stream(self, messages: list[ChatMessage], **kwargs) -> AsyncGenerator[str, None]:
        async with self.client.chat.completions.stream(
            model=self.model,
            messages=[{"role": m.role, "content": m.content} for m in messages],
            **kwargs
        ) as stream:
            async for event in stream:
                if event.type == "message.delta":
                    yield event.delta.content or ""
                elif event.type == "message.completed":
                    break

    async def embed(self, texts: list[str]) -> list[list[float]]:
        response = await self.client.embeddings.create(
            model="text-embedding-3-small",
            input=texts
        )
        return [item.embedding for item in response.data]
