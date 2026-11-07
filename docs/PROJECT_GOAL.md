PROJECT GOAL (save verbatim as docs/PROJECT_GOAL.md)

VoiceBridge is a voice-first mobile web app (PWA) that lets a traveller and a local driver who share no language find each other, talk, plan a day trip together and agree on it. First market: visitors arriving in Chennai, for example a Hindi speaker with a Tamil-speaking driver. The design must extend to more Indian language pairs, with English as a bridge.

Problem: language barriers and unclear commitments (price, hours, waiting charges, stops) cause disputes, drivers' local knowledge goes unused, and many drivers do not type comfortably. Plain translated chat does not fix unclear agreements.

Core experience:
1. The traveller picks a language, describes the trip, browses available drivers (languages, vehicle, rating, verified badge, price range) and requests one.
2. In one WhatsApp-like thread each person speaks in their own language with hold-to-talk, and hears and reads the other person's reply in theirs.
3. Speech pipeline: audio, Gnani Prisma speech-to-text, normalisation and entity extraction, translation (an LLM or IndicTrans2 behind an interface), verification (back-translation of prices, times and places, with the speaker confirming), TTS preparation, Gnani Timbre text-to-speech.
4. A shared plan card (itinerary plus commitments) is edited by either side by voice, validated (travel times, opening hours), confirmed by both people in both languages, then locked as an agreement.
5. Trip mode: location sharing, one-tap quick phrases, rating. Drivers record local tips by voice.

Constraints:
- Hackathon build that must genuinely use Gnani APIs: Prisma (speech-to-text) and Timbre (text-to-speech). Docs: https://docs.gnani.ai/api/introduction/introduction. Gnani's APIs cover speech in and speech out; translation uses a separate model. Evon (Gnani's 30B reasoning model) is optional.
- All drivers, ratings, verification badges and places are sample data and must be labelled as such. No real personal data.
- Modular: every external service sits behind an interface with a mock, so any module can be changed or tested alone.
- Accurate on numbers and commitments. Target about 1.5 seconds speech to speech, streaming between stages.
- UI: very easy for a tired traveller and for a driver in a vehicle. Mobile first, 48px touch targets, voice first, clear states.
