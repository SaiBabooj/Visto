import json
import logging
import os
import re
from typing import Dict, List, Optional

import httpx
from contracts.models import Entity, RiskLevel, TranslationResult
from language.tagger import tag_entities
from providers.base import Translator

logger = logging.getLogger(__name__)


class LLMTranslator(Translator):
    """OpenAI-compatible LLM translator (works with vLLM, Ollama, Evon, etc.)."""

    def __init__(
        self,
        base_url: Optional[str] = None,
        model: Optional[str] = None,
        api_key: Optional[str] = None,
        client: Optional[httpx.AsyncClient] = None,
    ):
        raw_url = base_url or os.getenv("LLM_BASE_URL", "https://api.openai.com/v1")
        self.base_url = raw_url.rstrip("/")
        self.model = model or os.getenv("LLM_MODEL", "gpt-4o-mini")
        self.api_key = api_key or os.getenv("OPENAI_API_KEY", os.getenv("LLM_API_KEY", "mock-key"))
        self._client = client

    def _extract_numbers(self, text: str) -> List[str]:
        return re.findall(r"\d+", text)

    def _validate_entities(self, src_text: str, tgt_text: str) -> bool:
        src_nums = self._extract_numbers(src_text)
        tgt_nums = self._extract_numbers(tgt_text)
        return src_nums == tgt_nums

    async def _call_llm(self, prompt: str, client: httpx.AsyncClient) -> Dict[str, str]:
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }
        body = {
            "model": self.model,
            "temperature": 0.0,
            "response_format": {"type": "json_object"},
            "messages": [
                {
                    "role": "system",
                    "content": (
                        "You are an exact translation engine for travellers and auto/cab drivers. "
                        "Translate only. Add nothing. Preserve all numbers and names. "
                        "Return strictly a JSON object: "
                        "{\"translation\": \"...\", \"notes\": \"...\"}"
                    ),
                },
                {"role": "user", "content": prompt},
            ],
        }
        resp = await client.post(
            f"{self.base_url}/chat/completions",
            headers=headers,
            json=body,
            timeout=10.0,
        )
        resp.raise_for_status()
        data = resp.json()
        raw_content = data["choices"][0]["message"]["content"]
        return json.loads(raw_content)

    async def translate(
        self,
        text: str,
        src: str,
        tgt: str,
        glossary: Optional[Dict[str, str]] = None,
        entities: Optional[List[Entity]] = None,
    ) -> TranslationResult:
        src_entities = entities or tag_entities(text)
        glossary_note = ""
        if glossary:
            terms = ", ".join([f"{k} -> {v}" for k, v in glossary.items()])
            glossary_note = f"\nUse these glossary term translations: {terms}."

        prompt = f"Source language: {src}\nTarget language: {tgt}{glossary_note}\nText: {text}"

        client = self._client or httpx.AsyncClient()
        attempt = 0
        translated_text = ""

        try:
            while attempt < 2:
                attempt += 1
                try:
                    res = await self._call_llm(prompt, client)
                    translated_text = res.get("translation", text)

                    # Validate that numbers and entities match
                    if self._validate_entities(text, translated_text):
                        break
                    logger.warning(
                        f"Entity mismatch on attempt {attempt}: {text} -> {translated_text}"
                    )
                except Exception as e:
                    logger.error(f"LLM translation call error: {e}")
                    if attempt >= 2:
                        translated_text = f"[{tgt}] {text}"
        finally:
            if not self._client:
                await client.aclose()

        is_valid = self._validate_entities(text, translated_text)
        risk = RiskLevel.COMMITMENT if (src_entities and len(src_entities) > 0) else RiskLevel.LOW
        if not is_valid:
            risk = RiskLevel.COMMITMENT

        return TranslationResult(
            utterance_id="trans-llm",
            source_language=src,
            target_language=tgt,
            translated_text=translated_text,
            entities=src_entities,
            risk_level=risk,
        )
