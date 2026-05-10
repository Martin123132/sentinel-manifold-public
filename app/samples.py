"""Seed data used by the local demo dashboard."""

DEMO_PAYLOAD = {
    "policy_profile": "support",
    "provider": "local_demo",
    "model": "sentinel-demo-v1",
    "prompt": "Answer the customer using only the supplied reference facts.",
    "mode": "strict",
    "policy": {
        "relation_clamps": True,
        "literal_guards": True,
        "negation_guards": True,
        "overclaim_guards": True,
    },
    "references": [
        "Earth orbits the Sun.",
        "The Sun is a star.",
        "Water boils at 100 degrees Celsius at sea level.",
        "The capital of France is Paris.",
        "General relativity describes gravity as the curvature of spacetime caused by mass and energy.",
    ],
    "candidates": [
        {
            "id": "candidate-a",
            "label": "Candidate A",
            "text": "Earth orbits the Sun. The Sun is a star. Water boils at 100 degrees Celsius at sea level.",
        },
        {
            "id": "candidate-b",
            "label": "Candidate B",
            "text": "The Sun orbits Earth. Water boils at 90 degrees Celsius at sea level. The capital of France is London.",
        },
        {
            "id": "candidate-c",
            "label": "Candidate C",
            "text": "General relativity fully solves gravity and proves there is no connection between gravity, mass, and energy.",
        },
    ],
}


DEMO_SUITE = {
    "name": "Mixed buyer release gate",
    "description": "Regression checks across support, regulated workflow, research claims, and generated demo candidates.",
    "policy_profile": "support",
    "provider": "local_demo",
    "model": "sentinel-demo-v1",
    "cases": [
        {
            "id": "support-safe-answer",
            "name": "Emit the supported answer",
            "references": [
                "The capital of France is Paris.",
                "Customer refunds are processed within 5 business days.",
            ],
            "candidates": [
                {
                    "id": "safe",
                    "label": "Safe",
                    "text": "The capital of France is Paris. Customer refunds are processed within 5 business days.",
                },
                {
                    "id": "drift",
                    "label": "Drift",
                    "text": "The capital of France is London. Customer refunds are processed within 2 business days.",
                },
            ],
            "expect": {
                "action": "EMIT",
                "emitted_candidate_id": "safe",
                "blocked_count": 1,
            },
        },
        {
            "id": "support-block-drift",
            "name": "Block unsafe drift",
            "references": [
                "Earth orbits the Sun.",
                "Water boils at 100 degrees Celsius at sea level.",
            ],
            "candidates": [
                {
                    "id": "wrong-relation",
                    "label": "Wrong relation",
                    "text": "The Sun orbits Earth.",
                },
                {
                    "id": "wrong-literal",
                    "label": "Wrong literal",
                    "text": "Water boils at 90 degrees Celsius at sea level.",
                },
            ],
            "expect": {
                "action": "BLOCK",
                "min_blocked_count": 2,
            },
        },
        {
            "id": "regulated-threshold-negation",
            "name": "Regulated threshold and negation drift",
            "policy_profile": "regulated",
            "references": [
                "Policy withdrawals over 10000 GBP require enhanced review.",
                "The customer is eligible for manual review within 3 business days.",
            ],
            "candidates": [
                {
                    "id": "safe",
                    "label": "Safe",
                    "text": "Policy withdrawals over 10000 GBP require enhanced review. The customer is eligible for manual review within 3 business days.",
                },
                {
                    "id": "unsafe",
                    "label": "Unsafe",
                    "text": "Policy withdrawals over 50000 GBP do not require enhanced review. The customer is eligible for instant approval.",
                },
            ],
            "expect": {
                "action": "EMIT",
                "emitted_candidate_id": "safe",
                "blocked_count": 1,
            },
        },
        {
            "id": "research-overclaim",
            "name": "Research overclaim blocks",
            "policy_profile": "research",
            "references": [
                "The study observed reduced error rates in 42 test runs.",
                "The study reports preliminary results.",
            ],
            "candidates": [
                {
                    "id": "unsafe",
                    "label": "Unsafe",
                    "text": "The study guarantees reduced error rates in every deployment and is always correct.",
                },
            ],
            "expect": {
                "action": "BLOCK",
                "min_blocked_count": 1,
            },
        },
        {
            "id": "generated-provider-path",
            "name": "Generated candidates still guard",
            "prompt": "Answer using only the supplied reference facts.",
            "references": [
                "The Sun is a star.",
                "Earth orbits the Sun.",
            ],
            "candidate_count": 3,
            "expect": {
                "action": "EMIT",
                "candidate_count": 3,
            },
        },
    ],
}
