from pathlib import Path
from typing import Dict, List, Optional

import yaml
from contracts.models import Entity, TranslationResult
from providers.base import Translator
from providers.mocks import MockTranslator

from translation.indic import IndicTranslator
from translation.llm import LLMTranslator


class TranslationRouter(Translator):
    """Router that selects translation provider based on language pair and config."""

    def __init__(
        self,
        config_path: Optional[str] = None,
        llm_provider: Optional[Translator] = None,
        indic_provider: Optional[Translator] = None,
        mock_provider: Optional[Translator] = None,
    ):
        self.llm = llm_provider or LLMTranslator()
        self.indic = indic_provider or IndicTranslator()
        self.mock = mock_provider or MockTranslator()
        self.routes = self._load_routes(config_path)

    def _load_routes(self, config_path: Optional[str] = None) -> Dict[str, str]:
        if config_path is None:
            base_dir = Path(__file__).resolve().parents[4]
            cfg_file = base_dir / "config" / "translate_routes.yaml"
        else:
            cfg_file = Path(config_path)

        if not cfg_file.exists():
            return {}

        with open(cfg_file, "r", encoding="utf-8") as f:
            data = yaml.safe_load(f)
            return data.get("routes", {})

    def get_provider(self, src: str, tgt: str) -> Translator:
        pair = f"{src.split('-')[0].lower()}->{tgt.split('-')[0].lower()}"
        choice = self.routes.get(pair, "llm").lower()
        if choice == "indic":
            return self.indic
        elif choice == "mock":
            return self.mock
        return self.llm

    async def translate(
        self,
        text: str,
        src: str,
        tgt: str,
        glossary: Optional[Dict[str, str]] = None,
        entities: Optional[List[Entity]] = None,
    ) -> TranslationResult:
        provider = self.get_provider(src, tgt)
        return await provider.translate(text, src, tgt, glossary, entities)
