/* eslint-disable */
/**
* Auto-generated from packages/contracts JSON Schemas.
* DO NOT EDIT DIRECTLY.
*/

// ================= Agreement =================
export type AgreementId = string;
export type TripId = string;
export type DriverId = string;
/**
 * Agreed fare in INR
 */
export type Price = number;
/**
 * Agreed duration if charter
 */
export type Hours = number | null;
/**
 * Waiting charge per hour
 */
export type WaitingCharge = number | null;
/**
 * Tolls, fuel, etc.
 */
export type Inclusions = string[];
export type ConfirmedByTraveller = boolean;
export type ConfirmedByDriver = boolean;
export type CreatedAt = string;

export interface Agreement {
  agreement_id: AgreementId;
  trip_id: TripId;
  driver_id: DriverId;
  commitment: Commitment;
  confirmed_by_traveller: ConfirmedByTraveller;
  confirmed_by_driver: ConfirmedByDriver;
  created_at: CreatedAt;
  [k: string]: unknown;
}
export interface Commitment {
  price: Price;
  hours?: Hours;
  waiting_charge?: WaitingCharge;
  inclusions?: Inclusions;
  [k: string]: unknown;
}


// ================= Commitment =================
/**
 * Agreed fare in INR
 */
export type Price = number;
/**
 * Agreed duration if charter
 */
export type Hours = number | null;
/**
 * Waiting charge per hour
 */
export type WaitingCharge = number | null;
/**
 * Tolls, fuel, etc.
 */
export type Inclusions = string[];

export interface Commitment {
  price: Price;
  hours?: Hours;
  waiting_charge?: WaitingCharge;
  inclusions?: Inclusions;
  [k: string]: unknown;
}


// ================= ConfirmRequest =================
export type RequestId = string;
export type SummaryText = string;
export type EntityType = "money" | "duration" | "time" | "place" | "count" | "vehicle_term";
export type Value = string;
/**
 * [start_offset, end_offset] within text
 */
export type Span = number[];
export type Entities = Entity[];
export type TargetRole = "traveller" | "driver";

export interface ConfirmRequest {
  request_id: RequestId;
  summary_text: SummaryText;
  entities?: Entities;
  target_role: TargetRole;
  [k: string]: unknown;
}
export interface Entity {
  type: EntityType;
  value: Value;
  span: Span;
  [k: string]: unknown;
}


// ================= ConfirmResponse =================
export type RequestId = string;
export type Confirmed = boolean;
export type Notes = string | null;

export interface ConfirmResponse {
  request_id: RequestId;
  confirmed: Confirmed;
  notes?: Notes;
  [k: string]: unknown;
}


// ================= Driver =================
export type Id = string;
export type Name = string;
export type VehicleNumber = string;
export type VehicleType = string;
export type PhoneNumber = string | null;

export interface Driver {
  id: Id;
  name: Name;
  vehicle_number: VehicleNumber;
  vehicle_type?: VehicleType;
  phone_number?: PhoneNumber;
  [k: string]: unknown;
}


// ================= Entity =================
export type EntityType = "money" | "duration" | "time" | "place" | "count" | "vehicle_term";
export type Value = string;
/**
 * [start_offset, end_offset] within text
 */
export type Span = number[];

export interface Entity {
  type: EntityType;
  value: Value;
  span: Span;
  [k: string]: unknown;
}


// ================= EntityType =================
export type EntityType = "money" | "duration" | "time" | "place" | "count" | "vehicle_term";


// ================= ErrorCode =================
export type ErrorCode =
  | "INVALID_AUDIO_FORMAT"
  | "STT_SERVICE_ERROR"
  | "TTS_SERVICE_ERROR"
  | "TRANSLATION_FAILED"
  | "CONNECTION_LOST"
  | "UNAUTHORIZED"
  | "VALIDATION_ERROR"
  | "INTERNAL_ERROR";


// ================= ErrorPayload =================
export type ErrorCode =
  | "INVALID_AUDIO_FORMAT"
  | "STT_SERVICE_ERROR"
  | "TTS_SERVICE_ERROR"
  | "TRANSLATION_FAILED"
  | "CONNECTION_LOST"
  | "UNAUTHORIZED"
  | "VALIDATION_ERROR"
  | "INTERNAL_ERROR";
export type Message = string;
export type Details = {
  [k: string]: unknown;
} | null;

export interface ErrorPayload {
  code: ErrorCode;
  message: Message;
  details?: Details;
  [k: string]: unknown;
}


// ================= Language =================
export type Code = string;
export type NativeName = string;
export type EnglishName = string;
export type SttSupported = boolean;
export type TtsSupported = boolean;

export interface Language {
  code: Code;
  native_name: NativeName;
  english_name: EnglishName;
  stt_supported?: SttSupported;
  tts_supported?: TtsSupported;
  [k: string]: unknown;
}


// ================= Plan =================
export type TripId = string;
export type StepNumber = number;
export type Title = string;
export type Location = string;
export type EstimatedDurationMinutes = number | null;
export type Items = PlanItem[];
export type EstimatedTotalKm = number | null;

export interface Plan {
  trip_id: TripId;
  items?: Items;
  estimated_total_km?: EstimatedTotalKm;
  [k: string]: unknown;
}
export interface PlanItem {
  step_number: StepNumber;
  title: Title;
  location: Location;
  estimated_duration_minutes?: EstimatedDurationMinutes;
  [k: string]: unknown;
}


// ================= PlanItem =================
export type StepNumber = number;
export type Title = string;
export type Location = string;
export type EstimatedDurationMinutes = number | null;

export interface PlanItem {
  step_number: StepNumber;
  title: Title;
  location: Location;
  estimated_duration_minutes?: EstimatedDurationMinutes;
  [k: string]: unknown;
}


