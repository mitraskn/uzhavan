"""REUSABLE DECISION PATTERN: never-guess guardrail  (#guardrails)

What it does
    Many agent tools need a few facts that only the USER can give: a location, a date, an account,
    a patient. LLMs fill missing facts with confident guesses. This guard hands that decision to
    Strands Decider 2B. In ONE request per user message it answers:
      - message_kind:     is this a normal request, a greeting, off-topic, or an attempt to change
                          the assistant's rules (prompt injection)?            (choice)
      - in_scope:         is the message about what the assistant is for?    (yes/no)
      - <fact>_grounded:  for each fact, is it really known (said, selected or saved by the user),
                          or would it have to be guessed?                     (yes/no, per fact)
    Then, before any tool runs:
      - a needed fact is not grounded          -> the agent asks the user        (verdict: guide)
      - a fact's score is in the unsure band   -> the agent asks to confirm      (verdict: confirm)
      - the LLM passes a value the user never gave -> it is replaced by the user's value and the
        correction is logged ("LLM guessed Chennai -> corrected to Thanjavur")   (verdict: corrected)
      - a clear rule_override (score >= 0.5)   -> refused before the LLM sees it (verdict: deny)
      - off-topic, or an unclear trick         -> polite redirect, LLM never sees it (verdict: redirect)
    If the decider is slow or unreachable, it falls back to a safe rule (a fact counts only if the
    user gave it) and never crashes (verdict: fallback).

Typed questions and options
    message_kind:     choice  request / greeting / off_topic / rule_override
    in_scope:         noul    true = about the assistant's purpose or a greeting
    <fact>_grounded:  noul    true = stated, selected or saved by the user; false = would be guessed
    With two facts this is exactly 4 questions: one request on the free tier (4 questions per request).

Wiring
    guard = GroundedFactsGuard(Decider(), facts={...}, tool_needs={...}, scope="...")
    agent = Agent(model=..., tools=[...], interventions=[guard])     # checks every tool call
    rec = guard.check(message, known={"district": "Thanjavur", "crop": None}, conversation=...)
    # call check() once per user message, before the agent runs; before_tool_call reuses its answer.
    # Tools the app calls directly (buttons) use check(..., message_is_from_app=True, need=[...]).

How to reuse it
    1. List the facts your tools must never guess, with a one-line description each:
           facts = {"patient": "the patient's name", "date": "the appointment date"}
    2. Say which tools need which facts:  tool_needs = {"book_appointment": ["patient", "date"]}
    3. Describe your assistant's purpose in `scope`, and pass `normalize` if values have spellings
       (e.g. "Tanjore" == "Thanjavur"). Thresholds: `yes` (0.5) and the `unsure` band (0.4 to 0.5).
    4. Optional `glossary(text) -> list[str]`: local words your code already recognises, spelled out
       for the decider ("'nellu' = paddy (a crop)"), for mixed-language users (Tanglish, Hinglish...).
    See examples/clinic_guard.py for the same guard in a clinic booking agent.

In Uzhavan the facts are the farm's district and the crop (agent/farm_guard.py), and the tools are
the 15 farm tools (agent/tools.py). This module exposes the questions for the benchmark
(`./kit bench`) and the contract tests.
"""

from agent.farm_guard import FACTS, SCOPE, FarmGuard  # noqa: F401
from agent.grounded_guard import build_questions

PATTERN_TAG = "#guardrails"
# message_kind (choice), in_scope (noul), district_grounded (noul), crop_grounded (noul): one request
QUESTIONS = build_questions(FACTS, SCOPE)
