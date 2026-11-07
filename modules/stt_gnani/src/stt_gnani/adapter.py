import json
import logging
import os
from collections.abc import AsyncIterator
from typing import List, Optional

import websockets
from contracts.models import ErrorCode, ErrorPayload, Utterance, WSEventEnvelope
from providers.base import STTProvider

logger = logging.getLogger(__name__)

# Normalize 2-letter language codes to Gnani's expected locale format
GNANI_LANG_MAP = {
    "ta": "ta-IN",
    "en": "en-IN",
    "hi": "hi-IN",
    "bn": "bn-IN",
    "gu": "gu-IN",
    "kn": "kn-IN",
    "ml": "ml-IN",
    "mr": "mr-IN",
    "pa": "pa-IN",
    "te": "te-IN",
    "auto": "indic-auto",
    "indic-auto": "indic-auto",
}


class GnaniSTTAdapter(STTProvider):
    """Gnani Prisma WebSocket Speech-to-Text streaming adapter with API key rotation."""

    def __init__(
        self,
        api_keys: Optional[List[str]] = None,
        endpoint: str = "wss://api.vachana.ai/stt/v3/stream",
        sample_rate: int = 16000,
    ):
        if api_keys is None:
            raw_keys = os.getenv("GNANI_API_KEYS", os.getenv("GNANI_API_KEY", ""))
            self.api_keys = [k.strip() for k in raw_keys.split(",") if k.strip()][:3]
        else:
            self.api_keys = api_keys

        self.endpoint = endpoint
        self.sample_rate = sample_rate
        self._key_index = 0

    def _get_next_api_key(self) -> str:
        if not self.api_keys:
            return ""
        key = self.api_keys[self._key_index % len(self.api_keys)]
        self._key_index += 1
        return key

    async def transcribe_stream(
        self, audio_chunks: AsyncIterator[bytes], lang: str
    ) -> AsyncIterator[WSEventEnvelope]:
        api_key = self._get_next_api_key()
        if not api_key:
            yield WSEventEnvelope(
                event_type="error",
                session_id="gnani-stt-unauth",
                payload=ErrorPayload(
                    code=ErrorCode.UNAUTHORIZED,
                    message="Missing Gnani API key in GNANI_API_KEYS",
                ),
            )
            return

        gnani_lang = GNANI_LANG_MAP.get(lang.lower(), lang)
        headers = {
            "x-api-key-id": api_key,
            "language_code": gnani_lang,
            "x-sample-rate": str(self.sample_rate),
        }

        try:
            async with websockets.connect(self.endpoint, additional_headers=headers) as ws:
                # Task to send binary chunks
                async def sender():
                    try:
                        async for chunk in audio_chunks:
                            if chunk:
                                await ws.send(chunk)
                    except Exception as e:
                        logger.error(f"Error streaming audio to Gnani: {type(e).__name__}")

                import asyncio
                sender_task = asyncio.create_task(sender())

                # Receive messages from Gnani
                async for msg in ws:
                    try:
                        data = json.loads(msg)
                        msg_type = data.get("type")

                        if msg_type == "processing":
                            yield WSEventEnvelope(
                                event_type="utterance.partial",
                                session_id=data.get("segment_id", "gnani-seg"),
                                payload=Utterance(
                                    id=data.get("segment_id", "gnani-seg"),
                                    speaker="traveller",
                                    text="...",
                                    language=lang,
                                    is_final=False,
                                ),
                            )
                        elif msg_type == "transcript":
                            text = data.get("text", "")
                            seg_id = data.get("segment_id", "gnani-final")
                            det_lang = data.get("detected_language_code", lang)
                            yield WSEventEnvelope(
                                event_type="utterance.final",
                                session_id=seg_id,
                                payload=Utterance(
                                    id=seg_id,
                                    speaker="traveller",
                                    text=text,
                                    language=det_lang,
                                    is_final=True,
                                ),
                            )
                        elif msg_type == "error":
                            yield WSEventEnvelope(
                                event_type="error",
                                session_id="gnani-error",
                                payload=ErrorPayload(
                                    code=ErrorCode.STT_SERVICE_ERROR,
                                    message=data.get("message", "Gnani STT error"),
                                ),
                            )
                    except json.JSONDecodeError:
                        continue

                await sender_task

        except websockets.exceptions.InvalidStatusCode as e:
            code = ErrorCode.UNAUTHORIZED if e.status_code == 401 else ErrorCode.STT_SERVICE_ERROR
            yield WSEventEnvelope(
                event_type="error",
                session_id="gnani-conn-err",
                payload=ErrorPayload(
                    code=code,
                    message=f"Gnani STT connection failed with HTTP {e.status_code}",
                ),
            )
        except Exception as e:
            yield WSEventEnvelope(
                event_type="error",
                session_id="gnani-err",
                payload=ErrorPayload(
                    code=ErrorCode.STT_SERVICE_ERROR,
                    message=f"STT stream exception: {type(e).__name__}",
                ),
            )
