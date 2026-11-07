# Gnani STT Adapter (Prisma)

## Purpose
Implements `STTProvider` using Gnani Prisma WebSocket streaming API.

## Documentation & Endpoints Found
From official Gnani documentation (https://docs.gnani.ai/api/STT/stt-websocket.md):
- **WebSocket Streaming Endpoint**: `wss://api.vachana.ai/stt/v3/stream`
- **Authentication**: `x-api-key-id` header passed at connection time.
- **Language Code**: `language_code` parameter (e.g. `ta-IN`, `en-IN`, `hi-IN` or `indic-auto`).
- **PCM Specification**: 16-bit little-endian mono PCM, 16000 Hz (or 8000 Hz), 512 samples/chunk (1,024 bytes/frame).
- **Server Message Sequence**:
  - `connected`: Handshake confirmation.
  - `processing`: VAD speech-end acknowledgment.
  - `transcript`: Transcribed utterance segment with `text`, `segment_id`, `latency`, and optional `detected_language_code`.

## Supported Languages (from docs.gnani.ai/api/STT/languages.md)
- `bn-IN`: Bengali (বাংলা)
- `en-IN`: English (Latin)
- `gu-IN`: Gujarati (ગુજરાતી)
- `hi-IN`: Hindi (हिन्दी)
- `kn-IN`: Kannada (ಕನ್ನಡ)
- `ml-IN`: Malayalam (മലയാളം)
- `mr-IN`: Marathi (मराठी)
- `pa-IN`: Punjabi (ਪੰਜਾਬੀ)
- `ta-IN`: Tamil (தமிழ்)
- `te-IN`: Telugu (తెలుగు)
- `indic-auto`: Automatic language detection

## Key Features & Security
- Key rotation: Reads `GNANI_API_KEYS` (comma-separated, up to 3) and rotates round-robin.
- Never logs keys or raw audio bytes.
- Standardized error mapping to `contracts.models.ErrorCode`.

## How to Test
- Offline: `pytest modules/stt_gnani/tests -m "not live"`
- Live (with real keys): `GNANI_API_KEYS=key1 pytest modules/stt_gnani/tests -m live`
