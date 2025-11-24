"""LLM client wrapper for multiple providers."""

import time
from typing import Optional, Literal

from anthropic import Anthropic
from openai import OpenAI

from .config import get_settings, get_llm_config


ProviderType = Literal["anthropic", "openai"]


class LLMClient:
    """Unified interface for LLM providers."""

    def __init__(
        self,
        provider: Optional[ProviderType] = None,
        model: Optional[str] = None
    ):
        """
        Initialize LLM client.

        Args:
            provider: "anthropic" or "openai". If None, reads from config.
            model: Model name. If None, reads from config.
        """
        self.settings = get_settings()
        self.llm_config = get_llm_config()

        # Determine provider
        self.provider = provider or self.llm_config.get("provider", "anthropic")

        # Initialize client based on provider
        if self.provider == "anthropic":
            if not self.settings.anthropic_api_key:
                raise ValueError(
                    "ANTHROPIC_API_KEY not found. "
                    "Please set it in .env file or environment."
                )
            self.client = Anthropic(api_key=self.settings.anthropic_api_key)
            self.model = model or self.llm_config["anthropic"]["model"]
            self.default_max_tokens = self.llm_config["anthropic"]["max_tokens"]
            self.default_temperature = self.llm_config["anthropic"]["temperature"]

        elif self.provider == "openai":
            if not self.settings.openai_api_key:
                raise ValueError(
                    "OPENAI_API_KEY not found. "
                    "Please set it in .env file or environment."
                )
            self.client = OpenAI(api_key=self.settings.openai_api_key)
            self.model = model or self.llm_config["openai"]["model"]
            self.default_max_tokens = self.llm_config["openai"]["max_tokens"]
            self.default_temperature = self.llm_config["openai"]["temperature"]

        else:
            raise ValueError(f"Unknown provider: {self.provider}")

        # Generation settings
        self.max_retries = self.llm_config["generation"]["max_retries"]
        self.timeout = self.llm_config["generation"]["timeout"]

    def generate(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
    ) -> str:
        """
        Generate text from prompt.

        Args:
            prompt: User prompt
            system_prompt: System prompt (optional)
            temperature: Sampling temperature (optional)
            max_tokens: Maximum tokens to generate (optional)

        Returns:
            Generated text
        """
        temperature = temperature or self.default_temperature
        max_tokens = max_tokens or self.default_max_tokens

        for attempt in range(self.max_retries):
            try:
                if self.provider == "anthropic":
                    return self._generate_anthropic(
                        prompt, system_prompt, temperature, max_tokens
                    )
                elif self.provider == "openai":
                    return self._generate_openai(
                        prompt, system_prompt, temperature, max_tokens
                    )
            except Exception as e:
                if attempt == self.max_retries - 1:
                    raise
                print(f"Retry {attempt + 1}/{self.max_retries} after error: {e}")
                time.sleep(2 ** attempt)  # Exponential backoff

        raise RuntimeError("Max retries exceeded")

    def _generate_anthropic(
        self,
        prompt: str,
        system_prompt: Optional[str],
        temperature: float,
        max_tokens: int
    ) -> str:
        """Generate using Anthropic Claude."""
        kwargs = {
            "model": self.model,
            "max_tokens": max_tokens,
            "temperature": temperature,
            "messages": [{"role": "user", "content": prompt}]
        }

        if system_prompt:
            kwargs["system"] = system_prompt

        response = self.client.messages.create(**kwargs)
        return response.content[0].text

    def _generate_openai(
        self,
        prompt: str,
        system_prompt: Optional[str],
        temperature: float,
        max_tokens: int
    ) -> str:
        """Generate using OpenAI GPT."""
        messages = []

        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})

        messages.append({"role": "user", "content": prompt})

        response = self.client.chat.completions.create(
            model=self.model,
            messages=messages,
            temperature=temperature,
            max_tokens=max_tokens
        )

        return response.choices[0].message.content

    def count_tokens_estimate(self, text: str) -> int:
        """
        Rough estimate of token count.
        For accurate counts, use tiktoken (OpenAI) or anthropic tokenizer.
        """
        # Rough approximation: 1 token ≈ 4 characters
        return len(text) // 4


def create_client(
    provider: Optional[ProviderType] = None,
    model: Optional[str] = None
) -> LLMClient:
    """Factory function to create LLM client."""
    return LLMClient(provider=provider, model=model)
