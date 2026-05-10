"""Reference-bound guardrail engine for Sentinel Manifold.

The engine is intentionally transparent. It does not claim access to external
truth; it checks candidate outputs against references supplied by the caller.
"""

from __future__ import annotations

import hashlib
import re
import string
import time
from dataclasses import asdict, dataclass, field
from typing import Any, Iterable

from policies import apply_policy_template

UNIT_WORDS = {
    "%",
    "c",
    "celsius",
    "degree",
    "degrees",
    "fahrenheit",
    "g",
    "kg",
    "kelvin",
    "kilometer",
    "kilometers",
    "km",
    "m",
    "meter",
    "meters",
    "metre",
    "metres",
    "mile",
    "miles",
    "minute",
    "minutes",
    "mph",
    "m/s",
    "percent",
    "second",
    "seconds",
    "year",
    "years",
}

STOPWORDS = {
    "a",
    "an",
    "and",
    "are",
    "as",
    "at",
    "be",
    "but",
    "by",
    "called",
    "can",
    "city",
    "commonly",
    "described",
    "does",
    "for",
    "from",
    "has",
    "have",
    "in",
    "into",
    "is",
    "it",
    "its",
    "of",
    "on",
    "or",
    "roughly",
    "the",
    "to",
    "use",
    "uses",
    "with",
    "without",
}

NEGATORS = {"not", "no", "never", "doesnt", "doesn't", "cannot", "cant", "can't"}

OVERCLAIM_PATTERNS = (
    "fully solves",
    "fully solved",
    "guarantees",
    "proves there is no",
    "proves gravity has no connection",
    "final truth",
    "complete and experimentally verified",
    "always correct",
    "never fails",
)

HARD_BLOCK_CODES = {
    "direct_contradiction",
    "known_participant_unsupported_relation",
    "relation_object_mismatch",
    "role_swapped_relation",
    "protected_number_drift",
    "protected_unit_drift",
    "unsupported_overclaim",
    "unsupported_negation",
}


@dataclass(frozen=True)
class Relation:
    subject: str
    predicate: str
    object: str

    def key(self) -> tuple[str, str, str]:
        return (self.subject, self.predicate, self.object)


@dataclass
class ReferenceModel:
    references: list[str]
    relations: list[Relation]
    numbers: set[str]
    units: set[str]
    entities: set[str]
    content_tokens: set[str]
    normalized_members: set[str]
    relation_participants: set[str]


@dataclass
class Finding:
    code: str
    label: str
    severity: int
    message: str
    evidence: str
    fix: str


@dataclass
class CandidateAudit:
    id: str
    label: str
    text: str
    verdict: str
    safe_to_emit: bool
    risk_score: int
    findings: list[Finding] = field(default_factory=list)
    relations: list[Relation] = field(default_factory=list)
    literal_drift: dict[str, list[str]] = field(default_factory=dict)
    metrics: dict[str, float | int] = field(default_factory=dict)
    token_shocks: list[dict[str, float | str]] = field(default_factory=list)


def run_guardrail(payload: dict[str, Any]) -> dict[str, Any]:
    """Run a reference-bound guardrail check over candidate outputs."""

    payload = apply_policy_template(payload)
    references = _coerce_references(payload.get("references", []))
    candidates = _coerce_candidates(payload.get("candidates", []))
    policy = _policy(payload.get("policy", {}))
    mode = str(payload.get("mode") or "strict")

    reference_model = build_reference_model(references)
    audits = [
        evaluate_candidate(candidate, reference_model, policy=policy, mode=mode)
        for candidate in candidates
    ]

    safe = [audit for audit in audits if audit.safe_to_emit]
    emitted = min(safe, key=lambda item: item.risk_score) if safe else None
    action = "EMIT" if emitted else "BLOCK"
    check_id = _check_id(references, candidates)

    result = {
        "check_id": check_id,
        "created_at": int(time.time()),
        "action": action,
        "emitted_candidate_id": emitted.id if emitted else None,
        "emitted_text": emitted.text if emitted else None,
        "summary": _summary(action, emitted, audits, reference_model),
        "mode": mode,
        "policy_profile": payload.get("policy_profile"),
        "policy_name": payload.get("policy_name"),
        "policy": policy,
        "reference_model": {
            "relation_count": len(reference_model.relations),
            "numbers": sorted(reference_model.numbers),
            "units": sorted(reference_model.units),
            "entities": sorted(reference_model.entities),
            "content_token_count": len(reference_model.content_tokens),
            "relations": [asdict(relation) for relation in reference_model.relations],
        },
        "candidates": [_json_audit(audit) for audit in audits],
    }
    return result


