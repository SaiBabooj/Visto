import json
import os

import pytest
import websockets
from contracts.models import Utterance
from stt_gnani.adapter import GnaniSTTAdapter


@pytest.mark.anyio
async def test_gnani_stt_round_robin_keys():
    adapter = GnaniSTTAdapter(api_keys=["key1", "key2", "key3"])
    assert adapter._get_next_api_key() == "key1"
    assert adapter._get_next_api_key() == "key2"
    assert adapter._get_next_api_key() == "key3"
    assert adapter._get_next_api_key() == "key1"


@pytest.mark.anyio
async def test_gnani_stt_offline_mock_server():
    # Spin up a local mock WebSocket server simulating Gnani Prisma
    async def mock_gnani_handler(websocket):
        async for msg in websocket:
            # When receiving audio chunk, reply with processing and then transcript
            await websocket.send(
                json.dumps(
                    {
                        "type": "processing",
                        "segment_id": "seg-101",
                        "timestamp": "2026-11-07T18:00:00Z",
                    }
                )
            )
            await websocket.send(
                json.dumps(
                    {
                        "type": "transcript",
                        "segment_id": "seg-101",
                        "text": "மெரினா கடற்கரை",
                        "detected_language_code": "ta-IN",
                        "timestamp": "2026-11-07T18:00:01Z",
                    }
                )
            )
            break

    server = await websockets.serve(mock_gnani_handler, "127.0.0.1", 8765)
    try:
        adapter = GnaniSTTAdapter(
            api_keys=["test-key"],
            endpoint="ws://127.0.0.1:8765",
        )

        async def audio_gen():
            yield b"\x00\x00" * 512

        events = []
        async for event in adapter.transcribe_stream(audio_gen(), "ta"):
            events.append(event)

        assert len(events) == 2
        assert events[0].event_type == "utterance.partial"
        assert events[1].event_type == "utterance.final"
        payload = events[1].payload
        assert isinstance(payload, Utterance)
        assert payload.text == "மெரினா கடற்கரை"
        assert payload.is_final is True
    finally:
        server.close()
        await server.wait_closed()


@pytest.mark.live
@pytest.mark.anyio
async def test_gnani_stt_live():
    api_key = os.getenv("GNANI_API_KEY")
    if not api_key:
        pytest.skip("GNANI_API_KEY not set for live testing")

    adapter = GnaniSTTAdapter()

    async def empty_audio():
        yield b"\x00\x00" * 512

    events = []
    async for event in adapter.transcribe_stream(empty_audio(), "en"):
        events.append(event)
    assert len(events) > 0
