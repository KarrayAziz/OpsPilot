# Evaluation

## Implemented in Phase 0

Phase 0 has engineering validation, not agent evaluation. Deterministic tests cover:

- environment-backed configuration and validation;
- liveness independence from external dependencies;
- successful readiness when all required probes pass;
- HTTP 503 and sanitized output when a probe fails;
- the Qdrant-native readiness request path;
- rejection of an empty readiness probe set.

Ruff and strict mypy are required static-quality gates. Docker Compose configuration and FastAPI
startup are validated separately. This document reports no benchmark numbers because no agent,
retriever, transcription provider, or business ground-truth dataset exists yet.

## Planned evaluation (not implemented)

Future milestone-specific suites are expected to measure:

- workflow classification and final-decision correctness;
- required-evidence recall and RAG Recall@k;
- tool choice, argument correctness, and trajectory efficiency;
- action correctness, approval compliance, and unauthorized sensitive-write rate;
- bounded retry and failure recovery behavior;
- latency, token use, and model cost;
- transcription quality on a small labeled, non-sensitive audio set.

Objective outcomes will use deterministic evaluators and deliberately authored ground truth.
LLM-as-judge will be reserved for genuinely subjective qualities. API-dependent tests will remain
opt-in so deterministic CI cannot fail because an external provider is unavailable.
