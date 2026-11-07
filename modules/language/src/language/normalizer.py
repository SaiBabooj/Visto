import re
from typing import Literal

# Unicode character block ranges
TAMIL_RANGE = (0x0B80, 0x0BFF)
DEVANAGARI_RANGE = (0x0900, 0x097F)
LATIN_RANGE = (0x0041, 0x007A)

# Digit mappings
DEVANAGARI_DIGITS = str.maketrans("०१२३४५६७८९", "0123456789")
TAMIL_DIGITS = str.maketrans("௦௧௨௩௪௫௬௭௮௯", "0123456789")


def detect_script(text: str) -> Literal["tamil", "devanagari", "latin", "mixed", "unknown"]:
    """Detects predominant script in input text."""
    counts = {"tamil": 0, "devanagari": 0, "latin": 0}

    for char in text:
        cp = ord(char)
        if TAMIL_RANGE[0] <= cp <= TAMIL_RANGE[1]:
            counts["tamil"] += 1
        elif DEVANAGARI_RANGE[0] <= cp <= DEVANAGARI_RANGE[1]:
            counts["devanagari"] += 1
        elif (0x0041 <= cp <= 0x005A) or (0x0061 <= cp <= 0x007A):
            counts["latin"] += 1

    total = sum(counts.values())
    if total == 0:
        return "unknown"

    active_scripts = [s for s, count in counts.items() if count / total > 0.15]
    if len(active_scripts) > 1:
        return "mixed"

    max_script = max(counts, key=counts.get)
    return max_script  # type: ignore


def convert_native_digits_to_ascii(text: str) -> str:
    """Converts native Tamil and Devanagari numerals to standard ASCII numerals."""
    return text.translate(DEVANAGARI_DIGITS).translate(TAMIL_DIGITS)


def clean_code_mixed_text(text: str) -> str:
    """Normalizes whitespaces, removes unwanted control codes, and standardizes punctuation."""
    cleaned = convert_native_digits_to_ascii(text)
    # Collapse multiple spaces
    cleaned = re.sub(r"\s+", " ", cleaned).strip()
    return cleaned
