# TTS Prep Module

## Purpose
A pure function text preparation pipeline that converts raw translated strings into spoken-optimized text before passing to the Text-to-Speech engine:
- Converts numeric digits and currency tokens into spoken words across English, Tamil, and Hindi.
- Applies transliteration glossary for Chennai places and auto/cab terms.
- Performs sentence boundary splitting to allow streaming speech synthesis to begin on the first ready sentence.

## Testing
Comprehensive table-driven test cases (30+ assertions) testing number pronunciation, currency normalization, glossary substitution, and sentence splitting.
