# Gnani TTS Adapter (Timbre)

## Purpose
Implements `TTSProvider` for streaming speech synthesis using Gnani Timbre APIs (v2.5 and v3.0).

## Documentation & Endpoints Found
From official Gnani documentation (https://docs.gnani.ai/api/TTS/tts-sse.md & available-voices.md):
- **Streaming Endpoint**: `POST https://api.vachana.ai/api/v1/tts/sse`
- **Authentication**: `X-API-Key-ID` header.
- **Model**: `timbre-v3.0` (all 13 voices support all 10 Indian languages) or `timbre-v2.5`.
- **Default Voices Config**: `config/tts_voices.yaml` (e.g. `ta: Shivani`, `en: Kaveri`, `hi: Nalini`).
- **Streaming Payload**: Audio chunks streamed via Server-Sent Events / chunked transfer.
- **SSML / Audio Tags**: Timbre v3.0 supports audio tags `<whispers>`, `<laugh>`, `<pauses>` inline in text.
- **Fallback**: Text-only fallback when language or voice is unavailable or service fails.

## How to Test
- Offline: `pytest modules/tts_gnani/tests -m "not live"`
- Live: `GNANI_API_KEY=key pytest modules/tts_gnani/tests -m live`
