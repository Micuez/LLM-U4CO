from __future__ import annotations

import json
import os
import urllib.request
from dataclasses import dataclass
from typing import Dict, Optional


class NullLLMClient:
    def generate(self, *args, **kwargs):
        raise RuntimeError("No LLM client is configured. Use provider=mock or provider=openai_compatible.")


class MockLLMClient:
    def __init__(self, canned_response: Optional[str] = None):
        self.canned_response = canned_response or (
            "def policy(state):\n"
            "    actions = []\n"
            "    actions.append({'name': 'fallback'})\n"
            "    return {'actions': actions}\n"
        )

    def generate(self, system_prompt: str, user_prompt: str, **kwargs) -> str:
        return self.canned_response


@dataclass
class OpenAICompatibleClient:
    base_url: str
    model: str
    api_key: str = ""
    timeout_s: float = 60.0

    def generate(self, system_prompt: str, user_prompt: str, temperature: float = 0.2, max_tokens: int = 800) -> str:
        payload = {
            "model": self.model,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            "temperature": temperature,
            "max_tokens": max_tokens,
        }
        data = json.dumps(payload).encode("utf-8")
        url = self.base_url.rstrip("/") + "/chat/completions"
        request = urllib.request.Request(url, data=data, method="POST")
        request.add_header("Content-Type", "application/json")
        if self.api_key:
            request.add_header("Authorization", "Bearer %s" % self.api_key)
        with urllib.request.urlopen(request, timeout=self.timeout_s) as response:
            body = json.loads(response.read().decode("utf-8"))
        return body["choices"][0]["message"]["content"]


def build_llm_client(config: Optional[Dict[str, object]] = None):
    cfg = config or {}
    provider = str(cfg.get("provider", os.environ.get("LLM4UNROLL_LLM_PROVIDER", "null")))
    if provider == "mock":
        return MockLLMClient()
    if provider == "openai_compatible":
        base_url = str(cfg.get("base_url", os.environ.get("LLM4UNROLL_LLM_BASE_URL", "")))
        model = str(cfg.get("model", os.environ.get("LLM4UNROLL_LLM_MODEL", "")))
        api_key = str(cfg.get("api_key", os.environ.get("LLM4UNROLL_LLM_API_KEY", "")))
        timeout_s = float(cfg.get("timeout_s", 60.0))
        if not base_url or not model:
            raise ValueError("openai_compatible provider requires base_url and model.")
        return OpenAICompatibleClient(base_url=base_url, model=model, api_key=api_key, timeout_s=timeout_s)
    return NullLLMClient()
