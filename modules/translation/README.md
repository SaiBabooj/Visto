# Translation Engine

## Purpose
Implements `Translator` interface using an OpenAI-compatible LLM endpoint (compatible with vLLM, Ollama, Gnani Evon 30B, OpenAI) and an optional lazy-loaded IndicTrans2 provider.

## Key Features
1. **Prompt Rules**:
   - `temperature: 0`
   - Strict instruction: Translate only, add nothing, preserve all numbers and entity names.
   - Output format: JSON `{ "translation": "...", "notes": "..." }`.
   - Injects glossary terms into prompt context.
2. **Entity Validation & Retry**:
   - Compares the numbers and key entities in translated output with the source text.
   - If mismatch occurs, retries once.
   - Flags result with `RiskLevel.COMMITMENT` if entities present, or low confidence note if mismatch persists.
3. **IndicTrans2 Provider**:
   - Optional provider with lazy import; skipped safely if package is missing.
4. **Router**:
   - Reads `config/translate_routes.yaml` and routes language pairs to configured provider.

## How to Test
Run `pytest modules/translation/tests` (fully covered offline with mock HTTP client).
