"""Uzhavan: Smart Farm Weather Advisor for Tamil Nadu farmers.

15 farm tools turn real weather (Open-Meteo: forecast, past rain, soil moisture, humidity, sunshine)
into clear advice cards, in Tamil or English. Strands Decider 2B is the guardrail: ONE request per
message checks the message (injection, off-topic) and whether the district and crop are really
known; before any tool runs, a value the farmer never gave is asked for or corrected, never guessed.
The LLM (Amazon Bedrock, through a Strands Agent) handles typed and spoken questions and picks the tool.

    from agent.agent import HackathonAgent
    out = HackathonAgent().chat("Can I spray today?", district="Thanjavur", crop="Paddy", lang="ta")
    out["reply"], out["reply_i18n"], out["cards"], out["decisions"]

Tool buttons send `intent` (see tools.REGISTRY): the app calls the tool directly (no LLM needed to
choose it), after the same Decider check.
"""

from __future__ import annotations

import os
import re
import time
from typing import Any

from strands import Agent

from decider_kit import Decider
from decider_kit.llm import agent_model, default_model_id, strip_thinking

from .farm_guard import TOOL_NEEDS, FarmGuard, conversation_text
from .i18n import crop_name, district_name, lang_of, t
from .photo_check import check_photo
from .tools import (CARDS, REGISTRY, TOOLS, WeatherError, alert_for, both, find_mentions, is_tamil, norm_crop,
                    norm_district, summary)

NAME = "Uzhavan: Smart Farm Weather Advisor"

SYSTEM_PROMPT = """You are Uzhavan, a farm weather advisor for farmers in Tamil Nadu.
The farmer may write in English, Tanglish (Tamil in English letters) or Tamil script.
- For questions about weather, rain, spraying, fertilizer, sowing, ploughing, harvest, drying produce, watering,
  drainage, crop disease, heat or cattle, call the matching tool. Never answer those from memory.
- The tool result is shown to the farmer as a card, so keep your own words to one short sentence.
- If a tool tells you to ask the farmer something, ask exactly that.
- Never invent phone numbers, helplines, websites, schemes, organisations, chemicals or doses. No disclaimers.
- Always answer in this exact format, two lines:
EN: <one short sentence in simple English>
TA: <the same sentence in simple Tamil script>"""


def split_bilingual(text: str) -> dict[str, str]:
    """'EN: ...\\nTA: ...' -> {"en": ..., "ta": ...}; plain text goes to both."""
    en = re.search(r"EN:\s*(.+?)(?=\n\s*TA:|$)", text, re.S)
    ta = re.search(r"TA:\s*(.+)$", text, re.S)
    if en or ta:
        e, tt = (en.group(1).strip() if en else ""), (ta.group(1).strip() if ta else "")
        return {"en": e or tt, "ta": tt or e}
    return {"en": text, "ta": text}


