"""Uzhavan's guard: the reusable never-guess guardrail (agent/grounded_guard.py) set up for farming.

Facts that must come from the farmer: the district and (for crop advice) the crop.
"""

from __future__ import annotations

import re
from typing import Any

from decider_kit import Decider

from .grounded_guard import PATTERN_TAG, GroundedFactsGuard, build_questions, state_text  # noqa: F401
from .tools import REGISTRY, TAMIL_CROPS, TAMIL_DISTRICTS, norm_crop, norm_district

FACTS = {"district": "the farm's district in Tamil Nadu", "crop": "the crop the farmer grows"}
SCOPE = "farming, crops, livestock, pests, spraying, watering or weather"
TOOL_NEEDS = {v[0]: (["district", "crop"] if v[2] else ["district"]) for v in REGISTRY.values()}
QUESTIONS = build_questions(FACTS, SCOPE)


def normalize(fact: str, value: Any) -> Any:
    if not value:
        return None
    return norm_district(value) if fact == "district" else (norm_crop(value) or str(value).strip().title())


# Everyday farm words in Tanglish (Tamil typed in English letters) and Tamil script. A word matches
# when a message word starts with it, so "paichalaama" matches "paichal".
FARM_WORDS = {
    "mazhai": "rain", "mazha": "rain", "thanni": "water", "thanneer": "water", "paichal": "watering the field",
    "uram": "fertilizer", "marundhu": "pesticide", "marunthu": "pesticide", "thelik": "spray", "adikk": "spray",
    "vidhai": "seed or sowing", "vithai": "seed or sowing", "nadavu": "planting", "nadu": "planting",
    "aruvadai": "harvest", "uzhavu": "ploughing", "uzhu": "ploughing", "maadu": "cattle", "maattu": "cattle",
    "veyil": "sunshine", "vepam": "heat", "veppam": "heat", "kaathu": "wind", "kaatru": "wind",
    "idi": "thunder", "minnal": "lightning", "puyal": "cyclone", "vellam": "flood", "vayal": "field",
    "kaaya": "sun-drying produce", "noi": "crop disease", "poochi": "pest", "naalai": "tomorrow",
    "inniki": "today", "indru": "today", "vaaram": "week", "pannalama": "can I do it?",
    "podalam": "can I apply/put?", "varuma": "will it come?", "padam": "movie", "paattu": "song",
    "மழை": "rain", "தண்ணீர்": "water", "பாய்ச்ச": "watering the field", "உரம்": "fertilizer",
    "மருந்து": "pesticide", "தெளி": "spray", "விதை": "seed or sowing", "அறுவடை": "harvest",
    "உழ": "ploughing", "மாடு": "cattle", "வெப்பம்": "heat", "காற்று": "wind", "இடி": "thunder",
    "மின்னல்": "lightning", "புயல்": "cyclone", "வெள்ளம்": "flood", "நோய்": "crop disease", "பூச்சி": "pest",
    "நாளை": "tomorrow", "இன்று": "today", "வாரம்": "week", "படம்": "movie",
}


def glossary(text: str) -> list[str]:
    """Words the app already recognises, spelled out in English for the decider."""
    out: list[str] = []
    seen: set[str] = set()

    def add(word: str, meaning: str) -> None:
        if word.lower() not in seen:
            seen.add(word.lower())
            out.append(f"'{word}' = {meaning}")

    for w in re.findall(r"[A-Za-z]+", text or ""):
        if d := norm_district(w):
            add(w, f"{d} (a district in Tamil Nadu)")
        elif c := norm_crop(w):
            add(w, f"{c.lower()} (a crop)")
        else:
            for k, v in FARM_WORDS.items():
                if k.isascii() and len(w) >= len(k) and w.lower().startswith(k) and (len(k) >= 4 or w.lower() == k):
                    add(w, v)
                    break
    for ta, name in TAMIL_DISTRICTS.items():
        if ta.rstrip("்") in (text or ""):
            add(ta, f"{name} (a district in Tamil Nadu)")
    for ta, name in TAMIL_CROPS.items():
        if ta.rstrip("்") in (text or ""):
            add(ta, f"{name.lower()} (a crop)")
    for k, v in FARM_WORDS.items():
        if not k.isascii() and k in (text or ""):
            add(k, v)
    return out[:10]


def farm_state(message: str, conversation: str, known: dict[str, Any]) -> str:
    """Exactly what FarmGuard sends to the decider (used by the benchmark cases too)."""
    return state_text(message, conversation, known, FACTS, glossary)


class FarmGuard(GroundedFactsGuard):
    name = "farm-guard"

    def __init__(self, decider: Decider, **kw):
        kw.setdefault("glossary", glossary)
        super().__init__(decider, facts=FACTS, tool_needs=TOOL_NEEDS, scope=SCOPE, normalize=normalize, **kw)


def conversation_text(messages: list[dict[str, Any]], last: int = 6) -> str:
    lines = []
    for m in messages[-last:]:
        for block in m.get("content", []) if isinstance(m.get("content"), list) else []:
            if isinstance(block, dict) and isinstance(block.get("text"), str):
                text = block["text"].split("\n\nFarmer says: ")[-1]  # drop our own context prefix
                lines.append(f"{m.get('role', '?')}: {text[:300]}")
    return "\n".join(lines)
