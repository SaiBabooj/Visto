from enum import Enum
from pathlib import Path
from typing import Any, List, Literal, Optional, Union

import yaml
from pydantic import BaseModel, Field


# -------------------------------------------------------------------------
# Language
# -------------------------------------------------------------------------
class Language(BaseModel):
    code: str
    native_name: str
    english_name: str
    stt_supported: bool = True
    tts_supported: bool = True

    @classmethod
    def load_languages(cls, config_path: Optional[str] = None) -> List["Language"]:
        if config_path is None:
            # Look up from project root
            base_dir = Path(__file__).resolve().parents[4]
            config_file = base_dir / "config" / "languages.yaml"
        else:
            config_file = Path(config_path)

        if not config_file.exists():
            return []

        with open(config_file, "r", encoding="utf-8") as f:
            data = yaml.safe_load(f)
            return [cls(**item) for item in data.get("languages", [])]


# -------------------------------------------------------------------------
# Entity & Risk
# -------------------------------------------------------------------------
class EntityType(str, Enum):
    MONEY = "money"
    DURATION = "duration"
    TIME = "time"
    PLACE = "place"
    COUNT = "count"
    VEHICLE_TERM = "vehicle_term"


class Entity(BaseModel):
    type: EntityType
    value: str
    span: List[int] = Field(description="[start_offset, end_offset] within text")


class RiskLevel(str, Enum):
    LOW = "low"
    COMMITMENT = "commitment"


# -------------------------------------------------------------------------
# Utterance, Translation & Confirmation
# -------------------------------------------------------------------------
class Utterance(BaseModel):
    id: str
    speaker: Literal["traveller", "driver"]
    text: str
    language: str
    is_final: bool = True
    entities: List[Entity] = Field(default_factory=list)


class TranslationResult(BaseModel):
    utterance_id: str
    source_language: str
    target_language: str
    translated_text: str
    entities: List[Entity] = Field(default_factory=list)
    risk_level: RiskLevel = RiskLevel.LOW


class ConfirmRequest(BaseModel):
    request_id: str
    summary_text: str
    entities: List[Entity] = Field(default_factory=list)
    target_role: Literal["traveller", "driver"]


class ConfirmResponse(BaseModel):
    request_id: str
    confirmed: bool
    notes: Optional[str] = None


# -------------------------------------------------------------------------
# Driver, Trip, Plan & Agreement
# -------------------------------------------------------------------------
class Driver(BaseModel):
    id: str
    name: str
    vehicle_number: str
    vehicle_type: str = "auto"
    phone_number: Optional[str] = None


class TripRequest(BaseModel):
    id: str
    pickup_location: str
    destination: Optional[str] = None
    passenger_count: int = 1
    traveller_language: str = "en"
    driver_language: str = "ta"


class PlanItem(BaseModel):
    step_number: int
    title: str
    location: str
    estimated_duration_minutes: Optional[int] = None


class Plan(BaseModel):
    trip_id: str
    items: List[PlanItem] = Field(default_factory=list)
    estimated_total_km: Optional[float] = None


class Commitment(BaseModel):
    price: float = Field(description="Agreed fare in INR")
    hours: Optional[float] = Field(default=None, description="Agreed duration if charter")
    waiting_charge: Optional[float] = Field(default=None, description="Waiting charge per hour")
    inclusions: List[str] = Field(default_factory=list, description="Tolls, fuel, etc.")


class Agreement(BaseModel):
    agreement_id: str
    trip_id: str
    driver_id: str
    commitment: Commitment
    confirmed_by_traveller: bool
    confirmed_by_driver: bool
    created_at: str


# -------------------------------------------------------------------------
# Errors
# -------------------------------------------------------------------------
class ErrorCode(str, Enum):
    INVALID_AUDIO_FORMAT = "INVALID_AUDIO_FORMAT"
    STT_SERVICE_ERROR = "STT_SERVICE_ERROR"
    TTS_SERVICE_ERROR = "TTS_SERVICE_ERROR"
    TRANSLATION_FAILED = "TRANSLATION_FAILED"
    CONNECTION_LOST = "CONNECTION_LOST"
    UNAUTHORIZED = "UNAUTHORIZED"
    VALIDATION_ERROR = "VALIDATION_ERROR"
    INTERNAL_ERROR = "INTERNAL_ERROR"


class ErrorPayload(BaseModel):
    code: ErrorCode
    message: str
    details: Optional[dict[str, Any]] = None


# -------------------------------------------------------------------------
# WebSocket Event Envelope
# -------------------------------------------------------------------------
EventType = Literal[
    "audio.start",
    "audio.chunk",
    "audio.end",
    "utterance.partial",
    "utterance.final",
    "translation",
    "confirm.request",
    "confirm.response",
    "tts.chunk",
    "plan.update",
    "status",
    "error",
]


class WSEventEnvelope(BaseModel):
    event_type: EventType
    session_id: str
    payload: Union[
        Utterance,
        TranslationResult,
        ConfirmRequest,
        ConfirmResponse,
        Plan,
        ErrorPayload,
        dict[str, Any],
    ]
