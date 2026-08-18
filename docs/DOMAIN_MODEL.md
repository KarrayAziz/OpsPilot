# Domain model

## Implemented in Phase 0

There are no persisted domain entities or database tables. SQLAlchemy currently provides only a
shared declarative metadata root, and Alembic is ready to manage revisions when a later milestone
introduces its first real schema. This avoids empty tables and premature abstractions.

## Planned conceptual model (not implemented)

The synthetic environment is expected to introduce these concepts incrementally:

- **Organization:** a customer account and its stable external identifiers.
- **Contract:** commercial terms, effective dates, structured metadata, and evidence references.
- **Invoice and invoice line:** billed amounts and their deterministic calculation inputs.
- **Support ticket and service incident:** customer reports and service-impact evidence.
- **Workflow run:** explicit durable execution state for one operational request.
- **Approval:** a human decision linked to an exact proposed sensitive action.
- **Audit event:** an append-oriented record of decisions, checks, transitions, and executions.
- **Action/idempotency record:** a durable key and result for mutation deduplication.
- **Audio artifact and transcript:** source-file metadata and derived untrusted evidence with
  provenance.

Relationships, constraints, state machines, monetary representations, and deletion policies will
be specified alongside the milestone that implements them. Ground-truth labels used by evaluation
must not be exposed through runtime-facing entity fields.