class HackathonAgent:
    def __init__(self, decider: Decider | None = None, model_id: str | None = None, eager: bool | None = None):
        self.decider = decider or Decider()
        self.eager = eager if eager is not None else os.environ.get("DEMO_EAGER") == "1"
        self.model_id = model_id or default_model_id()
        self.sessions: dict[str, dict[str, Any]] = {}

    def _session(self, sid: str) -> dict[str, Any]:
        if sid not in self.sessions:
            self.sessions[sid] = {"guard": FarmGuard(self.decider), "agent": None, "district": None, "crop": None,
                                  "src": {}, "history": []}
        return self.sessions[sid]

    def _llm(self, s: dict[str, Any]) -> Agent:
        if s["agent"] is None:
            s["agent"] = Agent(model=agent_model(self.model_id), system_prompt=SYSTEM_PROMPT, tools=TOOLS,
                               interventions=[s["guard"]], callback_handler=None)
        return s["agent"]

    # ---- one turn ------------------------------------------------------------------------------------
    def chat(self, message: str, session_id: str = "default", images: list[Any] | None = None,
             district: str | None = None, crop: str | None = None, intent: str | None = None,
             lang: str | None = None) -> dict[str, Any]:
        t0 = time.perf_counter()
        s = self._session(session_id)
        guard: FarmGuard = s["guard"]
        before = len(guard.log)
        lang = "ta" if is_tamil(message) else lang_of(lang)
        # what the app sends (map, crop buttons, saved profile) wins over old values; what the farmer says wins over both
        if district is not None:
            s["district"], s["src"]["district"] = norm_district(district), "selected"
        if crop is not None:
            s["crop"], s["src"]["crop"] = norm_crop(crop) or (crop.strip().title() or None), "selected"
        said_d, said_c = find_mentions(message)
        if said_d:
            s["district"], s["src"]["district"] = said_d, "said"
        if said_c:
            s["crop"], s["src"]["crop"] = said_c, "said"
        known = {"district": s["district"], "crop": s["crop"]}
        cards: list[dict[str, Any]] = []
        text = message or (REGISTRY[intent][5] if intent in REGISTRY else "")
        conv = conversation_text(s["history"])
        s["history"].append({"role": "user", "content": [{"text": text}]})

        try:
            if images:
                card, rec = check_photo(self.decider, images[0], s["crop"])
                guard.log.append(rec)
                cards.append(card)
                reply = summary(card)
            elif intent in REGISTRY:
                reply = self._button(s, intent, text, known, conv, cards)
            else:
                reply = self._typed(s, text, known, conv, cards, before)
        except WeatherError as e:
            reply = e.text

        s["history"].append({"role": "assistant", "content": [{"text": reply["en"]}]})
        alert = None
        if s["district"]:
            try:
                alert = alert_for(s["district"])
            except WeatherError:
                pass
        return {"reply": reply[lang], "reply_i18n": reply, "lang": lang, "cards": cards, "alert": alert,
                "decisions": guard.log[before:], "profile": {"district": s["district"], "crop": s["crop"]},
                "tool_results": cards, "model_id": self.model_id, "agent": NAME, "eager": self.eager,
                "latency_ms": round((time.perf_counter() - t0) * 1000)}

    def _button(self, s: dict, intent: str, text: str, known: dict, conv: str, cards: list) -> dict[str, str]:
        """A tool button: one Decider check, then the tool itself (fast, no LLM)."""
        tool_name, fn = REGISTRY[intent][0], REGISTRY[intent][1]
        need = TOOL_NEEDS[tool_name]
        rec = s["guard"].check(text, known, conv, need=need, message_is_from_app=True, tool=tool_name)
        if rec["verdict"] in ("guide", "confirm"):
            return self._ask(s, *((rec["missing"][0], "missing") if rec["missing"] else (rec["confirm"][0], "confirm")))
        card = fn(s["district"], s["crop"]) | {"tool": tool_name}
        card["why"] = self._why(s, rec, need)
        cards.append(card)
        return summary(card)

    def _typed(self, s: dict, text: str, known: dict, conv: str, cards: list, before: int) -> dict[str, str]:
        guard: FarmGuard = s["guard"]
        rec = guard.check(text, known, conv)  # the ONE Decider request for this message
        if rec["verdict"] == "deny":
            return both(lambda lg: t(lg, "deny"))
        if rec["verdict"] == "redirect":
            return both(lambda lg: t(lg, "redirect"))
        bucket: list[dict[str, Any]] = []
        token = CARDS.set(bucket)
        try:
            context = (f"[App context: district = {s['district'] or 'not selected'}; "
                       f"crop = {s['crop'] or 'not selected'}]\n\nFarmer says: {text}")
            raw = strip_thinking(str(self._llm(s)(context)))
        finally:
            CARDS.reset(token)
        if bucket:  # the advice card is the answer; its fixed text is reliable in both languages
            card = bucket[-1]
            fixes = [r for r in guard.log[before:] if r.get("stage") == "correction"]
            card["why"] = self._why(s, rec, TOOL_NEEDS.get(card.get("tool"), ["district"]), fixes)
            cards.append(card)
            return summary(card)
        if guard.asked:  # Decider stopped a guess: ask the farmer, in both languages
            return self._ask(s, *guard.asked)
        return split_bilingual(raw.strip() or "Sorry, please ask again.")

    # ---- words for the farmer ---------------------------------------------------------------------------
    def _ask(self, s: dict, fact: str, why: str) -> dict[str, str]:
        if why == "missing":
            return both(lambda lg: t(lg, f"ask.{fact}"))
        if fact == "district":
            return both(lambda lg: t(lg, "confirm.district", district=district_name(s["district"], lg)))
        return both(lambda lg: t(lg, "confirm.crop", crop=crop_name(s["crop"], lg)))

    def _why(self, s: dict, rec: dict, need: list[str], fixes: list[dict] | None = None) -> dict[str, Any]:
        """The 'Why this answer?' line: what Decider checked, where each value came from, and any correction."""
        facts = []
        for f in need:
            v = s[f]
            facts.append({"fact": f, "value": both(lambda lg, v=v, f=f: district_name(v, lg) if f == "district" else crop_name(v, lg)),
                          "src": s["src"].get(f, "selected"), "score": rec.get(f"{f}_grounded")})
        fixed = [{"fact": x["fact"], "guess": x["llm_guess"],
                  "value": both(lambda lg, x=x: district_name(x["fixed_to"], lg) if x["fact"] == "district" else crop_name(x["fixed_to"], lg))}
                 for x in (fixes or [])]
        return {"facts": facts, "fixed": fixed, "fallback": bool(rec.get("fallback")), "decider_ms": rec.get("decider_ms")}


if __name__ == "__main__":
    import json
    import sys

    a = HackathonAgent()
    print(json.dumps(a.chat(" ".join(sys.argv[1:]) or "Will it rain in Thanjavur this week?"), indent=1, ensure_ascii=False))