// ================= RiskLevel =================
export type RiskLevel = "low" | "commitment";


// ================= TranslationResult =================
export type UtteranceId = string;
export type SourceLanguage = string;
export type TargetLanguage = string;
export type TranslatedText = string;
export type EntityType = "money" | "duration" | "time" | "place" | "count" | "vehicle_term";
export type Value = string;
/**
 * [start_offset, end_offset] within text
 */
export type Span = number[];
export type Entities = Entity[];
export type RiskLevel = "low" | "commitment";

export interface TranslationResult {
  utterance_id: UtteranceId;
  source_language: SourceLanguage;
  target_language: TargetLanguage;
  translated_text: TranslatedText;
  entities?: Entities;
  risk_level?: RiskLevel;
  [k: string]: unknown;
}
export interface Entity {
  type: EntityType;
  value: Value;
  span: Span;
  [k: string]: unknown;
}


// ================= TripRequest =================
export type Id = string;
export type PickupLocation = string;
export type Destination = string | null;
export type PassengerCount = number;
export type TravellerLanguage = string;
export type DriverLanguage = string;

export interface TripRequest {
  id: Id;
  pickup_location: PickupLocation;
  destination?: Destination;
  passenger_count?: PassengerCount;
  traveller_language?: TravellerLanguage;
  driver_language?: DriverLanguage;
  [k: string]: unknown;
}


// ================= Utterance =================
export type Id = string;
export type Speaker = "traveller" | "driver";
export type Text = string;
export type Language = string;
export type IsFinal = boolean;
export type EntityType = "money" | "duration" | "time" | "place" | "count" | "vehicle_term";
export type Value = string;
/**
 * [start_offset, end_offset] within text
 */
export type Span = number[];
export type Entities = Entity[];

export interface Utterance {
  id: Id;
  speaker: Speaker;
  text: Text;
  language: Language;
  is_final?: IsFinal;
  entities?: Entities;
  [k: string]: unknown;
}
export interface Entity {
  type: EntityType;
  value: Value;
  span: Span;
  [k: string]: unknown;
}


// ================= WSEventEnvelope =================
export type EventType =
  | "audio.start"
  | "audio.chunk"
  | "audio.end"
  | "utterance.partial"
  | "utterance.final"
  | "translation"
  | "confirm.request"
  | "confirm.response"
  | "tts.chunk"
  | "plan.update"
  | "status"
  | "error";
export type SessionId = string;
export type Payload =
  | Utterance
  | TranslationResult
  | ConfirmRequest
  | ConfirmResponse
  | Plan
  | ErrorPayload
  | {
      [k: string]: unknown;
    };
export type Id = string;
export type Speaker = "traveller" | "driver";
export type Text = string;
export type Language = string;
export type IsFinal = boolean;
export type EntityType = "money" | "duration" | "time" | "place" | "count" | "vehicle_term";
export type Value = string;
/**
 * [start_offset, end_offset] within text
 */
export type Span = number[];
export type Entities = Entity[];
export type UtteranceId = string;
export type SourceLanguage = string;
export type TargetLanguage = string;
export type TranslatedText = string;
export type Entities1 = Entity[];
export type RiskLevel = "low" | "commitment";
export type RequestId = string;
export type SummaryText = string;
export type Entities2 = Entity[];
export type TargetRole = "traveller" | "driver";
export type RequestId1 = string;
export type Confirmed = boolean;
export type Notes = string | null;
export type TripId = string;
export type StepNumber = number;
export type Title = string;
export type Location = string;
export type EstimatedDurationMinutes = number | null;
export type Items = PlanItem[];
export type EstimatedTotalKm = number | null;
export type ErrorCode =
  | "INVALID_AUDIO_FORMAT"
  | "STT_SERVICE_ERROR"
  | "TTS_SERVICE_ERROR"
  | "TRANSLATION_FAILED"
  | "CONNECTION_LOST"
  | "UNAUTHORIZED"
  | "VALIDATION_ERROR"
  | "INTERNAL_ERROR";
export type Message = string;
export type Details = {
  [k: string]: unknown;
} | null;

export interface WSEventEnvelope {
  event_type: EventType;
  session_id: SessionId;
  payload: Payload;
  [k: string]: unknown;
}
export interface Utterance {
  id: Id;
  speaker: Speaker;
  text: Text;
  language: Language;
  is_final?: IsFinal;
  entities?: Entities;
  [k: string]: unknown;
}
export interface Entity {
  type: EntityType;
  value: Value;
  span: Span;
  [k: string]: unknown;
}
export interface TranslationResult {
  utterance_id: UtteranceId;
  source_language: SourceLanguage;
  target_language: TargetLanguage;
  translated_text: TranslatedText;
  entities?: Entities1;
  risk_level?: RiskLevel;
  [k: string]: unknown;
}
export interface ConfirmRequest {
  request_id: RequestId;
  summary_text: SummaryText;
  entities?: Entities2;
  target_role: TargetRole;
  [k: string]: unknown;
}
export interface ConfirmResponse {
  request_id: RequestId1;
  confirmed: Confirmed;
  notes?: Notes;
  [k: string]: unknown;
}
export interface Plan {
  trip_id: TripId;
  items?: Items;
  estimated_total_km?: EstimatedTotalKm;
  [k: string]: unknown;
}
export interface PlanItem {
  step_number: StepNumber;
  title: Title;
  location: Location;
  estimated_duration_minutes?: EstimatedDurationMinutes;
  [k: string]: unknown;
}
export interface ErrorPayload {
  code: ErrorCode;
  message: Message;
  details?: Details;
  [k: string]: unknown;
}


