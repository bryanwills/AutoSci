"""Thin async LLM client for SciDAG operators.

Replaces MaAS's MetaGPT `llm.aask` with a dependency-free client that speaks
the OpenAI chat-completions protocol against AutoSci's configured endpoint.
Reads the same environment variables the llm-review MCP server uses:

    LLM_API_KEY        required to enable real calls
    LLM_BASE_URL       default https://api.openai.com/v1
    LLM_MODEL          model name
    LLM_FALLBACK_MODEL optional fallback on primary failure

The async surface is `await client.aask(prompt, system=...)`, matching the
shape MaAS operators expect, so operator bodies port over with minimal edits.
Network I/O (urllib) runs in a worker thread via asyncio.to_thread so many
operator nodes can be awaited concurrently without blocking the event loop.

`MockLLMClient` provides a deterministic, network-free implementation for
smoke-testing the DAG executor without an API key.
"""
from __future__ import annotations

import asyncio
import json
import os
import urllib.error
import urllib.request
from typing import Callable, List, Optional


def _load_dotenv() -> None:
    """Populate os.environ from project-root .env and ~/.env (minimal parser).

    Mirrors mcp-servers/llm-review/server.py so SciDAG reads the same config
    without requiring the user to export keys in every shell.
    """
    here = os.path.dirname(os.path.abspath(__file__))
    candidates = [
        os.environ.get("SCIDAG_ENV_FILE"),
        os.path.join(here, "..", ".env"),  # AutoSci project root (scidag/ is one level down)
        os.path.join(os.path.expanduser("~"), ".env"),
    ]
    for path in candidates:
        if path and os.path.isfile(path):
            try:
                with open(path) as f:
                    for line in f:
                        line = line.strip()
                        if not line or line.startswith("#") or "=" not in line:
                            continue
                        k, v = line.split("=", 1)
                        os.environ.setdefault(k.strip(), v.strip().strip('"').strip("'"))
            except Exception:
                pass


class LLMClient:
    """OpenAI-compatible chat client. One instance is shared by all operators.

    Tracks `n_calls` (the cost-manager equivalent from MaAS) so the executor /
    controller can measure per-layer call budgets for conditional pruning.
    """

    def __init__(
        self,
        api_key: Optional[str] = None,
        base_url: Optional[str] = None,
        model: Optional[str] = None,
        fallback_model: Optional[str] = None,
        temperature: float = 0.7,
        timeout: int = 180,
    ) -> None:
        _load_dotenv()
        self.api_key = api_key or os.environ.get("LLM_API_KEY", "")
        self.base_url = (base_url or os.environ.get("LLM_BASE_URL", "https://api.openai.com/v1")).rstrip("/")
        self.model = model or os.environ.get("LLM_MODEL", "")
        self.fallback_model = fallback_model or os.environ.get("LLM_FALLBACK_MODEL", "")
        self.temperature = temperature
        self.timeout = timeout
        self.n_calls = 0  # total completions issued (cost proxy)

    def _chat_once(self, messages: List[dict], model: str, temperature: float) -> str:
        payload = {"messages": messages, "model": model, "temperature": temperature}
        req = urllib.request.Request(
            self.base_url + "/chat/completions",
            data=json.dumps(payload).encode("utf-8"),
            headers={
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json",
            },
            method="POST",
        )
        with urllib.request.urlopen(req, timeout=self.timeout) as resp:
            body = json.loads(resp.read().decode("utf-8"))
        return body["choices"][0]["message"]["content"] or ""

    def _chat_blocking(self, prompt: str, system: Optional[str], temperature: float) -> str:
        messages = []
        if system:
            messages.append({"role": "system", "content": system})
        messages.append({"role": "user", "content": prompt})
        models = [m for m in (self.model, self.fallback_model) if m] or [""]
        last_err = ""
        for model in models:
            for _attempt in range(2):  # one retry on transient error
                try:
                    return self._chat_once(messages, model, temperature)
                except urllib.error.HTTPError as e:
                    last_err = f"HTTP {e.code}: {e.read().decode('utf-8', 'ignore')[:200]}"
                except Exception as e:  # noqa: BLE001 — surface any transport error
                    last_err = f"{type(e).__name__}: {e}"
        raise RuntimeError(f"LLM call failed after retries/fallback: {last_err}")

    async def aask(
        self,
        prompt: str,
        system: Optional[str] = None,
        temperature: Optional[float] = None,
        stream: bool = False,  # accepted for signature parity; unused (no streaming)
    ) -> str:
        """Async chat call. Returns the assistant message text."""
        self.n_calls += 1
        temp = self.temperature if temperature is None else temperature
        return await asyncio.to_thread(self._chat_blocking, prompt, system, temp)

    def is_configured(self) -> bool:
        return bool(self.api_key)


class MockLLMClient:
    """Deterministic, network-free LLM for smoke tests.

    Pass a `responder(prompt, system) -> str` to control output; the default
    echoes a short stub plus a hash of the prompt so distinct calls differ.
    Honors the same `aask` surface and `n_calls` counter as LLMClient.
    """

    def __init__(self, responder: Optional[Callable[[str, Optional[str]], str]] = None) -> None:
        self.responder = responder
        self.n_calls = 0

    async def aask(
        self,
        prompt: str,
        system: Optional[str] = None,
        temperature: Optional[float] = None,
        stream: bool = False,
    ) -> str:
        self.n_calls += 1
        await asyncio.sleep(0)  # yield, so concurrency is real
        if self.responder is not None:
            return self.responder(prompt, system)
        return f"[mock idea #{self.n_calls}] " + prompt.strip().splitlines()[0][:80]

    def is_configured(self) -> bool:
        return True
