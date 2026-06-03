import asyncio
from typing import List
from .base import ChatMessage, GenerationResult, BaseLLMProvider

class FallbackChain:
    def __init__(self, providers: List[BaseLLMProvider]):
        self.providers = providers

    async def complete(self, messages: list[ChatMessage], **kwargs) -> GenerationResult:
        last_error = None
        for provider in self.providers:
            try:
                return await provider.complete(messages, **kwargs)
            except Exception as e:
                last_error = e
                continue
        raise RuntimeError(f"All providers failed. Last error: {last_error}")

    async def stream(self, messages: list[ChatMessage], **kwargs):
        last_error = None
        for provider in self.providers:
            try:
                async for token in provider.stream(messages, **kwargs):
                    yield token
                return
            except Exception as e:
                last_error = e
                continue
        raise RuntimeError(f"All providers failed during stream. Last error: {last_error}")
S
