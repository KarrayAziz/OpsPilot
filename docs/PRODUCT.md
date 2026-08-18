# Product

## Implemented in Phase 0

OpsPilot currently provides only an executable service foundation: validated configuration,
PostgreSQL and Qdrant development infrastructure, database migration plumbing, liveness, and
real dependency readiness checks. It accepts no operational requests and performs no business
actions.

## Planned product behavior

The planned product operates in a deterministic synthetic B2B SaaS company. An employee will
submit a text request or, in a later phase, a recorded voice note. OpsPilot will resolve the
relevant entities, collect structured and unstructured evidence, plan an investigation, explain
its findings, and propose an appropriate action. Deterministic software—not a model—will enforce
authorization, risk rules, approvals, idempotency, execution, and audit persistence.

The initial planned workflows are:

1. billing-dispute investigation;
2. support and SLA escalation;
3. account and contract change requests.

The first planned vertical slice is billing disputes, but it is not part of Phase 0.

## Product boundaries

The synthetic company is intentional. It enables fixed ground truth, repeatable failure cases,
and measurable end-to-end behavior while capability interfaces remain replaceable by real CRM,
billing, support, and knowledge-system adapters later.

OpsPilot is not intended to be a general chatbot. Realtime voice interaction, text-to-speech,
unrestricted SQL or shell tools, a multi-agent hierarchy, and a user interface are outside the
current scope.
