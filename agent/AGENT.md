# Use case

- **Pitch:** Uzhavan turns real weather into clear farm advice for Tamil Nadu farmers, in Tamil or English, and never guesses whose farm it is advising: Strands Decider 2B checks that first.
- **Who it is for:** small farmers in Tamil Nadu, including those who cannot read (big Tap & speak
  button, answers read aloud).
- **Features:**
  - 15 tools from real Open-Meteo data (forecast, past 7 days, soil moisture, humidity, sunshine,
    crop water use): rain this week, past rain, storm and lightning safety, spraying (safe hourly
    window), fertilizer timing, sowing, ploughing, harvest, sun-drying produce, watering (rain vs crop
    water use), drainage, fungal disease risk, heat stress, cattle heat stress (THI), weekly plan;
  - traffic-light cards (GREEN / YELLOW / RED) with the numbers behind them and the best time;
  - a "Decider checked" line on every card, and a visible correction when the AI guessed a value;
  - one language at a time (Tamil or English), voice in and out;
  - your farm: map, district list or "Use my location", crop buttons, remembered on the phone;
  - heavy-rain / strong-wind alert banner (IMD heavy rain: 64.5 mm or more in a day);
  - crop photo check read by Strands Decider 2B;
  - a Decider page with live statistics (checks, guesses corrected, asked instead of guessing,
    tricks blocked, median Decider time).
- **The decision handed to Strands Decider 2B (`#guardrails`):** one request per farmer message,
  four typed questions: what kind of message is it (request / greeting / off-topic / an attempt to
  change the rules), is it in scope, and are the district and the crop really known (said, selected
  or saved) or would they be guessed. Before any tool runs: missing -> ask, unsure -> confirm, a
  value the AI invented -> replaced by the farmer's value and shown. Reusable pattern:
  `agent/grounded_guard.py` (second-domain example: `examples/clinic_guard.py`).
- **Why a decision model:** this check runs on every message, so it must be fast and cheap, and it
  returns calibrated scores the code branches on (proceed / confirm / ask / deny).
- **Mixed language:** an optional `glossary` spells out local words for the decider ("'nellu' =
  paddy (a crop)"); Tanglish accuracy went from 68% to 77% with it (see Measured).
- **Amazon Bedrock:** the conversation and tool choice for typed and spoken questions, through a
  Strands Agent. The advice itself is computed from the data with fixed rules, so the numbers are real.
