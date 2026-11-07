# Language Module

## Purpose
Provides text normalization and entity extraction across Hindi, Tamil, and English:
1. **Normalizer**:
   - Script detection (Latin, Devanagari, Tamil, mixed).
   - Native-digit to ASCII digit conversion (e.g., Devanagari `०-९` and Tamil `௦-௯` to standard `0-9`).
   - Light handling of code-mixed Hindi-English and Tamil-English.
2. **Entity Tagger**:
   - Rule-based extraction of `money`, `duration`, `time`, `place`, `count`, and `vehicle_term`.
   - Spoken number word recognition, including Indian numbering units (`lakh`, `crore`, `ரூபாய்`, `ரொக்கம்`, `रुपये`).
   - Optional fallback interface for LLM-based entity extraction.
3. **Glossary Loader**:
   - Loads versioned YAML glossary of Chennai places and taxi terms with schema validation.

## How to Test
Run `pytest modules/language/tests` (over 40 table-driven test cases across Hindi, Tamil, and English).
