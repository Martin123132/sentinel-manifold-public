"""OpenAI-compatible chat completion surface for Sentinel Manifold."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from evidence import save_evidence_pack, sha256_json
from guardrail import run_guardrail
from policies import DEFAULT_POLICY_ID, apply_policy_template
from providers import DEFAULT_PROVIDER, build_generation_payload, generate_candidates


def run_chat_completions(payload: dict[str, Any], evidence_dir: Path) -> dict[str, Any]:
    """Run an OpenAI-shaped chat completion request through Sentinel."""

    result = _run_sentinel_chat(payload, evidence_dir)
    return _openai_response(payload, result)


def run_chat_completions_stream(payload: dict[str, Any], evidence_dir: Path) -> list[str]:
    """Return OpenAI-compatible Server-Sent Event chunks for a guarded response."""

    result = _run_sentinel_chat(payload, evidence_dir)
    response = _openai_response(payload, result)
    return [_sse_event(chunk) for chunk in _openai_stream_chunks(response)] + ["data: [DONE]\n\n"]


def _run_sentinel_chat(payload: dict[str, Any], evidence_dir: Path) -> dict[str, Any]:
    sentinel = payload.get("sentinel") if isinstance(payload.get("sentinel"), dict) else {}
    provider_payload = _provider_payload(payload, sentinel)
    generated = generate_candidates(provider_payload)
    guardrail_payload = build_generation_payload(provider_payload, generated)
    guardrail_payload = apply_policy_template(guardrail_payload)
    result = run_guardrail(guardrail_payload)
    result["provider_trace"] = guardrail_payload.get("provider_trace")
    result["provider"] = guardrail_payload.get("provider")
    result["model"] = guardrail_payload.get("model")
    result["compat_request"] = _compat_request_metadata(payload)
    evidence = save_evidence_pack(guardrail_payload | {"compat_request": result["compat_request"]}, result, evidence_dir)
    result["evidence"] = evidence
    return result


def _provider_payload(payload: dict[str, Any], sentinel: dict[str, Any]) -> dict[str, Any]:
    provider = sentinel.get("provider") or payload.get("provider") or DEFAULT_PROVIDER
    model = sentinel.get("provider_model") or payload.get("provider_model") or payload.get("model")
    prompt = sentinel.get("prompt") or _last_user_message(payload.get("messages", []))
    references = sentinel.get("references") or payload.get("references") or _references_from_messages(payload.get("messages", []))
    candidate_count = sentinel.get("candidate_count") or payload.get("n") or 3

    return {
        "provider": provider,
        "model": model,
        "prompt": prompt,
        "references": references,
        "candidate_count": candidate_count,
        "policy_profile": sentinel.get("policy_profile") or payload.get("policy_profile") or DEFAULT_POLICY_ID,
        "policy": sentinel.get("policy") or payload.get("policy") or {},
        "mode": sentinel.get("mode") or payload.get("mode"),
    }


def _openai_response(payload: dict[str, Any], result: dict[str, Any]) -> dict[str, Any]:
    emitted_text = result.get("emitted_text") or ""
    action = result.get("action")
    finish_reason = "stop" if action == "EMIT" else "content_filter"
    model = str(payload.get("model") or "sentinel-manifold")
    response_id = f"chatcmpl-{result['check_id']}"
    usage = _usage(payload, emitted_text)

    return {
        "id": response_id,
        "object": "chat.completion",
        "created": result["created_at"],
        "model": model,
        "choices": [
            {
                "index": 0,
                "message": {
                    "role": "assistant",
                    "content": emitted_text,
                },
                "finish_reason": finish_reason,
            }
        ],
        "usage": usage,
        "sentinel": {
            "check_id": result["check_id"],
            "action": action,
            "emitted_candidate_id": result.get("emitted_candidate_id"),
            "blocked_count": result.get("summary", {}).get("blocked_count"),
            "highest_risk_score": result.get("summary", {}).get("highest_risk_score"),
            "provider": result.get("provider"),
            "provider_model": result.get("model"),
            "evidence": result.get("evidence"),
            "candidates": [
                {
                    "id": candidate.get("id"),
                    "label": candidate.get("label"),
                    "verdict": candidate.get("verdict"),
                    "risk_score": candidate.get("risk_score"),
                    "safe_to_emit": candidate.get("safe_to_emit"),
                }
                for candidate in result.get("candidates", [])
            ],
        },
    }


def _openai_stream_chunks(response: dict[str, Any]) -> list[dict[str, Any]]:
    base = {
        "id": response["id"],
        "object": "chat.completion.chunk",
        "created": response["created"],
        "model": response["model"],
    }
    chunks = [
        base
        | {
            "choices": [
                {
                    "index": 0,
                    "delta": {"role": "assistant"},
                    "finish_reason": None,
                }
            ],
        }
    ]
    content = response.get("choices", [{}])[0].get("message", {}).get("content", "")
    for piece in _stream_pieces(content):
        chunks.append(
            base
            | {
                "choices": [
                    {
                        "index": 0,
                        "delta": {"content": piece},
                        "finish_reason": None,
                    }
                ],
            }
        )
    chunks.append(
        base
        | {
            "choices": [
                {
                    "index": 0,
                    "delta": {},
                    "finish_reason": response.get("choices", [{}])[0].get("finish_reason"),
                }
            ],
            "sentinel": response.get("sentinel", {}),
            "usage": response.get("usage", {}),
        }
    )
    return chunks


def _stream_pieces(text: str, max_words: int = 8) -> list[str]:
    words = text.split(" ")
    if not text or not words:
        return []
    pieces: list[str] = []
    for index in range(0, len(words), max_words):
        piece = " ".join(words[index : index + max_words])
        if index + max_words < len(words):
            piece += " "
        pieces.append(piece)
    return pieces


def _sse_event(payload: dict[str, Any]) -> str:
    return f"data: {json.dumps(payload, separators=(',', ':'), ensure_ascii=False)}\n\n"


def _last_user_message(messages: Any) -> str:
    if not isinstance(messages, list):
        return ""
    for message in reversed(messages):
        if isinstance(message, dict) and message.get("role") == "user":
            return _message_content(message)
    return ""


def _references_from_messages(messages: Any) -> list[str]:
    if not isinstance(messages, list):
        return []
    references: list[str] = []
    for message in messages:
        if not isinstance(message, dict):
            continue
        content = _message_content(message)
        if "References:" in content:
            content = content.split("References:", 1)[1]
        elif message.get("role") not in {"system", "developer"}:
            continue
        for line in content.splitlines():
            cleaned = line.strip().lstrip("-*• ").strip()
            if cleaned and not cleaned.lower().startswith(("prompt:", "task:", "answer ")):
                references.append(cleaned)
    return references


def _message_content(message: dict[str, Any]) -> str:
    content = message.get("content")
    if isinstance(content, str):
        return content
    if isinstance(content, list):
        parts = []
        for item in content:
            if isinstance(item, dict) and item.get("type") == "text":
                parts.append(str(item.get("text") or ""))
        return "\n".join(parts)
    return ""


def _usage(payload: dict[str, Any], emitted_text: str) -> dict[str, int]:
    prompt_material = json.dumps(payload.get("messages", []), ensure_ascii=False)
    prompt_tokens = _rough_tokens(prompt_material)
    completion_tokens = _rough_tokens(emitted_text)
    return {
        "prompt_tokens": prompt_tokens,
        "completion_tokens": completion_tokens,
        "total_tokens": prompt_tokens + completion_tokens,
    }


def _rough_tokens(text: str) -> int:
    if not text:
        return 0
    return max(1, len(text.split()))


def _compat_request_metadata(payload: dict[str, Any]) -> dict[str, Any]:
    return {
        "endpoint": "/v1/chat/completions",
        "model": payload.get("model"),
        "stream": payload.get("stream", False),
        "request_sha256": sha256_json(
            {
                "model": payload.get("model"),
                "stream": payload.get("stream", False),
                "messages": payload.get("messages", []),
                "sentinel": payload.get("sentinel", {}),
            }
        ),
    }

