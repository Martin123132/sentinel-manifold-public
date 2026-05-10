"""Model-provider adapters for Sentinel Manifold gateway checks.

The adapters are dependency-light by design. OpenAI and Ollama calls use the
standard library so the repo remains runnable in a fresh Windows checkout.
"""

from __future__ import annotations

import json
import os
import re
import urllib.error
import urllib.parse
import urllib.request
from copy import deepcopy
from typing import Any


DEFAULT_PROVIDER = "local_demo"
DEFAULT_MODELS = {
    "local_demo": "sentinel-demo-v1",
    "ollama": "llama3.1",
    "openai": "gpt-4o-mini",
    "anthropic": "claude-3-5-haiku-20241022",
    "gemini": "gemini-2.5-flash",
}


def list_providers() -> list[dict[str, Any]]:
    """Return provider metadata for the dashboard and API."""

    return [
        {
            "id": "local_demo",
            "name": "Local Demo",
            "default_model": DEFAULT_MODELS["local_demo"],
            "requires": [],
            "description": "Deterministic built-in candidate generator for demos and tests.",
        },
        {
            "id": "ollama",
            "name": "Ollama",
            "default_model": DEFAULT_MODELS["ollama"],
            "requires": ["OLLAMA_HOST"],
            "description": "Calls a local Ollama chat model and guards the response.",
        },
        {
            "id": "openai",
            "name": "OpenAI",
            "default_model": DEFAULT_MODELS["openai"],
            "requires": ["OPENAI_API_KEY"],
            "description": "Calls OpenAI Chat Completions and guards generated candidates.",
        },
        {
            "id": "anthropic",
            "name": "Anthropic",
            "default_model": DEFAULT_MODELS["anthropic"],
            "requires": ["ANTHROPIC_API_KEY"],
            "description": "Calls Anthropic Messages and guards generated candidates.",
        },
        {
            "id": "gemini",
            "name": "Gemini",
            "default_model": DEFAULT_MODELS["gemini"],
            "requires": ["GEMINI_API_KEY"],
            "description": "Calls Google Gemini generateContent and guards generated candidates.",
        },
    ]


def generate_candidates(payload: dict[str, Any]) -> dict[str, Any]:
    """Generate candidates from a configured provider."""

    provider = str(payload.get("provider") or DEFAULT_PROVIDER)
    model = str(payload.get("model") or DEFAULT_MODELS.get(provider, "unknown"))
    prompt = str(payload.get("prompt") or "").strip()
    references = _coerce_references(payload.get("references", []))
    candidate_count = max(1, min(5, int(payload.get("candidate_count") or 3)))

    if provider == "local_demo":
        candidates = _local_demo_candidates(prompt, references, candidate_count)
        return _trace(provider, model, prompt, candidates, "generated")
    if provider == "ollama":
        candidates = _ollama_candidates(prompt, references, model, candidate_count)
        return _trace(provider, model, prompt, candidates, "generated")
    if provider == "openai":
        candidates = _openai_candidates(prompt, references, model, candidate_count)
        return _trace(provider, model, prompt, candidates, "generated")
    if provider == "anthropic":
        candidates = _anthropic_candidates(prompt, references, model, candidate_count)
        return _trace(provider, model, prompt, candidates, "generated")
    if provider == "gemini":
        candidates = _gemini_candidates(prompt, references, model, candidate_count)
        return _trace(provider, model, prompt, candidates, "generated")

    raise ProviderError(f"Unsupported provider: {provider}")


class ProviderError(RuntimeError):
    """Raised when a provider cannot generate candidates."""


def _trace(
    provider: str,
    model: str,
    prompt: str,
    candidates: list[dict[str, str]],
    status: str,
) -> dict[str, Any]:
    return {
        "provider": provider,
        "model": model,
        "prompt": prompt,
        "status": status,
        "candidate_count": len(candidates),
        "candidates": candidates,
    }


