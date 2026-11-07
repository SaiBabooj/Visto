from tts_prep.prep import (
    apply_place_glossary,
    normalize_currency_and_numbers,
    number_to_words,
    prepare_for_tts,
    split_sentences,
)

# Table-driven test cases (30+ cases)
NUMBER_CASES = [
    # English
    (0, "en", "zero"),
    (1, "en", "one"),
    (5, "en", "five"),
    (10, "en", "ten"),
    (25, "en", "twenty-five"),
    (50, "en", "fifty"),
    (100, "en", "hundred"),
    (500, "en", "five hundred"),
    (1000, "en", "thousand"),
    # Tamil
    (0, "ta", "பூஜ்ஜியம்"),
    (1, "ta", "ஒன்று"),
    (5, "ta", "ஐந்து"),
    (10, "ta", "பத்து"),
    (25, "ta", "இருபது ஐந்து"),
    (50, "ta", "ஐம்பது"),
    (100, "ta", "நூறு"),
    (500, "ta", "ஐந்நூறு"),
    (1000, "ta", "ஆயிரம்"),
    # Hindi
    (0, "hi", "शून्य"),
    (1, "hi", "एक"),
    (5, "hi", "पाँच"),
    (10, "hi", "दस"),
    (25, "hi", "बीस पाँच"),
    (50, "hi", "पचास"),
    (100, "hi", "सौ"),
    (500, "hi", "पाँच सौ"),
    (1000, "hi", "हज़ार"),
]


def test_number_to_words_table():
    for num, lang, expected in NUMBER_CASES:
        assert number_to_words(num, lang) == expected, f"Failed for {num} in {lang}"


CURRENCY_CASES = [
    ("Fare is ₹500", "en", "Fare is five hundred rupees"),
    ("Fare is Rs. 100", "en", "Fare is hundred rupees"),
    ("கட்டணம் ₹500", "ta", "கட்டணம் ஐந்நூறு ரூபாய்"),
    ("கட்டணம் Rs 1000", "ta", "கட்டணம் ஆயிரம் ரூபாய்"),
    ("किराया ₹500", "hi", "किराया पाँच सौ रुपये"),
    ("किराया INR 100", "hi", "किराया सौ रुपये"),
]


def test_currency_normalization_table():
    for inp, lang, expected in CURRENCY_CASES:
        assert normalize_currency_and_numbers(inp, lang) == expected


GLOSSARY_CASES = [
    ("Let us go to Marina Beach", "ta", "Let us go to மெரினா கடற்கரை"),
    ("Drop me at Central Station", "ta", "டிராப் me at சென்ட்ரல் ரயில் நிலையம்"),
    ("Marina Beach chalte hain", "hi", "मरीना बीच chalte hain"),
    ("Charge includes waiting charge and toll", "ta", "Charge includes காத்திருப்பு கட்டணம் and டோல்"),
]


def test_glossary_substitution_table():
    for inp, lang, expected in GLOSSARY_CASES:
        assert apply_place_glossary(inp, lang) == expected


def test_sentence_splitting():
    text = "Hello sir! Where do you want to go? We can visit Marina Beach. Let's go."
    splits = split_sentences(text)
    assert len(splits) == 4
    assert splits[0] == "Hello sir!"
    assert splits[1] == "Where do you want to go?"
    assert splits[2] == "We can visit Marina Beach."
    assert splits[3] == "Let's go."


def test_prepare_for_tts_pipeline():
    text = "Welcome to Chennai! The fare to Marina Beach is ₹500. Have a nice trip."
    res = prepare_for_tts(text, "en")
    assert len(res) == 3
    assert "five hundred rupees" in res[1]
