import os
from typing import Dict, Type

from providers.base import STTProvider, Translator, TTSProvider
from providers.mocks import MockSTT, MockTranslator, MockTTS


class ProviderRegistry:
    """Registry managing active STT, Translation, and TTS providers
    based on environment variables."""

    _stt_classes: Dict[str, Type[STTProvider]] = {
        "mock": MockSTT,
    }
    _translator_classes: Dict[str, Type[Translator]] = {
        "mock": MockTranslator,
    }
    _tts_classes: Dict[str, Type[TTSProvider]] = {
        "mock": MockTTS,
    }

    @classmethod
    def register_stt(cls, name: str, provider_cls: Type[STTProvider]):
        cls._stt_classes[name.lower()] = provider_cls

    @classmethod
    def register_translator(cls, name: str, provider_cls: Type[Translator]):
        cls._translator_classes[name.lower()] = provider_cls

    @classmethod
    def register_tts(cls, name: str, provider_cls: Type[TTSProvider]):
        cls._tts_classes[name.lower()] = provider_cls

    @classmethod
    def get_stt(cls) -> STTProvider:
        name = os.getenv("PROVIDER_STT", os.getenv("STT_PROVIDER", "mock")).lower()
        provider_cls = cls._stt_classes.get(name, MockSTT)
        return provider_cls()

    @classmethod
    def get_translator(cls) -> Translator:
        name = os.getenv("PROVIDER_TRANSLATE", os.getenv("TRANSLATION_PROVIDER", "mock")).lower()
        provider_cls = cls._translator_classes.get(name, MockTranslator)
        return provider_cls()

    @classmethod
    def get_tts(cls) -> TTSProvider:
        name = os.getenv("PROVIDER_TTS", os.getenv("TTS_PROVIDER", "mock")).lower()
        provider_cls = cls._tts_classes.get(name, MockTTS)
        return provider_cls()