def build_reference_model(references: Iterable[str]) -> ReferenceModel:
    refs = [str(ref).strip() for ref in references if str(ref).strip()]
    relation_map: dict[tuple[str, str, str], Relation] = {}
    for ref in refs:
        for relation in extract_relations(ref):
            relation_map[relation.key()] = relation

    joined = "\n".join(refs)
    entities = extract_entities(joined)
    relations = sorted(relation_map.values(), key=lambda r: r.key())
    participants = {part for rel in relations for part in (rel.subject, rel.object)}

    return ReferenceModel(
        references=refs,
        relations=relations,
        numbers=set(extract_numbers(joined)),
        units=set(extract_units(joined)),
        entities=entities,
        content_tokens=set(content_tokens(joined)),
        normalized_members={normalize_text(ref) for ref in refs},
        relation_participants=participants,
    )


def evaluate_candidate(
    candidate: dict[str, str],
    reference_model: ReferenceModel,
    *,
    policy: dict[str, bool] | None = None,
    mode: str = "strict",
) -> CandidateAudit:
    policy = _policy(policy or {})
    text = str(candidate.get("text", "")).strip()
    candidate_id = str(candidate.get("id") or _short_hash(text))
    label = str(candidate.get("label") or candidate_id)
    findings: list[Finding] = []
    relations = extract_relations(text)
    normalized_candidate = normalize_text(text)

    relation_findings: list[Finding] = []
    if policy["relation_clamps"]:
        relation_findings = _relation_findings(relations, reference_model)
        findings.extend(relation_findings)

    candidate_numbers = set(extract_numbers(text))
    candidate_units = set(extract_units(text))
    candidate_entities = extract_entities(text)
    novel_numbers = sorted(candidate_numbers - reference_model.numbers)
    novel_units = sorted(candidate_units - reference_model.units)
    novel_entities = sorted(
        entity for entity in candidate_entities - reference_model.entities if len(entity) > 1
    )

    if policy["literal_guards"]:
        if novel_numbers:
            findings.append(
                Finding(
                    code="protected_number_drift",
                    label="Protected Number Drift",
                    severity=24,
                    message="Candidate introduced number(s) not present in the reference material.",
                    evidence=", ".join(novel_numbers),
                    fix="Use only referenced numbers, or add a supporting source before emission.",
                )
            )
        if novel_units:
            findings.append(
                Finding(
                    code="protected_unit_drift",
                    label="Protected Unit Drift",
                    severity=22,
                    message="Candidate introduced unit(s) not present in the reference material.",
                    evidence=", ".join(novel_units),
                    fix="Keep units aligned with the reference or supply a new verified reference.",
                )
            )
        if novel_entities:
            findings.append(
                Finding(
                    code="novel_entity",
                    label="Novel Entity",
                    severity=12,
                    message="Candidate introduced named entities outside the reference set.",
                    evidence=", ".join(novel_entities[:8]),
                    fix="Check whether the extra entity is supported by the task references.",
                )
            )

    if policy["negation_guards"]:
        negation_finding = _unsupported_negation(text, reference_model)
        if negation_finding:
            findings.append(negation_finding)

    if policy["overclaim_guards"]:
        overclaim_finding = _overclaim(text)
        if overclaim_finding:
            findings.append(overclaim_finding)

    if _direct_self_contradiction(text):
        findings.append(
            Finding(
                code="direct_contradiction",
                label="Direct Contradiction",
                severity=30,
                message="Candidate appears to affirm and deny the same clause.",
                evidence="Detected local is/is-not contradiction pattern.",
                fix="Remove the conflicting clause before this answer can be emitted.",
            )
        )

    exact_reference = normalized_candidate in reference_model.normalized_members
    overlap = jaccard(set(content_tokens(text)), reference_model.content_tokens)
    supported_relations = sum(1 for rel in relations if rel.key() in {r.key() for r in reference_model.relations})
    relation_support = supported_relations / max(1, len(relations))
    risk_score = _risk_score(findings, overlap=overlap, relation_support=relation_support, mode=mode)
    hard_block = any(finding.code in HARD_BLOCK_CODES for finding in findings)
    safe_to_emit = bool(text) and (exact_reference or (risk_score < 42 and not hard_block))
    verdict = _verdict(safe_to_emit, findings, risk_score)

    return CandidateAudit(
        id=candidate_id,
        label=label,
        text=text,
        verdict=verdict,
        safe_to_emit=safe_to_emit,
        risk_score=risk_score,
        findings=findings,
        relations=relations,
        literal_drift={
            "novel_numbers": novel_numbers,
            "novel_units": novel_units,
            "novel_entities": novel_entities,
        },
        metrics={
            "evidence_overlap": round(overlap, 3),
            "relation_support": round(relation_support, 3),
            "supported_relations": supported_relations,
            "extracted_relations": len(relations),
            "finding_count": len(findings),
        },
        token_shocks=token_shock(text, reference_model)[:8],
    )