def _local_demo_candidates(prompt: str, references: list[str], count: int) -> list[dict[str, str]]:
    """Create deterministic candidate outputs for an attention-grabbing demo."""

    safe = " ".join(references[:3]).strip()
    if not safe:
        safe = "No supported answer can be emitted without reference material."

    drift = _make_drift_candidate(references)
    overclaim = _make_overclaim_candidate(prompt, references)
    pool = [safe, drift, overclaim]

    return [
        {
            "id": f"generated-{index + 1}",
            "label": f"Generated {chr(65 + index)}",
            "text": text,
        }
        for index, text in enumerate(pool[:count])
    ]


def _make_drift_candidate(references: list[str]) -> str:
    joined = "\n".join(references)
    replacements = [
        ("Earth orbits the Sun", "The Sun orbits Earth"),
        ("earth orbits the sun", "the sun orbits earth"),
        ("Paris", "London"),
        ("100 degrees Celsius", "90 degrees Celsius"),
        ("100 Celsius", "90 Celsius"),
    ]
    for old, new in replacements:
        if old in joined:
            return joined.replace(old, new, 1).split("\n")[0]

    first = references[0] if references else "The reference answer is supported."
    return f"{first} This is always correct and never fails."


def _make_overclaim_candidate(prompt: str, references: list[str]) -> str:
    topic = "the answer"
    if prompt:
        words = re.findall(r"[A-Za-z][A-Za-z0-9_-]+", prompt)
        if words:
            topic = " ".join(words[:5]).lower()
    if references:
        return f"{references[-1]} This fully solves {topic} and is guaranteed to be final."
    return f"This fully solves {topic} and is guaranteed to be final."


def _ollama_candidates(prompt: str, references: list[str], model: str, count: int) -> list[dict[str, str]]:
    host = os.environ.get("OLLAMA_HOST", "http://127.0.0.1:11434").rstrip("/")
    candidates = []
    for index in range(count):
        body = {
            "model": model,
            "stream": False,
            "messages": _chat_messages(prompt, references, index),
        }
        data = _post_json(f"{host}/api/chat", body, headers={})
        text = data.get("message", {}).get("content") or data.get("response") or ""
        candidates.append(
            {
                "id": f"ollama-{index + 1}",
                "label": f"Ollama {chr(65 + index)}",
                "text": str(text).strip(),
            }
        )
    return [candidate for candidate in candidates if candidate["text"]]


def _openai_candidates(prompt: str, references: list[str], model: str, count: int) -> list[dict[str, str]]:
    api_key = os.environ.get("OPENAI_API_KEY")
    if not api_key:
        raise ProviderError("OPENAI_API_KEY is required for provider=openai")

    body = {
        "model": model,
        "n": count,
        "messages": _chat_messages(prompt, references, 0),
        "temperature": 0.2,
    }
    data = _post_json(
        "https://api.openai.com/v1/chat/completions",
        body,
        headers={"Authorization": f"Bearer {api_key}"},
    )
    choices = data.get("choices", [])
    return [
        {
            "id": f"openai-{index + 1}",
            "label": f"OpenAI {chr(65 + index)}",
            "text": str(choice.get("message", {}).get("content", "")).strip(),
        }
        for index, choice in enumerate(choices)
        if str(choice.get("message", {}).get("content", "")).strip()
    ]


def _anthropic_candidates(prompt: str, references: list[str], model: str, count: int) -> list[dict[str, str]]:
    api_key = os.environ.get("ANTHROPIC_API_KEY")
    if not api_key:
        raise ProviderError("ANTHROPIC_API_KEY is required for provider=anthropic")

    candidates = []
    for index in range(count):
        body = {
            "model": model,
            "max_tokens": 1024,
            "messages": [
                {
                    "role": "user",
                    "content": _provider_prompt(prompt, references, index),
                }
            ],
            "temperature": 0.2,
        }
        data = _post_json(
            "https://api.anthropic.com/v1/messages",
            body,
            headers={
                "x-api-key": api_key,
                "anthropic-version": "2023-06-01",
            },
        )
        text = _anthropic_text(data)
        if text:
            candidates.append(
                {
                    "id": f"anthropic-{index + 1}",
                    "label": f"Anthropic {chr(65 + index)}",
                    "text": text,
                }
            )
    return candidates


