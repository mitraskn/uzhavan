# Uzhavan: Smart Farm Weather Advisor for Tamil Nadu

A farm advice app that turns **real weather data** into clear answers for Tamil Nadu farmers, in **Tamil or English**, by tapping, typing or speaking. It never guesses whose farm it is advising: before any advice, **Strands Decider 2B** checks that the district and the crop are really known.

Built for the AWS Builder Center **Agent Experience Hackathon: Strands Decider** (AWS User Group Madurai). Tags: `#strands-decider-2b` `#guardrails`

---

## Try It

| | Link |
|---|---|
| **Live app** (open it on your phone) | https://kzxepqk3sve5r2yh2yt3a6vyzm0mnnyv.lambda-url.ap-southeast-2.on.aws/ |
| **Demo video** (2:44) | https://youtu.be/flmXWHHdwiI |
| **Article** (AWS Builder Center) | https://builder.aws.com/content/3L12jzePSALHLBWlQqwULrCP5uo/uzhavan-real-weather-advice-for-tamil-nadu-farmers-in-tamil-and-english-with-a-strands-decider-2b-guardrail-that-asks-instead-of-guessing |
| **Agent on AWS** | Amazon Bedrock AgentCore Runtime, ap-southeast-2 |

> The live app allows 30 questions per hour per device, to keep the cost low. The first answer can take about 20 seconds while AWS starts up.

---

## Overview

Farmers decide every day whether to spray, water, sow or harvest, and the weather decides whether that work is wasted. A spray washed off by rain the next morning costs money and a day's labour.

Uzhavan answers these questions with numbers from the **Open-Meteo** forecast (rain, wind, humidity, soil moisture, sunshine and crop water use) for any of the **38 districts of Tamil Nadu**. Every answer is a traffic-light card (GREEN / YELLOW / RED) with the reason and the best time to do the work.

The key problem with AI assistants here: if a farmer asks *"Can I spray today?"* without saying where the farm is, a normal LLM fills in a district and answers confidently. That advice is about someone else's field. Uzhavan hands that decision to Strands Decider 2B, so it **asks instead of guessing**.

---

## Approach

1. **Check first (Strands Decider 2B).** One request per farmer message answers four typed questions: what kind of message it is (request / greeting / off-topic / an attempt to change the rules), whether it is about farming, and whether the **district** and the **crop** are really known (said, selected or saved) or would be guessed.
2. **Act on the answer.** Missing fact: ask the farmer. Unsure: ask to confirm. A value the AI invented: replaced with the farmer's value, and the correction is shown on the card. Clear rule-breaking trick: refused before the LLM sees it. Off-topic: polite redirect.
3. **Compute the advice with fixed rules.** The 15 tools compute the advice in Python from the forecast numbers (for example, a safe spray window needs 4 dry, calm daylight hours). The numbers are real, not generated.
4. **Talk with Amazon Bedrock.** Amazon Nova Pro, through a Strands Agent, understands typed and spoken questions and picks the right tool.

---

## Features

| Group | Tools |
|---|---|
| Weather | Rain this week, Past rain (7 days), Storm and lightning safety |
| Field work | Spraying (safe hourly window), Fertilizer timing, Sowing, Ploughing, Harvest, Sun-drying produce |
| Water | Watering (rain vs crop water use + soil moisture), Drainage |
| Health | Fungal disease risk, Heat stress, Cattle heat stress (THI) |
| Plan | My week (a day-by-day farm plan) |

- **One language at a time:** Tamil or English, including Tanglish typing (*"Thanjavur la mazhai varuma?"*)
- **Big Tap and speak button**, answers read aloud (for farmers who cannot read)
- **Your farm:** pick on the map, from the list, or with "Use my location"; remembered on the phone
- **Heavy-rain alert banner** (IMD heavy rain: 64.5 mm or more in a day, or wind above 40 km/h)
- **Crop photo check** read by Strands Decider 2B (is it a leaf, and what does it look like)
- **"Decider checked" line on every card**, and a **Decider page** with live statistics

---

## Decision Pattern: Never-Guess Guardrail (`#guardrails`)

The reusable pattern lives in [`agent/grounded_guard.py`](agent/grounded_guard.py) (labelled `REUSABLE DECISION PATTERN`), set up for farming in [`agent/farm_guard.py`](agent/farm_guard.py). The same guard works in other domains: see [`examples/clinic_guard.py`](examples/clinic_guard.py) for a clinic booking agent.

