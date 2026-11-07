import json

import httpx
import pytest
from contracts.models import Entity, EntityType, RiskLevel
from providers.mocks import MockTranslator
from translation.indic import IndicTranslator
from translation.llm import LLMTranslator
from translation.router import TranslationRouter


@pytest.mark.anyio
async def test_mock_translation():
    translator = MockTranslator()
    res = await translator.translate("Hello", src="en", tgt="ta")
    assert res.target_language == "ta"
    assert res.translated_text == "வணக்கம்"


@pytest.mark.anyio
async def test_llm_translator_with_mock_http():
    async def handler(request: httpx.Request):
        payload = json.loads(request.read())
        user_msg = payload["messages"][1]["content"]
        if "500" in user_msg:
            resp_data = {"translation": "மெரினா செல்ல 500 ரூபாய்", "notes": "ok"}
        else:
            resp_data = {"translation": "வணக்கம்", "notes": "ok"}
        return httpx.Response(
            200,
            json={"choices": [{"message": {"content": json.dumps(resp_data)}}]}
        )

    transport = httpx.MockTransport(handler)
    async with httpx.AsyncClient(transport=transport) as client:
        llm = LLMTranslator(client=client)
        ent = Entity(type=EntityType.MONEY, value="500", span=[0, 3])
        res = await llm.translate("To Marina is 500 rupees", src="en", tgt="ta", entities=[ent])
        assert res.risk_level == RiskLevel.COMMITMENT
        assert "500" in res.translated_text


@pytest.mark.anyio
async def test_llm_translator_entity_mismatch_retry():
    calls = 0

    async def retry_handler(request: httpx.Request):
        nonlocal calls
        calls += 1
        if calls == 1:
            resp_data = {"translation": "மெரினா செல்ல ரூபாய்", "notes": "dropped number"}
        else:
            resp_data = {"translation": "மெரினா செல்ல 500 ரூபாய்", "notes": "fixed"}
        return httpx.Response(
            200,
            json={"choices": [{"message": {"content": json.dumps(resp_data)}}]}
        )

    transport = httpx.MockTransport(retry_handler)
    async with httpx.AsyncClient(transport=transport) as client:
        llm = LLMTranslator(client=client)
        res = await llm.translate("500 rupees", src="en", tgt="ta")
        assert calls == 2
        assert "500" in res.translated_text


def test_indic_translator_graceful_skip():
    indic = IndicTranslator()
    assert indic._available is False


@pytest.mark.anyio
async def test_translation_router():
    mock_prov = MockTranslator()
    router = TranslationRouter(
        llm_provider=mock_prov,
        mock_provider=mock_prov,
    )
    res = await router.translate("Marina", src="en", tgt="ta")
    assert res.target_language == "ta"