def extract_relations(text: str) -> list[Relation]:
    """Extract small, auditable relation claims from text."""

    relation_map: dict[tuple[str, str, str], Relation] = {}
    for sentence in split_sentences(text):
        normalized = normalize_text(sentence)
        if not normalized:
            continue

        patterns = [
            (r"(?:the )?capital of ([a-z][a-z ]+?) is ([a-z][a-z ]+)$", "capital", False),
            (r"([a-z][a-z ]+?) is (?:the )?capital (?:city )?of ([a-z][a-z ]+)$", "capital", True),
            (r"([a-z][a-z ]+?) orbits ([a-z][a-z ]+)$", "orbit", False),
            (r"([a-z][a-z ]+?) contains ([a-z][a-z ]+)$", "contain", False),
            (r"([a-z][a-z ]+?) requires ([a-z][a-z ]+)$", "require", False),
            (r"([a-z][a-z ]+?) uses ([a-z][a-z ]+)$", "use", False),
            (r"([a-z][a-z ]+?) releases ([a-z][a-z ]+)$", "release", False),
            (r"([a-z][a-z ]+?) produces ([a-z][a-z ]+)$", "produce", False),
            (r"([a-z][a-z ]+?) stores ([a-z][a-z ]+)$", "store", False),
            (r"([a-z][a-z ]+?) converts ([a-z][a-z ]+?) into ([a-z][a-z ]+)$", "convert_to", False),
        ]

        for pattern, predicate, reverse in patterns:
            match = re.search(pattern, normalized)
            if not match:
                continue
            if predicate == "convert_to" and len(match.groups()) == 3:
                relation = Relation(_clean_span(match.group(1)), predicate, _clean_span(match.group(3)))
            elif reverse:
                relation = Relation(_clean_span(match.group(2)), predicate, _clean_span(match.group(1)))
            else:
                relation = Relation(_clean_span(match.group(1)), predicate, _clean_span(match.group(2)))
            if relation.subject and relation.object:
                relation_map[relation.key()] = relation

        copular = re.search(r"([a-z][a-z ]+?) is (?:a |an |the )?([a-z][a-z ]+)$", normalized)
        if copular:
            subject = _clean_span(copular.group(1))
            obj = _clean_span(copular.group(2))
            if subject and obj and subject != obj and obj not in {"capital city of france", "capital city"}:
                relation_map[(subject, "is_a", obj)] = Relation(subject, "is_a", obj)

    return sorted(relation_map.values(), key=lambda r: r.key())


def split_sentences(text: str) -> list[str]:
    return [part.strip() for part in re.split(r"(?<=[.!?])\s+|\n+", text) if part.strip()]


def normalize_text(text: str) -> str:
    lowered = text.lower().replace("’", "'").replace("“", '"').replace("”", '"')
    punctuation = string.punctuation.replace("%", "").replace("/", "")
    return " ".join(lowered.translate(str.maketrans("", "", punctuation)).split())


def extract_numbers(text: str) -> list[str]:
    return re.findall(r"\b\d+(?:\.\d+)?\b", text)


def extract_units(text: str) -> list[str]:
    tokens = re.findall(r"%|[a-zA-Z/]+", text.lower())
    return sorted({token for token in tokens if token in UNIT_WORDS})


def extract_entities(text: str) -> set[str]:
    entities = set()
    for match in re.finditer(r"\b[A-Z][a-zA-Z]+(?:\s+[A-Z][a-zA-Z]+)*\b", text):
        value = match.group(0).strip()
        if value.lower() not in STOPWORDS:
            entities.add(normalize_text(value))
    return entities


