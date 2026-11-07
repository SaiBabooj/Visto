# Verification Layer

## Purpose
Prevents misunderstandings and disputes regarding money, times, durations, and places through:
1. **Risk Classifier**: Utterances containing money, time, duration, count, or place entities are classified as `RiskLevel.COMMITMENT`; otherwise `RiskLevel.LOW`.
2. **Back-Translation**: Uses `Translator` to translate target output back into speaker's original language.
3. **Entity & Text Comparison**: Verifies entity equality and lexical similarity.
4. **Confirm State Machine**:
   - Manages state transitions: `PENDING` -> `CONFIRMED`, `REJECTED`, `EDITED`, or `EXPIRED`.
   - Generates a `ConfirmRequest` containing the back-translation in speaker's own language.
   - Strict invariant: A commitment without confirmation is **never** marked deliverable.

## How to Test
Run `pytest modules/verify/tests`.
