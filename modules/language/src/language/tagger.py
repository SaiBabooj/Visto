import re
from abc import ABC, abstractmethod
from pathlib import Path
from typing import Dict, List, Optional

import yaml
from contracts.models import Entity, EntityType

from language.normalizer import clean_code_mixed_text

# Word-to-number multipliers
INDIAN_NUMBER_WORDS = {
    "lakh": 100_000,
    "lac": 100_000,
    "lakhs": 100_000,
    "लाख": 100_000,
    "இலட்சம்": 100_000,
    "crore": 10_000_000,
    "crores": 10_000_000,
    "करोड़": 10_000_000,
    "கோடி": 10_000_000,
    "thousand": 1_000,
    "हज़ार": 1_000,
    "ஆயிரம்": 1_000,
}

VEHICLE_TERMS = [
    "auto", "cab", "taxi", "rickshaw", "car", "ஆட்டோ", "டாக்ஸி", "கார்", "ऑटो", "टैक्सी", "गाड़ी"
]


class LLMExtractionFallback(ABC):
    """Optional LLM entity extraction fallback interface."""

    @abstractmethod
    async def extract_entities(self, text: str, lang: str) -> List[Entity]:
        pass


def load_chennai_glossary_places() -> Dict[str, List[str]]:
    """Loads Chennai places from glossary config."""
    base_dir = Path(__file__).resolve().parents[4]
    cfg = base_dir / "config" / "chennai_places_glossary.yaml"
    places = []
    if cfg.exists():
        with open(cfg, "r", encoding="utf-8") as f:
            data = yaml.safe_load(f)
            glossary = data.get("glossary", {})
            for k, val in glossary.items():
                places.append(k)
                if isinstance(val, dict):
                    places.extend(val.values())
    return {"places": list(set(places))}


def tag_entities(text: str, fallback_llm: Optional[LLMExtractionFallback] = None) -> List[Entity]:
    """Rule-based entity tagger extracting money, duration, time, count, place, vehicle_term."""
    normalized = clean_code_mixed_text(text)
    entities: List[Entity] = []

    # 1. Money (e.g. ₹500, Rs. 1000, 500 rupees, 500 ரூபாய், 500 रुपये, 2 lakh)
    money_regex = re.compile(
        r"(?:(?:₹|rs\.?|inr)\s*(\d+(?:,\d+)*(?:\.\d+)?)\s*(lakh|crore|thousand|लाख|करोड़|ஆயிரம்)?)|"
        r"(?:(\d+(?:,\d+)*(?:\.\d+)?)\s*(lakh|crore|thousand|लाख|करोड़|ஆயிரம்)?\s*(?:rupees|rupee|bucks|ரூபாய்|ரொக்கம்|रुपये|रुपया))",
        re.IGNORECASE,
    )
    for m in money_regex.finditer(normalized):
        entities.append(Entity(
            type=EntityType.MONEY,
            value=m.group(0).strip(),
            span=[m.start(), m.end()]
        ))

    # 2. Duration (e.g. 2 hours, 30 minutes, 3 மணி நேரம், 2 घंटे)
    duration_regex = re.compile(
        r"(?:^|[^\w])(\d+)\s*(?:hours|hour|hrs|hr|minutes|mins|min|மணி\s*நேரம்|மணி|நிமிடம்|घंटे|घंटा|मिनट)(?:$|[^\w])",
        re.IGNORECASE,
    )
    for m in duration_regex.finditer(normalized):
        entities.append(Entity(
            type=EntityType.DURATION,
            value=m.group(0).strip(),
            span=[m.start(), m.end()]
        ))

    # 3. Time (e.g. 5 pm, 10:30 am, 4:00, 10 am)
    time_regex = re.compile(
        r"\b(\d{1,2}(?::\d{2})?\s*(?:am|pm|a\.m\.|p\.m\.))\b",
        re.IGNORECASE,
    )
    for m in time_regex.finditer(normalized):
        entities.append(Entity(
            type=EntityType.TIME,
            value=m.group(0).strip(),
            span=[m.start(), m.end()]
        ))

    # 4. Vehicle terms
    for term in VEHICLE_TERMS:
        pattern = rf"(?:^|[^\w]){re.escape(term)}(?:$|[^\w])"
        for m in re.finditer(pattern, normalized, re.IGNORECASE):
            entities.append(Entity(
                type=EntityType.VEHICLE_TERM,
                value=term,
                span=[m.start(), m.end()]
            ))

    # 5. Places from Chennai glossary
    places_info = load_chennai_glossary_places()
    for place in places_info.get("places", []):
        if len(place.strip()) < 3:
            continue
        p_pattern = rf"(?:^|[^\w]){re.escape(place)}(?:$|[^\w])"
        for m in re.finditer(p_pattern, normalized, re.IGNORECASE):
            entities.append(Entity(
                type=EntityType.PLACE,
                value=place,
                span=[m.start(), m.end()]
            ))

    # 6. Count (e.g. 3 people, 4 passengers, 2 பேர், 4 लोग)
    count_regex = re.compile(
        r"(?:^|[^\w])(\d+)\s*(?:people|persons|passengers|பேர்|நபர்கள்|लोग|सवारी)(?:$|[^\w])",
        re.IGNORECASE,
    )
    for m in count_regex.finditer(normalized):
        entities.append(Entity(
            type=EntityType.COUNT,
            value=m.group(0).strip(),
            span=[m.start(), m.end()]
        ))

    # Sort entities by start offset and remove duplicates
    entities = sorted(entities, key=lambda e: (e.span[0], e.span[1]))
    unique_entities: List[Entity] = []
    last_end = -1
    for e in entities:
        if e.span[0] >= last_end:
            unique_entities.append(e)
            last_end = e.span[1]

    return unique_entities
