import pytest
from tts_gnani.adapter import GnaniTTSAdapter


def test_voice_selection_and_cache():
    adapter = GnaniTTSAdapter(voice_map={"ta": "Shivani", "en": "Kaveri", "hi": "Nalini"})
    assert adapter.get_voice_for_language("ta") == "Shivani"
    assert adapter.get_voice_for_language("en-IN") == "Kaveri"
    assert adapter.get_voice_for_language("hi") == "Nalini"
    assert adapter.get_voice_for_language("unknown") == "Shivani"


@pytest.mark.anyio
async def test_offline_fallback_when_no_key():
    adapter = GnaniTTSAdapter(api_key="")
    chunks = []
    async for chunk in adapter.synthesize_stream("வணக்கம்", lang="ta"):
        chunks.append(chunk)

    assert len(chunks) == 1
    assert chunks[0].startswith(b"TEXT_FALLBACK:")


@pytest.mark.live
@pytest.mark.anyio
async def test_gnani_tts_live():
    import os
    api_key = os.getenv("GNANI_API_KEY")
    if not api_key:
        pytest.skip("GNANI_API_KEY not set for live testing")

    adapter = GnaniTTSAdapter(api_key=api_key)
    chunks = []
    async for chunk in adapter.synthesize_stream("Hello, welcome to Chennai", lang="en"):
        chunks.append(chunk)

    assert len(chunks) > 0
