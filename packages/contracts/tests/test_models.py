from contracts.models import (
    Agreement,
    Commitment,
    Driver,
    Entity,
    EntityType,
    ErrorCode,
    ErrorPayload,
    Language,
    RiskLevel,
    TranslationResult,
    Utterance,
    WSEventEnvelope,
)


def test_language_loading_and_roundtrip():
    lang = Language(code="ta", native_name="தமிழ்", english_name="Tamil")
    data = lang.model_dump()
    reloaded = Language.model_validate(data)
    assert reloaded.code == "ta"
    assert reloaded.native_name == "தமிழ்"

    languages = Language.load_languages()
    assert len(languages) >= 2
    assert any(lang.code == "ta" for lang in languages)


def test_entity_and_utterance_roundtrip():
    entity = Entity(type=EntityType.MONEY, value="300", span=[10, 13])
    utterance = Utterance(
        id="utt-001",
        speaker="driver",
        text="That will be 300 rupees",
        language="en",
        entities=[entity],
    )
    json_str = utterance.model_dump_json()
    reloaded = Utterance.model_validate_json(json_str)
    assert reloaded.id == "utt-001"
    assert len(reloaded.entities) == 1
    assert reloaded.entities[0].type == EntityType.MONEY
    assert reloaded.entities[0].value == "300"


def test_translation_and_risk_roundtrip():
    result = TranslationResult(
        utterance_id="utt-001",
        source_language="en",
        target_language="ta",
        translated_text="அது 300 ரூபாய் ஆகும்",
        risk_level=RiskLevel.COMMITMENT,
    )
    dumped = result.model_dump()
    reloaded = TranslationResult.model_validate(dumped)
    assert reloaded.risk_level == RiskLevel.COMMITMENT
    assert reloaded.target_language == "ta"


def test_driver_plan_commitment_agreement_roundtrip():
    driver = Driver(id="drv-1", name="Murugan", vehicle_number="TN01AB1234")
    commitment = Commitment(
        price=500.0,
        hours=2.0,
        waiting_charge=50.0,
        inclusions=["fuel", "tolls"],
    )
    agreement = Agreement(
        agreement_id="agr-1",
        trip_id="trip-1",
        driver_id=driver.id,
        commitment=commitment,
        confirmed_by_traveller=True,
        confirmed_by_driver=True,
        created_at="2026-11-07T12:00:00Z",
    )

    data = agreement.model_dump_json()
    reloaded = Agreement.model_validate_json(data)
    assert reloaded.commitment.price == 500.0
    assert reloaded.confirmed_by_traveller is True


def test_ws_event_envelope_roundtrip():
    error_payload = ErrorPayload(
        code=ErrorCode.STT_SERVICE_ERROR,
        message="Gnani STT connection failed",
        details={"retry": True},
    )
    env = WSEventEnvelope(
        event_type="error",
        session_id="sess-xyz",
        payload=error_payload,
    )

    serialized = env.model_dump_json()
    reloaded = WSEventEnvelope.model_validate_json(serialized)
    assert reloaded.event_type == "error"
    assert reloaded.session_id == "sess-xyz"