```python
FACTS = {"district": "the farm's district in Tamil Nadu", "crop": "the crop the farmer grows"}
SCOPE = "farming, crops, livestock, pests, spraying, watering or weather"
QUESTIONS = build_questions(FACTS, SCOPE)
# message_kind (choice), in_scope (yes/no), district_grounded (yes/no), crop_grounded (yes/no)
# = 4 questions, one Decider request per message
```

To reuse it in your own agent: list the facts your tools must never guess, say which tools need which facts, and describe your assistant's scope. An optional `glossary` spells out local words for the Decider (*'nellu' = paddy (a crop)*), which helps mixed-language users.

---

## Model Comparison

Strands Decider 2B against Amazon Nova Pro (Bedrock), asked the same typed questions on 40 labelled cases (95 decisions).

| | Strands Decider 2B | Amazon Nova Pro |
|---|---|---|
| Accuracy | 90.5% | 94.7% |
| **Accuracy when confident** | **100%** | 94.7% |
| Latency (median per decision) | 4085 ms | 2840 ms |
| **Cost per 1,000 decisions** | **$0.035** | $0.557 |

> **Why the Decider:** this check runs on **every message**, so cost matters: the Decider is about **16x cheaper**. When it was confident it was right every time, and when it is unsure the app asks the farmer, so a lower raw score never becomes wrong advice. Its latency includes the internet round trip to the free shared hosted API. The test set is small (40 cases), so I stopped tuning the wording once the numbers were honest, to avoid fitting the test set.

### Results by Language

| Language | Decisions | Before word help | After word help |
|---|---|---|---|
| English | 55 | 93% | **98%** |
| Tanglish | 22 | 68% | **77%** |
| Tamil script | 18 | 89% | 83% |

Reproduce: `.\kit.cmd bench` and `python scripts/bench_by_language.py` (cases in `agent/eval_cases.jsonl`).

---

## Tools and Libraries Used

| Category | Used |
|---|---|
| Language | Python 3.12, JavaScript (single-page web app) |
| Decision model | Strands Decider 2B (AWS User Group Madurai hosted API) |
| LLM | Amazon Bedrock, Amazon Nova Pro |
| Agent framework | Strands Agents SDK (tools, interventions) |
| Hosting | Amazon Bedrock AgentCore Runtime (agent), AWS Lambda Function URL (public web app) |
| Data | Open-Meteo forecast API (weather, soil moisture, crop water use) |
| Web | FastAPI, Leaflet + OpenStreetMap, Web Speech API, gTTS (Tamil voice) |
| Testing | pytest (80 offline tests) |

---

## Installation

```bash
git clone https://github.com/mitraskn/uzhavan
cd uzhavan
./kit setup          # Windows: .\kit.cmd setup   (Python, AWS keys, Strands Decider)
./kit demo           # the app at http://localhost:8501
./kit test           # offline tests
./kit deploy         # the agent on Amazon Bedrock AgentCore Runtime
python scripts/deploy_web.py   # the public web link on AWS Lambda
```

Requirements: Python 3.10+, an AWS account with Amazon Bedrock access, a Strands Decider key, and Node 20+ for deploying.

### Project Structure

| Path | What it is |
|---|---|
| `agent/agent.py` | The agent: one Decider check per message, then tools or the LLM |
| `agent/grounded_guard.py` | The reusable never-guess guardrail |
| `agent/farm_guard.py` | The guard set up for farming (facts, scope, Tanglish glossary) |
| `agent/tools.py` | The 15 farm tools and the weather rules |
| `agent/i18n.py`, `agent/i18n_tools.py` | English and Tamil text |
| `demo/static/index.html` | The web app (Home and Decider pages) |
| `deploy/web/lambda_app.py` | The public web app on AWS Lambda |

---

## Author

**Mitra Sreekandan** (team Byte Solo), Computer Science and Engineering, Sri Krishna College of Technology, Coimbatore
GitHub: [mitraskn](https://github.com/mitraskn)

Built with Kiro and AI coding assistants.

---

## Credits

Built with the AWS User Group Madurai Strands Decider hackathon kit (https://github.com/awsugmdu). The kit's library (`decider_kit/`, the video and article tooling, the Kiro steering and skills) is the user group's; the agent in `agent/` and the app in `demo/static/` are mine. Weather data: [Open-Meteo](https://open-meteo.com) (CC BY 4.0). Map: OpenStreetMap contributors. Strands Decider: https://github.com/strands-labs/strands-decider (Apache-2.0).

Advice is based on weather forecasts. For crop diseases, consult your local agriculture officer.

Licence: Apache-2.0 (see LICENSE).
