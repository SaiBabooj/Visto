import hashlib
from collections.abc import AsyncIterator
from typing import Dict, List, Optional

from contracts.models import Entity, RiskLevel, TranslationResult, Utterance, WSEventEnvelope

from providers.base import STTProvider, Translator, TTSProvider

# Scripted transcription fixture keyed by SHA256 of first chunk or default
DEFAULT_FIXTURES: Dict[str, str] = {
    "default": "Marina Beach eppadi poganum?",
    "pricing": "Thousand rupees for round trip",
}

# Small translation dictionary for offline unit tests
DICTIONARY: Dict[str, Dict[str, str]] = {
    "hello": {"ta": "வணக்கம்", "hi": "नमस्ते"},
    "marina beach": {"ta": "மெரினா கடற்கரை", "hi": "मरीना बीच"},
    "how much": {"ta": "எவ்வளவு", "hi": "कितना"},
    "yes": {"ta": "ஆம்", "hi": "हाँ"},
    "no": {"ta": "இல்லை", "hi": "नहीं"},
}


class MockSTT(STTProvider):
    """Mock STT returning scripted partial and final utterances."""

    def __init__(self, fixtures: Optional[Dict[str, str]] = None):
        self.fixtures = fixtures or DEFAULT_FIXTURES

    async def transcribe_stream(
        self, audio_chunks: AsyncIterator[bytes], lang: str
    ) -> AsyncIterator[WSEventEnvelope]:
        first_chunk = b""
        async for chunk in audio_chunks:
            if not first_chunk and chunk:
                first_chunk = chunk
                # Emit a partial event
                yield WSEventEnvelope(
                    event_type="utterance.partial",
                    session_id="mock-session",
                    payload=Utterance(
                        id="utt-part-1",
                        speaker="traveller",
                        text="...",
                        language=lang,
                        is_final=False,
                    ),
                )

        audio_hash = hashlib.sha256(first_chunk).hexdigest()[:8] if first_chunk else "empty"
        transcript = self.fixtures.get(audio_hash, self.fixtures.get("default", "Vanakkam"))

        # Emit final event
        yield WSEventEnvelope(
            event_type="utterance.final",
            session_id="mock-session",
            payload=Utterance(
                id=f"utt-fin-{audio_hash}",
                speaker="traveller",
                text=transcript,
                language=lang,
                is_final=True,
            ),
        )


class MockTranslator(Translator):
    """Mock Translator using a small dictionary or deterministic bracketed translation."""

    def __init__(self, dictionary: Optional[Dict[str, Dict[str, str]]] = None):
        self.dict = dictionary or DICTIONARY

    async def translate(
        self,
        text: str,
        src: str,
        tgt: str,
        glossary: Optional[Dict[str, str]] = None,
        entities: Optional[List[Entity]] = None,
    ) -> TranslationResult:
        # Check dictionary
        lower = text.strip().lower()
        if lower in self.dict and tgt in self.dict[lower]:
            translated = self.dict[lower][tgt]
        elif glossary and lower in glossary:
            translated = glossary[lower]
        else:
            translated = f"[{tgt}] {text}"

        risk = RiskLevel.COMMITMENT if (entities and len(entities) > 0) else RiskLevel.LOW
        return TranslationResult(
            utterance_id="mock-utt-1",
            source_language=src,
            target_language=tgt,
            translated_text=translated,
            entities=entities or [],
            risk_level=risk,
        )


class MockTTS(TTSProvider):
    """Mock TTS generating a short valid synthetic WAV header/payload."""

    async def synthesize_stream(
        self,
        text: str,
        lang: str,
        voice: Optional[str] = None,
        ssml: bool = False,
    ) -> AsyncIterator[bytes]:
        # Minimal 44-byte standard RIFF PCM WAV header
        header = (
            b"RIFF\x2c\x00\x00\x00WAVEfmt \x10\x00\x00\x00\x01\x00\x01\x00"
            b"\x80>\x00\x00\x00}\x00\x00\x02\x00\x10\x00data\x08\x00\x00\x00"
        )
        yield header
        # Short audio payload chunk
        yield b"\x00\x00\x7f\x7f\x00\x00\x80\x80"
