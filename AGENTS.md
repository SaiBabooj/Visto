# Voicebridge Rules for Engineering & Automated Agents

1. At the start of every session, read docs/PROJECT_GOAL.md and this file.
2. Modules talk only through interfaces in packages/contracts. Never import another module's internals.
3. Every external service (Gnani STT, Gnani TTS, LLM, IndicTrans2) sits behind a provider interface with a mock implementation, selected by env var.
4. No secrets in code or logs.
5. Every module README states purpose, interface, how to test.
6. All user-facing strings go through i18n.
7. Before coding, list files you will create or change and your assumptions. After coding, run make test and make lint, then summarise changes.
8. Never modify modules outside the task's scope.