def content_tokens(text: str) -> list[str]:
    return [
        token
        for token in re.findall(r"[a-zA-Z][a-zA-Z0-9_/-]*", text.lower())
        if len(token) > 2 and token not in STOPWORDS and token not in NEGATORS
    ]


def jaccard(left: set[str], right: set[str]) -> float:
    if not left and not right:
        return 1.0
    if not left or not right:
        return 0.0
    return len(left & right) / len(left | right)


def token_shock(text: str, reference_model: ReferenceModel) -> list[dict[str, float | str]]:
    """Cheap token-level drift localization without embeddings."""

    ref_tokens = reference_model.content_tokens
    shocks = []
    for token in content_tokens(text):
        clean = normalize_text(token)
        if not clean:
            continue
        if clean in ref_tokens:
            score = 0.05
        elif clean in reference_model.relation_participants or clean in reference_model.entities:
            score = 0.28
        else:
            score = 0.62
        shocks.append({"token": token, "score": score})
    return sorted(shocks, key=lambda item: float(item["score"]), reverse=True)


def _relation_findings(candidate_relations: list[Relation], reference_model: ReferenceModel) -> list[Finding]:
    findings: list[Finding] = []
    ref_keys = {relation.key() for relation in reference_model.relations}
    by_subject_predicate: dict[tuple[str, str], set[str]] = {}
    participants = reference_model.relation_participants

    for relation in reference_model.relations:
        by_subject_predicate.setdefault((relation.subject, relation.predicate), set()).add(relation.object)

    for relation in candidate_relations:
        if relation.key() in ref_keys:
            continue

        reversed_key = (relation.object, relation.predicate, relation.subject)
        if reversed_key in ref_keys:
            findings.append(
                Finding(
                    code="role_swapped_relation",
                    label="Role-Swapped Relation",
                    severity=34,
                    message="Candidate reverses a protected subject/object relation.",
                    evidence=f"{relation.subject} {relation.predicate} {relation.object}",
                    fix="Restore the subject/object direction from the reference material.",
                )
            )
            continue

        supported_objects = by_subject_predicate.get((relation.subject, relation.predicate))
        if supported_objects and relation.object not in supported_objects:
            findings.append(
                Finding(
                    code="relation_object_mismatch",
                    label="Relation Object Mismatch",
                    severity=32,
                    message="Candidate keeps the protected relation but changes its object.",
                    evidence=f"{relation.subject} {relation.predicate} {relation.object}; expected one of {', '.join(sorted(supported_objects))}",
                    fix="Use the referenced object for this relation.",
                )
            )
            continue

        if relation.subject in participants or relation.object in participants:
            findings.append(
                Finding(
                    code="known_participant_unsupported_relation",
                    label="Unsupported Relation",
                    severity=26,
                    message="Candidate links known reference participants through an unsupported relation.",
                    evidence=f"{relation.subject} {relation.predicate} {relation.object}",
                    fix="Add a source for the relation or remove it from the answer.",
                )
            )

    return findings


def _unsupported_negation(text: str, reference_model: ReferenceModel) -> Finding | None:
    candidate_tokens = set(content_tokens(text))
    raw_tokens = set(re.findall(r"[a-zA-Z']+", text.lower()))
    if not raw_tokens & NEGATORS:
        return None

    best_overlap = 0.0
    best_ref = ""
    for ref in reference_model.references:
        overlap = jaccard(candidate_tokens, set(content_tokens(ref)))
        if overlap > best_overlap:
            best_overlap = overlap
            best_ref = ref

    if best_overlap >= 0.45:
        return Finding(
            code="unsupported_negation",
            label="Unsupported Negation",
            severity=30,
            message="Candidate negates content that is positively supported by the references.",
            evidence=best_ref,
            fix="Remove the negation or provide a reference that supports it.",
        )
    return None


def _overclaim(text: str) -> Finding | None:
    normalized = normalize_text(text)
    for pattern in OVERCLAIM_PATTERNS:
        if pattern in normalized:
            return Finding(
                code="unsupported_overclaim",
                label="Unsupported Overclaim",
                severity=16,
                message="Candidate uses absolute or stronger-than-supported wording.",
                evidence=pattern,
                fix="Rewrite as a scoped claim tied to the supplied reference material.",
            )
    return None


