import asyncio
from typing import AsyncGenerator
from anthropic import AsyncAnthropic
from anthropic.error import RateLimitError

from .base import BaseLLMProvider, ChatMessage, GenerationResult

# Example price table (USD per million tokens)
PRICE_TABLE = {
    "claude-3-opus": {"input": 3.00, "output": 15.00},
    "claude-3-haiku": {"input": 0.25, "output": 1.25},
}

class AnthropicProvider(BaseLLMProvider):
    def __init__(self, api_key: str, model: str = "claude-3-haiku"):
        self.client = AsyncAnthropic(api_key=api_key)
        self.model = model

    @property
    def cost_per_input_token(self) -> float:
        return PRICE_TABLE[self.model]["input"] / 1_000_000

    @property
    def cost_per_output_token(self) -> float:
        return PRICE_TABLE[self.model]["output"] / 1_000_000

    @property
    def context_window(self) -> int:
        return 200_000 if self.model == "claude-3-opus" else 32_000

    async def complete(self, messages: list[ChatMessage], **kwargs) -> GenerationResult:
        retries = 0
        while retries < 3:
            try:
                # Anthropic expects system prompt separately
                system_msg = next((m.content for m in messages if m.role == "system"), None)
                user_msgs = [{"role": m.role, "content": m.content} for m in messages if m.role != "system"]

                response = await self.client.messages.create(
                    model=self.model,
                    system=system_msg,
                    messages=user_msgs,
                    **kwargs
                )
                usage = response.usage
                return GenerationResult(
                    content=response.content[0].text,
                    model=self.model,
                    input_tokens=usage.input_tokens,
                    output_tokens=usage.output_tokens,
                    latency_ms=response.response_ms,
                    cost_usd=(usage.input_tokens * self.cost_per_input_token +
                              usage.output_tokens * self.cost_per_output_token),
                    finish_reason=response.stop_reason,
                )
            except RateLimitError as e:
                retry_after = getattr(e, "retry_after", 1)
                await asyncio.sleep(retry_after * (2 ** retries))
                retries += 1
        raise RuntimeError("AnthropicProvider: Rate limit exceeded after retries")

    async def stream(self, messages: list[ChatMessage], **kwargs) -> AsyncGenerator[str, None]:
        system_msg = next((m.content for m in messages if m.role == "system"), None)
        user_msgs = [{"role": m.role, "content": m.content} for m in messages if m.role != "system"]

        async with self.client.messages.stream(
            model=self.model,
            system=system_msg,
            messages=user_msgs,
            **kwargs
        ) as stream:
            async for event in stream:
                if event.type == "message.delta":
                    yield event.delta.text or ""
                elif event.type == "message.stop":
                    break

    async def embed(self, texts: list[str]) -> list[list[float]]:
        response = await self.client.embeddings.create(
            model="claude-embedding-1",
            input=texts
        )
        return [item.embedding for item in response.data]
