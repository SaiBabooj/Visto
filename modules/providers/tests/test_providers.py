import asyncio

import pytest
from contracts.models import Entity, EntityType, RiskLevel, Utterance
from providers.base import TimingRecord, timing_decorator, with_retry, with_timeout
from providers.mocks import MockSTT, MockTranslator, MockTTS
from providers.registry import ProviderRegistry


@pytest.mark.anyio
async def test_mock_stt_streaming():
    stt = MockSTT()

    async def sample_audio_generator():
        yield b"chunk_1"
        yield b"chunk_2"

    events = []
    async for event in stt.transcribe_stream(sample_audio_generator(), "ta"):
        events.append(event)

    assert len(events) >= 2
    assert events[0].event_type == "utterance.partial"
    assert events[-1].event_type == "utterance.final"
    final_payload = events[-1].payload
    assert isinstance(final_payload, Utterance)
    assert final_payload.is_final is True


@pytest.mark.anyio
async def test_mock_translator_dictionary_and_fallback():
    translator = MockTranslator()
    # Dictionary lookup
    res_dict = await translator.translate("hello", src="en", tgt="ta")
    assert res_dict.translated_text == "வணக்கம்"
    assert res_dict.risk_level == RiskLevel.LOW

    # Glossary lookup
    res_glossary = await translator.translate(
        "custom_stop",
        src="en",
        tgt="ta",
        glossary={"custom_stop": "சிறப்பு நிறுத்தம்"},
    )
    assert res_glossary.translated_text == "சிறப்பு நிறுத்தம்"

    # Entities make it commitment risk
    ent = Entity(type=EntityType.MONEY, value="500", span=[0, 3])
    res_ent = await translator.translate("500 rupees", src="en", tgt="ta", entities=[ent])
    assert res_ent.risk_level == RiskLevel.COMMITMENT


@pytest.mark.anyio
async def test_mock_tts_stream():
    tts = MockTTS()
    chunks = []
    async for chunk in tts.synthesize_stream("வணக்கம்", lang="ta"):
        chunks.append(chunk)

    assert len(chunks) == 2
    assert chunks[0].startswith(b"RIFF")


def test_provider_registry(monkeypatch):
    monkeypatch.setenv("PROVIDER_STT", "mock")
    monkeypatch.setenv("PROVIDER_TRANSLATE", "mock")
    monkeypatch.setenv("PROVIDER_TTS", "mock")

    stt = ProviderRegistry.get_stt()
    tr = ProviderRegistry.get_translator()
    tts = ProviderRegistry.get_tts()

    assert isinstance(stt, MockSTT)
    assert isinstance(tr, MockTranslator)
    assert isinstance(tts, MockTTS)


@pytest.mark.anyio
async def test_timing_decorator():
    records = []

    def record_cb(rec: TimingRecord):
        records.append(rec)

    @timing_decorator("test_stage", callback=record_cb)
    async def sample_work():
        await asyncio.sleep(0.01)
        return "done"

    res = await sample_work()
    assert res == "done"
    assert len(records) == 1
    assert records[0].stage == "test_stage"
    assert records[0].duration_ms > 0
    assert records[0].success is True


@pytest.mark.anyio
async def test_with_retry():
    attempts = 0

    @with_retry(max_retries=2, delay_seconds=0.01)
    async def flakey_fn():
        nonlocal attempts
        attempts += 1
        if attempts < 2:
            raise ValueError("Temporary glitch")
        return "success"

    result = await flakey_fn()
    assert result == "success"
    assert attempts == 2


@pytest.mark.anyio
async def test_with_timeout():
    @with_timeout(timeout_seconds=0.05)
    async def slow_fn():
        await asyncio.sleep(0.2)
        return "slow"

    with pytest.raises(asyncio.TimeoutError):
        await slow_fn()
