from contracts.models import TranslationResult, Utterance


class MockTranslator:
    """Mock translation provider for testing and development."""

    def translate(self, utterance: Utterance, target_language: str) -> TranslationResult:
        return TranslationResult(
            utterance_id=utterance.id,
            source_language=utterance.language,
            target_language=target_language,
            translated_text=f"[{target_language}] {utterance.text}",
            entities=utterance.entities,
        )
