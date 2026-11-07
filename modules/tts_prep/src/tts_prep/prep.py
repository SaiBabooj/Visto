import re
from pathlib import Path
from typing import Dict, List, Optional

import yaml

# Basic spoken number dictionaries
EN_NUMS = {
    0: "zero", 1: "one", 2: "two", 3: "three", 4: "four",
    5: "five", 6: "six", 7: "seven", 8: "eight", 9: "nine",
    10: "ten", 20: "twenty", 30: "thirty", 40: "forty",
    50: "fifty", 100: "hundred", 500: "five hundred", 1000: "thousand",
}

TA_NUMS = {
    0: "பூஜ்ஜியம்", 1: "ஒன்று", 2: "இரண்டு", 3: "மூன்று", 4: "நான்கு",
    5: "ஐந்து", 6: "ஆறு", 7: "ஏழு", 8: "எட்டு", 9: "ஒன்பது",
    10: "பத்து", 20: "இருபது", 30: "முப்பது", 40: "நாற்பது",
    50: "ஐம்பது", 100: "நூறு", 500: "ஐந்நூறு", 1000: "ஆயிரம்",
}

HI_NUMS = {
    0: "शून्य", 1: "एक", 2: "दो", 3: "तीन", 4: "चार",
    5: "पाँच", 6: "छह", 7: "सात", 8: "आठ", 9: "नौ",
    10: "दस", 20: "बीस", 30: "तीस", 40: "चालीस",
    50: "पचास", 100: "सौ", 500: "पाँच सौ", 1000: "हज़ार",
}


def number_to_words(num: int, lang: str) -> str:
    """Converts common numbers to spoken words for speech engines."""
    lang_code = lang.split("-")[0].lower()
    table = TA_NUMS if lang_code == "ta" else (HI_NUMS if lang_code == "hi" else EN_NUMS)
    if num in table:
        return table[num]
    if num < 100:
        tens = (num // 10) * 10
        ones = num % 10
        if tens in table and ones in table:
            sep = " " if lang_code != "en" else "-"
            return f"{table[tens]}{sep}{table[ones]}"
    return str(num)


def load_chennai_glossary(config_path: Optional[str] = None) -> Dict[str, Dict[str, str]]:
    """Loads Chennai landmarks and taxi terms glossary."""
    if config_path is None:
        base_dir = Path(__file__).resolve().parents[4]
        config_file = base_dir / "config" / "chennai_places_glossary.yaml"
    else:
        config_file = Path(config_path)

    if not config_file.exists():
        return {}

    with open(config_file, "r", encoding="utf-8") as f:
        data = yaml.safe_load(f)
        return data.get("glossary", {})


def normalize_currency_and_numbers(text: str, lang: str) -> str:
    """Replaces currency symbols and raw numbers with natural spoken representations."""
    lang_code = lang.split("-")[0].lower()
    currency_word = "ரூபாய்" if lang_code == "ta" else ("रुपये" if lang_code == "hi" else "rupees")

    # Replace ₹500 or Rs. 500 or INR 500
    pattern_currency = re.compile(r"(?:₹|Rs\.?|INR)\s*(\d+)", re.IGNORECASE)

    def replace_currency(match):
        val = int(match.group(1))
        words = number_to_words(val, lang)
        return f"{words} {currency_word}"

    result = pattern_currency.sub(replace_currency, text)

    # Replace standalone numbers up to 1000
    pattern_nums = re.compile(r"\b(\d+)\b")

    def replace_num(match):
        val = int(match.group(1))
        return number_to_words(val, lang)

    return pattern_nums.sub(replace_num, result)


def apply_place_glossary(
    text: str, lang: str, glossary: Optional[Dict[str, Dict[str, str]]] = None
) -> str:
    """Substitutes Chennai place names and taxi terms into target language script."""
    if glossary is None:
        glossary = load_chennai_glossary()

    lang_code = lang.split("-")[0].lower()
    result = text

    for term, translations in glossary.items():
        if lang_code in translations:
            pattern = re.compile(rf"\b{re.escape(term)}\b", re.IGNORECASE)
            result = pattern.sub(translations[lang_code], result)

    return result


def split_sentences(text: str) -> List[str]:
    """Splits text into sentences so streaming speech synthesis can begin immediately."""
    sentences = re.split(r"(?<=[.!?।])\s+", text.strip())
    return [s.strip() for s in sentences if s.strip()]


def prepare_for_tts(
    text: str, lang: str, glossary: Optional[Dict[str, Dict[str, str]]] = None
) -> List[str]:
    """Complete TTS preparation pipeline:
    normalizes numbers, applies glossary, splits into sentences.
    """
    normalized = normalize_currency_and_numbers(text, lang)
    transliterated = apply_place_glossary(normalized, lang, glossary)
    return split_sentences(transliterated)
