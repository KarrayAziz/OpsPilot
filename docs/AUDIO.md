# Audio

## Implemented in Phase 0

Audio upload, storage, validation, transcription, and retrieval are not implemented. The project
has no OpenAI SDK dependency and makes no speech-to-text calls.

## Planned capability (not implemented)

Audio will be an input and evidence channel inside the same operational workflow, not a separate
agent. Planned examples include employee voice-note requests, customer voicemails, and support
call recordings.

A later milestone will define a replaceable `TranscriptionProvider` boundary and an OpenAI
`whisper-1` recorded-file implementation as the initial baseline. Provider-specific code must not
leak into the workflow graph so alternative transcription models can be benchmarked later.

Persisted provenance is expected to include the source artifact reference, checksum, provider and
model, transcript, timestamps, and language or duration when available. File constraints and
checksums will be enforced deterministically. Transcripts are untrusted evidence: their content
cannot bypass normal permissions, risk classification, approval, or execution controls.

Realtime voice-agent behavior and text-to-speech are explicitly outside the planned V1 scope.
External transcription tests will be opt-in and use no private real-world audio.
