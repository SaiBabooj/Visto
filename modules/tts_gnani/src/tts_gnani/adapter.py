import logging
import os
from collections.abc import AsyncIterator
from pathlib import Path
from typing import Dict, Optional

import httpx
import yaml
from providers.base import TTSProvider

logger = logging.getLogger(__name__)


def load_voice_config() -> Dict[str, str]:
    base_dir = Path(__file__).resolve().parents[4]
    cfg_path = base_dir / "config" / "tts_voices.yaml"
    if cfg_path.exists():
        with open(cfg_path, "r", encoding="utf-8") as f:
            data = yaml.safe_load(f)
            return data.get("voices", {})
    return {"ta": "Shivani", "en": "Kaveri", "hi": "Nalini"}


class GnaniTTSAdapter(TTSProvider):
    """Gnani Timbre Text-to-Speech streaming adapter with voice mapping and fallback."""

    def __init__(
        self,
        api_key: Optional[str] = None,
        endpoint: str = "https://api.vachana.ai/api/v1/tts/sse",
        model: str = "timbre-v3.0",
        voice_map: Optional[Dict[str, str]] = None,
    ):
        self.api_key = api_key or os.getenv("GNANI_API_KEY", "")
        self.endpoint = endpoint
        self.model = model
        self.voice_map = voice_map or load_voice_config()
        self._voice_cache: Dict[str, str] = {}

    def get_voice_for_language(self, lang: str) -> str:
        lang_code = lang.split("-")[0].lower()
        if lang_code in self._voice_cache:
            return self._voice_cache[lang_code]
        voice = self.voice_map.get(lang_code, "Shivani")
        self._voice_cache[lang_code] = voice
        return voice

    async def synthesize_stream(
        self,
        text: str,
        lang: str,
        voice: Optional[str] = None,
        ssml: bool = False,
    ) -> AsyncIterator[bytes]:
        selected_voice = voice or self.get_voice_for_language(lang)
        lang_code = f"{lang.split('-')[0].lower()}-IN" if "-" not in lang else lang

        if not self.api_key:
            # Offline / missing key fallback: emit a minimal silent audio chunk or text fallback
            logger.warning("No Gnani API key provided; returning text-only fallback payload")
            yield f"TEXT_FALLBACK:{text}".encode("utf-8")
            return

        headers = {
            "X-API-Key-ID": self.api_key,
            "Content-Type": "application/json",
        }

        payload = {
            "text": text,
            "model": self.model,
            "voice": selected_voice,
            "language": lang_code,
            "speed": 1.0,
            "audio_config": {
                "sample_rate": 16000,
                "encoding": "linear_pcm",
                "container": "wav",
            },
        }

        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                async with client.stream(
                    "POST", self.endpoint, json=payload, headers=headers
                ) as response:
                    if response.status_code != 200:
                        logger.error(f"Gnani TTS returned HTTP {response.status_code}")
                        yield f"TEXT_FALLBACK:{text}".encode("utf-8")
                        return

                    async for chunk in response.aiter_bytes():
                        if chunk:
                            yield chunk
        except Exception as e:
            logger.error(f"Gnani TTS request failed: {type(e).__name__}")
            yield f"TEXT_FALLBACK:{text}".encode("utf-8")
