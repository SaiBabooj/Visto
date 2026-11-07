# Voicebridge Architecture

Voicebridge is a voice-first bidirectional translation application between international/non-Tamil travellers and local drivers (autos, cabs) in Chennai.

## Core Modules & Layout

- apps/web: React, Vite, TypeScript, Tailwind mobile-first frontend.
- services/gateway: FastAPI gateway handling WebSocket audio/message streaming and HTTP endpoints.
- packages/contracts: Single source of truth for Pydantic v2 domain schemas, WebSocket envelopes, and generated TypeScript types.
- modules/*: Specialized business domains (translation, speech, confirmation/commitments). Each isolated with README and tests.
- eval/: Evaluation harnesses for transcription quality, translation accuracy, and entity detection.
