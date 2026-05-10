"""Policy templates for common Sentinel Manifold deployments."""

from __future__ import annotations

from copy import deepcopy
from typing import Any


POLICY_TEMPLATES: dict[str, dict[str, Any]] = {
    "support": {
        "id": "support",
        "name": "Customer Support",
        "mode": "strict",
        "description": "Blocks policy drift, changed prices/dates, and unsafe customer-facing claims.",
        "policy": {
            "relation_clamps": True,
            "literal_guards": True,
            "negation_guards": True,
            "overclaim_guards": True,
        },
    },
    "regulated": {
        "id": "regulated",
        "name": "Regulated Workflow",
        "mode": "strict",
        "description": "Highest-friction profile for finance, healthcare, insurance, and legal review.",
        "policy": {
            "relation_clamps": True,
            "literal_guards": True,
            "negation_guards": True,
            "overclaim_guards": True,
        },
    },
    "research": {
        "id": "research",
        "name": "Research Claims",
        "mode": "strict",
        "description": "Emphasizes overclaim, contradiction, unit, and relation drift in technical text.",
        "policy": {
            "relation_clamps": True,
            "literal_guards": True,
            "negation_guards": True,
            "overclaim_guards": True,
        },
    },
    "code_review": {
        "id": "code_review",
        "name": "Code Review",
        "mode": "balanced",
        "description": "Keeps relation and literal checks active while allowing more exploratory wording.",
        "policy": {
            "relation_clamps": True,
            "literal_guards": True,
            "negation_guards": True,
            "overclaim_guards": False,
        },
    },
}


DEFAULT_POLICY_ID = "support"


def list_policy_templates() -> list[dict[str, Any]]:
    """Return policy templates safe for API exposure."""

    return [deepcopy(template) for template in POLICY_TEMPLATES.values()]


def get_policy_template(policy_id: str | None) -> dict[str, Any]:
    """Return one policy template, falling back to the support default."""

    key = policy_id or DEFAULT_POLICY_ID
    return deepcopy(POLICY_TEMPLATES.get(key, POLICY_TEMPLATES[DEFAULT_POLICY_ID]))


def apply_policy_template(payload: dict[str, Any]) -> dict[str, Any]:
    """Merge a named template into a caller payload without mutating the caller."""

    merged = deepcopy(payload)
    template = get_policy_template(str(merged.get("policy_profile") or DEFAULT_POLICY_ID))
    explicit_policy = merged.get("policy") if isinstance(merged.get("policy"), dict) else {}

    template_policy = template["policy"]
    merged["policy"] = {**template_policy, **explicit_policy}
    merged["mode"] = str(merged.get("mode") or template["mode"])
    merged["policy_profile"] = template["id"]
    merged["policy_name"] = template["name"]
    return merged

