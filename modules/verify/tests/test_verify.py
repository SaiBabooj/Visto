import asyncio

import pytest
from contracts.models import ConfirmResponse, Entity, EntityType, RiskLevel
from providers.mocks import MockTranslator
from verify.verifier import (
    ConfirmState,
    ConfirmStateMachine,
    VerificationLayer,
    classify_risk,
)


def test_classify_risk():
    assert classify_risk("Hello, how are you?") == RiskLevel.LOW
    assert classify_risk("500 rupees") == RiskLevel.COMMITMENT
    assert classify_risk("Wait for 30 minutes") == RiskLevel.COMMITMENT
    assert classify_risk("Marina Beach") == RiskLevel.COMMITMENT


def test_confirm_state_machine_flow():
    sm = ConfirmStateMachine(timeout_seconds=0.1)
    ent = [Entity(type=EntityType.MONEY, value="500", span=[0, 3])]

    # Confirm path
    sm.create_request("req-1", "Fare 500", ent, "driver")
    assert sm.get_state("req-1") == ConfirmState.PENDING
    state = sm.process_response(ConfirmResponse(request_id="req-1", confirmed=True))
    assert state == ConfirmState.CONFIRMED

    # Reject path
    sm.create_request("req-2", "Fare 1000", ent, "driver")
    state = sm.process_response(ConfirmResponse(request_id="req-2", confirmed=False))
    assert state == ConfirmState.REJECTED

    # Edit path
    sm.create_request("req-3", "Fare 700", ent, "driver")
    state = sm.process_response(
        ConfirmResponse(request_id="req-3", confirmed=False, notes="I want to edit")
    )
    assert state == ConfirmState.EDITED


@pytest.mark.anyio
async def test_confirm_state_machine_timeout():
    sm = ConfirmStateMachine(timeout_seconds=0.02)
    sm.create_request("req-timeout", "Fare 500", [], "traveller")
    await asyncio.sleep(0.05)
    assert sm.get_state("req-timeout") == ConfirmState.EXPIRED


@pytest.mark.anyio
async def test_verification_layer_commitment_not_deliverable_initially():
    translator = MockTranslator()
    verifier = VerificationLayer(translator=translator)

    outcome = await verifier.verify_translation(
        source_text="Trip fare is 500 rupees",
        translated_text="பயண கட்டணம் 500 ரூபாய்",
        source_lang="en",
        target_lang="ta",
        speaker_role="driver",
        request_id="req-commit-1",
    )

    assert outcome.risk_level == RiskLevel.COMMITMENT
    assert outcome.confirm_request is not None
    # Strict rule: A commitment without confirmation is NEVER marked deliverable!
    assert outcome.is_deliverable is False


@pytest.mark.anyio
async def test_verification_layer_low_risk_deliverable():
    translator = MockTranslator()
    verifier = VerificationLayer(translator=translator)

    outcome = await verifier.verify_translation(
        source_text="Hello",
        translated_text="வணக்கம்",
        source_lang="en",
        target_lang="ta",
        speaker_role="traveller",
        request_id="req-low-1",
    )

    assert outcome.risk_level == RiskLevel.LOW
    assert outcome.is_deliverable is True
    assert outcome.confirm_request is None
