from contracts.models import EntityType
from language.normalizer import (
    clean_code_mixed_text,
    convert_native_digits_to_ascii,
    detect_script,
)
from language.tagger import tag_entities

# Table-driven test cases (40+ assertions across 3 languages)
SCRIPT_CASES = [
    ("வணக்கம்", "tamil"),
    ("மெரினா கடற்கரை", "tamil"),
    ("नमस्ते भारत", "devanagari"),
    ("मरीना बीच", "devanagari"),
    ("Marina Beach Chennai", "latin"),
    ("Auto stand nearby", "latin"),
    ("வணக்கம் sir auto வருமா", "mixed"),
    ("Hello भाई how much", "mixed"),
]


def test_script_detection():
    for text, expected in SCRIPT_CASES:
        assert detect_script(text) == expected, f"Failed script detection for {text}"


DIGIT_CASES = [
    ("₹५००", "₹500"),
    ("ஆட்டோ ௨௦௦ ரூபாய்", "ஆட்டோ 200 ரூபாய்"),
    ("किराया १००० रुपये", "किराया 1000 रुपये"),
    ("சென்னை ௧௨௩", "சென்னை 123"),
]


def test_digit_normalization():
    for text, expected in DIGIT_CASES:
        assert convert_native_digits_to_ascii(text) == expected


ENTITY_CASES = [
    # Money
    ("Price is ₹500", EntityType.MONEY),
    ("Take Rs. 1000", EntityType.MONEY),
    ("That will be 300 rupees", EntityType.MONEY),
    ("கட்டணம் ₹500", EntityType.MONEY),
    ("ஆட்டோ 500 ரூபாய்", EntityType.MONEY),
    ("किराया 500 रुपये", EntityType.MONEY),
    ("₹1000", EntityType.MONEY),
    ("2 lakh rupees", EntityType.MONEY),
    # Duration
    ("Wait for 30 minutes", EntityType.DURATION),
    ("Trip is 2 hours", EntityType.DURATION),
    ("3 மணி நேரம் ஆகும்", EntityType.DURATION),
    ("2 घंटे लगेंगे", EntityType.DURATION),
    ("Wait 1 hr", EntityType.DURATION),
    # Time
    ("Pickup at 5 pm", EntityType.TIME),
    ("Flight at 10:30 am", EntityType.TIME),
    ("Morning 9 am", EntityType.TIME),
    # Count
    ("We are 3 passengers", EntityType.COUNT),
    ("Book for 4 people", EntityType.COUNT),
    ("2 பேர் வருகிறோம்", EntityType.COUNT),
    ("4 लोग हैं", EntityType.COUNT),
    # Vehicle terms
    ("I need an auto", EntityType.VEHICLE_TERM),
    ("Book a taxi", EntityType.VEHICLE_TERM),
    ("ஆட்டோ எங்கே கிடைக்கும்", EntityType.VEHICLE_TERM),
    ("टैक्सी चाहिए", EntityType.VEHICLE_TERM),
    # Places
    ("Drop me at Marina Beach", EntityType.PLACE),
    ("Go to Central Station", EntityType.PLACE),
    ("Airport jao", EntityType.PLACE),
    ("மெரினா கடற்கரை போகணும்", EntityType.PLACE),
    ("சென்னை சென்ட்ரல்", EntityType.PLACE),
    ("मरीना बीच", EntityType.PLACE),
]


def test_entity_tagging_table():
    for text, expected_type in ENTITY_CASES:
        entities = tag_entities(text)
        types = [e.type for e in entities]
        assert expected_type in types, f"Expected {expected_type} in {text}, got {types}"


def test_clean_code_mixed_text():
    raw = "  ஆட்டோ  ௨௦௦   ரூபாய் \n"
    cleaned = clean_code_mixed_text(raw)
    assert cleaned == "ஆட்டோ 200 ரூபாய்"
