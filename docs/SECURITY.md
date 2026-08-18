# Security

## Implemented in Phase 0

- Runtime configuration is loaded from environment variables and validated before use.
- The database URL is represented as a Pydantic secret to reduce accidental display.
- `.env` is ignored; `.env.example` contains local development values only.
- Readiness responses expose dependency state but sanitize connection exceptions. Detailed
  failures are logged server-side rather than returned to callers.
- The API exposes only liveness, readiness, and FastAPI's development documentation routes. It has
  no business read or mutation capability.

The Compose credentials are intentionally public local defaults. They must not be used in a
shared or production environment. Authentication, TLS termination, network policy, deployment
hardening, and secret-manager integration are not implemented.

## Planned controls (not implemented)

Deterministic Python will own permissions, risk classification, approval requirements, input
validation, retry ceilings, idempotency, mutation execution, workflow lifecycle, and audit logs.
Reasoning components will never receive unrestricted SQL, shell, filesystem, arbitrary HTTP, or
generic write tools.

Contracts, policies, tickets, support notes, and transcripts will be treated as untrusted data.
Their content cannot override system policy or directly trigger a sensitive action. Sensitive
writes will require an approved proposal whose identity and arguments exactly match the action
executed.

Security claims will be backed by adversarial and failure-injection tests when those surfaces are
implemented; none are claimed for Phase 0.
