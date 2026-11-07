import logging
from typing import Dict, List, Optional

from contracts.models import Entity, RiskLevel, TranslationResult
from providers.base import Translator

logger = logging.getLogger(__name__)


class IndicTranslator(Translator):
    """Optional IndicTrans2 model provider with lazy imports."""

    def __init__(self):
        self._initialized = False
        try:
            # Lazy check for IndicTrans2 or HuggingFace transformers
            import transformers  # noqa: F401
            self._available = True
        except ImportError:
            self._available = False
            logger.info("IndicTrans2 dependencies not available; skipping provider.")

    async def translate(
        self,
        text: str,
        src: str,
        tgt: str,
        glossary: Optional[Dict[str, str]] = None,
        entities: Optional[List[Entity]] = None,
    ) -> TranslationResult:
        if not self._available:
            raise RuntimeError("IndicTrans2 is not installed in the current environment.")

        # Real inference would go here if weights were loaded
        return TranslationResult(
            utterance_id="trans-indic",
            source_language=src,
            target_language=tgt,
            translated_text=f"[indic-{tgt}] {text}",
            entities=entities or [],
            risk_level=RiskLevel.LOW,
        )
