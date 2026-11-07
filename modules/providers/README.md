# Providers Module

## Purpose
Defines standard async provider interfaces (`STTProvider`, `Translator`, `TTSProvider`), latency tracking metrics, retry/timeout wrappers, provider registry, and offline mock implementations for development and testing.

## Interfaces
Exposed via `providers`:
- `STTProvider`: `transcribe_stream(audio_chunks: AsyncIterator[bytes], lang: str) -> AsyncIterator[WSEventEnvelope]`
- `Translator`: `translate(text: str, src: str, tgt: str, glossary: dict[str, str] | None, entities: list[Entity] | None) -> TranslationResult`
- `TTSProvider`: `synthesize_stream(text: str, lang: str, voice: str | None, ssml: bool) -> AsyncIterator[bytes]`
- `ProviderRegistry`: resolves active provider by environment variables (`PROVIDER_STT`, `PROVIDER_TRANSLATE`, `PROVIDER_TTS`).
- `with_timing`, `with_retry`, `with_timeout`: resilience and latency utilities.

## How to Test
Run `pytest modules/providers/tests` from the root of the repository.