def _gemini_candidates(prompt: str, references: list[str], model: str, count: int) -> list[dict[str, str]]:
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        raise ProviderError("GEMINI_API_KEY is required for provider=gemini")

    model_path = urllib.parse.quote(model.removeprefix("models/"), safe="")
    body = {
        "contents": [
            {
                "role": "user",
                "parts": [{"text": _provider_prompt(prompt, references, 0)}],
            }
        ],
        "generationConfig": {
            "candidateCount": count,
            "temperature": 0.2,
        },
    }
    data = _post_json(
        f"https://generativelanguage.googleapis.com/v1beta/models/{model_path}:generateContent",
        body,
        headers={"x-goog-api-key": api_key},
    )
    candidates = []
    for index, candidate in enumerate(data.get("candidates", [])):
        text = _gemini_text(candidate)
        if text:
            candidates.append(
                {
                    "id": f"gemini-{index + 1}",
                    "label": f"Gemini {chr(65 + index)}",
                    "text": text,
                }
            )
    return candidates


def _chat_messages(prompt: str, references: list[str], index: int) -> list[dict[str, str]]:
    return [
        {"role": "system", "content": _provider_instruction(index)},
        {
            "role": "user",
            "content": _reference_prompt(prompt, references),
        },
    ]


def _provider_prompt(prompt: str, references: list[str], index: int) -> str:
    return f"{_provider_instruction(index)}\n\n{_reference_prompt(prompt, references)}"


def _provider_instruction(index: int) -> str:
    instruction = (
        "Answer only from the supplied references. Do not add facts, entities, "
        "numbers, units, or relations that are not supported by the references."
    )
    if index:
        instruction += f" Candidate variant {index + 1}: use concise wording."
    return instruction


def _reference_prompt(prompt: str, references: list[str]) -> str:
    reference_text = "\n".join(f"- {ref}" for ref in references)
    return f"References:\n{reference_text}\n\nPrompt:\n{prompt}"


def _anthropic_text(data: dict[str, Any]) -> str:
    parts = []
    for block in data.get("content", []):
        if isinstance(block, dict) and block.get("type") == "text":
            parts.append(str(block.get("text") or ""))
    return "\n".join(part.strip() for part in parts if part.strip()).strip()


def _gemini_text(candidate: dict[str, Any]) -> str:
    parts = candidate.get("content", {}).get("parts", [])
    text_parts = [str(part.get("text") or "") for part in parts if isinstance(part, dict)]
    return "\n".join(part.strip() for part in text_parts if part.strip()).strip()


def _post_json(url: str, body: dict[str, Any], headers: dict[str, str]) -> dict[str, Any]:
    request = urllib.request.Request(
        url,
        data=json.dumps(body).encode("utf-8"),
        headers={"Content-Type": "application/json", **headers},
        method="POST",
    )
    try:
        with urllib.request.urlopen(request, timeout=45) as response:
            return json.loads(response.read().decode("utf-8"))
    except urllib.error.HTTPError as exc:
        detail = exc.read().decode("utf-8", errors="replace")
        raise ProviderError(f"Provider HTTP {exc.code}: {detail}") from exc
    except urllib.error.URLError as exc:
        raise ProviderError(f"Provider unavailable: {exc.reason}") from exc


def _coerce_references(value: Any) -> list[str]:
    if isinstance(value, str):
        return [part.strip() for part in value.splitlines() if part.strip()]
    if isinstance(value, list):
        return [str(item).strip() for item in value if str(item).strip()]
    return []


def build_generation_payload(payload: dict[str, Any], generated: dict[str, Any]) -> dict[str, Any]:
    """Return a guardrail payload with generated candidates attached."""

    merged = deepcopy(payload)
    merged["candidates"] = generated["candidates"]
    merged["provider_trace"] = {
        key: value
        for key, value in generated.items()
        if key != "candidates"
    }
    merged["provider"] = generated["provider"]
    merged["model"] = generated["model"]
    return merged

