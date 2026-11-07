import time
from dataclasses import dataclass
from difflib import SequenceMatcher
from enum import Enum
from typing import Dict, List, Literal, Optional

from contracts.models import ConfirmRequest, ConfirmResponse, Entity, EntityType, RiskLevel
from language.tagger import tag_entities
from providers.base import Translator


class ConfirmState(str, Enum):
    PENDING = "pending"
    CONFIRMED = "confirmed"
    REJECTED = "rejected"
    EDITED = "edited"
    EXPIRED = "expired"


@dataclass
class VerificationOutcome:
    risk_level: RiskLevel
    back_translated_text: Optional[str]
    entity_match: bool
    similarity_score: float
    is_deliverable: bool
    confirm_request: Optional[ConfirmRequest] = None


def classify_risk(text: str, entities: Optional[List[Entity]] = None) -> RiskLevel:
    """Classifies risk level: commitment if any money, time, duration, count or place is found."""
    found_entities = entities if entities is not None else tag_entities(text)
    commitment_types = {
        EntityType.MONEY,
        EntityType.DURATION,
        EntityType.TIME,
        EntityType.PLACE,
        EntityType.COUNT,
    }
    for e in found_entities:
        if e.type in commitment_types:
            return RiskLevel.COMMITMENT
    return RiskLevel.LOW


def calculate_similarity(text_a: str, text_b: str) -> float:
    """Calculates normalized sequence similarity ratio."""
    return SequenceMatcher(None, text_a.lower().strip(), text_b.lower().strip()).ratio()


class ConfirmStateMachine:
    """State machine tracking user confirmation of high-risk commitments."""

    def __init__(self, timeout_seconds: float = 30.0):
        self.timeout_seconds = timeout_seconds
        self._requests: Dict[str, Dict] = {}

    def create_request(
        self,
        request_id: str,
        summary_text: str,
        entities: List[Entity],
        target_role: Literal["traveller", "driver"],
    ) -> ConfirmRequest:
        req = ConfirmRequest(
            request_id=request_id,
            summary_text=summary_text,
            entities=entities,
            target_role=target_role,
        )
        self._requests[request_id] = {
            "request": req,
            "state": ConfirmState.PENDING,
            "created_at": time.time(),
            "notes": None,
        }
        return req

    def process_response(self, response: ConfirmResponse) -> ConfirmState:
        entry = self._requests.get(response.request_id)
        if not entry:
            return ConfirmState.REJECTED

        # Check expiration
        if (time.time() - entry["created_at"]) > self.timeout_seconds:
            entry["state"] = ConfirmState.EXPIRED
            return ConfirmState.EXPIRED

        if response.confirmed:
            entry["state"] = ConfirmState.CONFIRMED
        else:
            if response.notes and "edit" in response.notes.lower():
                entry["state"] = ConfirmState.EDITED
            else:
                entry["state"] = ConfirmState.REJECTED

        entry["notes"] = response.notes
        return entry["state"]

    def get_state(self, request_id: str) -> ConfirmState:
        entry = self._requests.get(request_id)
        if not entry:
            return ConfirmState.EXPIRED
        elapsed = time.time() - entry["created_at"]
        if entry["state"] == ConfirmState.PENDING and elapsed > self.timeout_seconds:
            entry["state"] = ConfirmState.EXPIRED
        return entry["state"]


class VerificationLayer:
    """Orchestrates risk assessment, back-translation, comparison, and confirm flow."""

    def __init__(self, translator: Translator, state_machine: Optional[ConfirmStateMachine] = None):
        self.translator = translator
        self.state_machine = state_machine or ConfirmStateMachine()

    async def verify_translation(
        self,
        source_text: str,
        translated_text: str,
        source_lang: str,
        target_lang: str,
        speaker_role: Literal["traveller", "driver"],
        request_id: str,
    ) -> VerificationOutcome:
        src_entities = tag_entities(source_text)
        risk = classify_risk(source_text, src_entities)

        # Back-translate target text back into speaker's original language
        back_res = await self.translator.translate(
            text=translated_text,
            src=target_lang,
            tgt=source_lang,
        )
        back_text = back_res.translated_text
        sim_score = calculate_similarity(source_text, back_text)

        # Check entity preservation
        back_entities = tag_entities(back_text)
        src_values = {e.value for e in src_entities if e.type == EntityType.MONEY}
        back_values = {e.value for e in back_entities if e.type == EntityType.MONEY}
        entity_match = src_values == back_values

        confirm_req = None
        if risk == RiskLevel.COMMITMENT:
            # Create a confirmation request with back-translated summary in speaker's language
            confirm_req = self.state_machine.create_request(
                request_id=request_id,
                summary_text=back_text,
                entities=src_entities,
                target_role=speaker_role,
            )
            is_deliverable = False  # NEVER deliver a commitment without confirmed state
        else:
            is_deliverable = True

        return VerificationOutcome(
            risk_level=risk,
            back_translated_text=back_text,
            entity_match=entity_match,
            similarity_score=sim_score,
            is_deliverable=is_deliverable,
            confirm_request=confirm_req,
        )
