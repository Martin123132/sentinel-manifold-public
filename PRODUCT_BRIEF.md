# Product Brief: Sentinel Manifold

## One-Liner

Sentinel Manifold is an AI output firewall that blocks hallucinated, contradictory, or unsupported LLM answers before they reach users.

## Why This Has The Best Chance Of Getting Attention

The demo is instantly understandable: paste reference truth, paste multiple AI outputs, click Run Check, and watch the product choose the supported answer or block the unsafe pool. It turns abstract AI safety into a visible gateway decision.

This product sits in a hot buying category:

- AI governance
- AI observability
- RAG reliability
- regulated AI deployment
- enterprise audit trails

## Target Buyers

- AI platform teams
- compliance and risk leads
- legaltech and fintech founders
- customer-support automation teams
- healthcare and research AI teams
- dev-tool companies shipping agentic workflows

## MVP Promise

Given:

- reference material
- several candidate model outputs
- a policy profile

Sentinel Manifold returns:

- `EMIT` or `BLOCK`
- selected candidate, when safe
- per-candidate risk score
- relation-drift findings
- contradiction and negation findings
- protected entity/number/unit drift
- exportable audit JSON
- signed evidence packs for later review
- policy profiles for different deployment contexts
- CLI/API use outside the dashboard

## Positioning

Not "AI that knows truth."

Better:

> Regulates AI outputs against the truth sources your team supplied.

That is easier to prove, easier to demo, and easier to sell.

## Build Philosophy

The product should feel like infrastructure, not a toy:

- crisp audit trail
- deterministic explanations
- policy toggles
- exportable evidence
- no hidden classifier claims
- no unverifiable magic language

## Stage 2 Commercial Story

The product now has the pieces a buyer expects from a gateway rather than a demo:

- Policy profiles: support, regulated workflow, research claims, and code review.
- Audit persistence: each check writes a replayable evidence pack with canonical SHA-256 integrity metadata.
- API and CLI paths: teams can run the same guardrail from a browser, local script, CI job, or future model proxy.
- Provider adapters: a local demo generator, optional Ollama, and optional OpenAI can now feed the guardrail path.
- OpenAI-compatible gateway: apps can point at Sentinel through `/v1/chat/completions` and receive a normal chat-completion shaped response plus Sentinel audit metadata.

This creates a stronger sales hook:

> Block bad AI answers, then prove exactly why they were blocked.

## Stage 3 Commercial Story

Sentinel now demonstrates the actual gateway motion:

1. An app submits references and a prompt.
2. A provider adapter generates candidate outputs.
3. Sentinel regulates the candidates before emission.
4. The evidence pack records the prompt, provider, model, candidates, verdict, and integrity digest.

That makes the product easier to position as infrastructure instead of a standalone checker.

## Stage 4 Commercial Story

Sentinel can now sit in the path where model traffic already flows. The `/v1/chat/completions` surface gives prospects a clear integration story:

> Keep your app's chat-completions shape, but add pre-emission guardrails and evidence packs.

## Stage 5 Commercial Story

Sentinel can now prove that saved audit artifacts are intact after the fact. The CLI and API verification report checks the evidence-pack digest plus the request-level reference, candidate, and policy hashes.

That makes the compliance story sharper:

> Block bad AI answers, preserve the audit record, then independently verify that record later.

## Stage 6 Commercial Story

Sentinel can now run guardrail regression suites as a release gate. Teams can define expected gateway outcomes across many prompts, references, candidates, providers, and policies, then fail CI when a model or prompt change starts emitting unsupported answers.

That gives platform teams a stronger buying reason:

> Treat AI safety like tests: run the suite before every release, keep evidence for every case, and know exactly which behavior regressed.

## Stage 7 Commercial Story

Sentinel can now package AI safety checks as CI release artifacts. Every guarded release can produce a suite report plus tamper-evident evidence packs, giving teams a practical compliance bundle without adding a database or external storage.

That sharpens the enterprise hook:

> Fail releases when AI behavior regresses, and keep the evidence package auditors will ask for.

## Stage 8 Commercial Story

Sentinel can now be launched publicly without giving away the whole business.
The software is source-available for personal, community, evaluation, nonprofit,
research, and small-business use; larger commercial use requires a separate
license. The product identity is protected, and hosted public demos run as a
bounded sandbox instead of an admin console.

That gives the project a cleaner attention loop:

> Let people try and learn from the AI safety gateway, while making large
> commercial platforms ask, pay fairly, and leave room for community benefit.