def _direct_self_contradiction(text: str) -> bool:
    normalized = normalize_text(text)
    for match in re.finditer(r"\b([a-z][a-z ]+?) is not ([a-z][a-z ]+?)(?:$| and | but )", normalized):
        positive = f"{_clean_span(match.group(1))} is {_clean_span(match.group(2))}"
        if positive in normalized:
            return True
    return False


def _risk_score(
    findings: list[Finding],
    *,
    overlap: float,
    relation_support: float,
    mode: str,
) -> int:
    base = sum(finding.severity for finding in findings)
    evidence_penalty = int(max(0.0, 1.0 - overlap) * 12)
    relation_penalty = int(max(0.0, 1.0 - relation_support) * 8)
    strict_bonus = 6 if mode == "strict" and findings else 0
    return max(0, min(100, base + evidence_penalty + relation_penalty + strict_bonus))


def _verdict(safe_to_emit: bool, findings: list[Finding], risk_score: int) -> str:
    if safe_to_emit:
        return "EMIT"
    codes = {finding.code for finding in findings}
    if codes & {
        "direct_contradiction",
        "protected_number_drift",
        "protected_unit_drift",
        "relation_object_mismatch",
        "role_swapped_relation",
        "unsupported_negation",
    }:
        return "CONTRADICTION"
    if risk_score >= 58:
        return "BLOCK"
    return "DRIFT"


def _summary(
    action: str,
    emitted: CandidateAudit | None,
    audits: list[CandidateAudit],
    reference_model: ReferenceModel,
) -> dict[str, Any]:
    blocked = sum(1 for audit in audits if not audit.safe_to_emit)
    riskiest = max(audits, key=lambda audit: audit.risk_score, default=None)
    return {
        "headline": (
            f"{emitted.label} emitted with risk {emitted.risk_score}."
            if emitted
            else "Every candidate was blocked by reference-bound guardrails."
        ),
        "action": action,
        "candidate_count": len(audits),
        "blocked_count": blocked,
        "reference_relations": len(reference_model.relations),
        "highest_risk_candidate": riskiest.label if riskiest else None,
        "highest_risk_score": riskiest.risk_score if riskiest else None,
    }


def _json_audit(audit: CandidateAudit) -> dict[str, Any]:
    data = asdict(audit)
    data["findings"] = [asdict(finding) for finding in audit.findings]
    data["relations"] = [asdict(relation) for relation in audit.relations]
    return data


def _coerce_references(value: Any) -> list[str]:
    if isinstance(value, str):
        return [part.strip() for part in split_sentences(value) if part.strip()]
    if isinstance(value, list):
        return [str(item).strip() for item in value if str(item).strip()]
    return []


def _coerce_candidates(value: Any) -> list[dict[str, str]]:
    if isinstance(value, str):
        return [{"id": "candidate-a", "label": "Candidate A", "text": value}]
    if not isinstance(value, list):
        return []
    candidates = []
    for index, item in enumerate(value):
        if isinstance(item, dict):
            text = str(item.get("text", "")).strip()
            if text:
                candidates.append(
                    {
                        "id": str(item.get("id") or f"candidate-{index + 1}"),
                        "label": str(item.get("label") or f"Candidate {index + 1}"),
                        "text": text,
                    }
                )
        elif str(item).strip():
            candidates.append(
                {
                    "id": f"candidate-{index + 1}",
                    "label": f"Candidate {index + 1}",
                    "text": str(item).strip(),
                }
            )
    return candidates


def _policy(value: dict[str, Any]) -> dict[str, bool]:
    return {
        "relation_clamps": bool(value.get("relation_clamps", True)),
        "literal_guards": bool(value.get("literal_guards", True)),
        "negation_guards": bool(value.get("negation_guards", True)),
        "overclaim_guards": bool(value.get("overclaim_guards", True)),
    }


def _clean_span(value: str) -> str:
    cleaned = normalize_text(value)
    parts = [part for part in cleaned.split() if part not in {"the", "a", "an"}]
    while parts and parts[-1] in {"and", "but", "of", "in", "at", "with", "to"}:
        parts.pop()
    return " ".join(parts)


def _short_hash(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()[:10]


def _check_id(references: list[str], candidates: list[dict[str, str]]) -> str:
    material = "\n".join(references + [candidate["text"] for candidate in candidates])
    return f"sm-{_short_hash(material)}"
