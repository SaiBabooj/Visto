from contracts.models import Utterance
from translation.provider import MockTranslator


def test_mock_translation():
    translator = MockTranslator()
    utt = Utterance(
        id="u-123",
        speaker="traveller",
        text="Hello, how much to Marina Beach?",
        language="en",
    )
    res = translator.translate(utt, "ta")
    assert res.utterance_id == "u-123"
    assert res.target_language == "ta"
    assert "[ta]" in res.translated_text
