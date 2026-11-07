# Voicebridge Rules for Engineering & Automated Agents

1. Modules talk only through interfaces in packages/contracts. Never import another module's internals.
2. Every external service (Gnani STT, Gnani TTS, LLM, IndicTrans2) sits behind a provider interface with a mock implementation, selected by env var.
3. No secrets in code or logs.
4. Every module README states purpose, interface, how to test.
5. All user-facing strings go through i18n.
6. Before coding, list files you will create or change and your assumptions. After coding, run make test and make lint, then summarise changes.
7. Never modify modules outside the task's scope.
