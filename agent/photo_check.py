"""Crop photo check: Strands Decider 2B reads the photo (the LLM never sees it).

One request, one image, two questions: is it a crop leaf photo at all, and what does the leaf
look like. The tips are fixed text per condition (English and Tamil), so they never invent a
disease or a product.
"""

from __future__ import annotations

from typing import Any

from decider_kit import Decider

from .i18n import PHOTO_LABELS, PHOTO_TIPS, t
from .tools import both

PHOTO_QUESTIONS = {
    "is_crop_photo": Decider.noul(
        "Does this photo clearly show a crop plant or a plant leaf?",
        {"true": "a plant, crop or leaf fills a good part of the photo",
         "false": "a person, a cartoon, an object, a screenshot, a blank or blurry image, or anything that is not a plant"}),
    "condition": Decider.choice(
        "What does the leaf or plant in the photo look like?",
        {"healthy": "green, even colour, no spots or holes",
         "yellowing": "leaves turning yellow or pale",
         "spots": "brown, black or rust-coloured spots or patches",
         "pest_damage": "holes, chewed edges, insects, webbing or eggs",
         "wilting": "dry, curled, drooping or brown dried leaves"}),
}


def check_photo(decider: Decider, image: Any, crop: str | None = None) -> tuple[dict[str, Any], dict[str, Any]]:
    """-> (card for the UI, decision record for the panel)."""
    a = decider.ask(f"A farmer{' growing ' + crop if crop else ''} sent this photo to a farm advice app.",
                    PHOTO_QUESTIONS, images=[image])
    is_leaf = a["is_crop_photo"].p_yes or 0.0
    cond = a["condition"].label
    conf = a["condition"].confidence
    if cond not in PHOTO_TIPS["en"]:  # an unexpected answer: treat as unsure, never crash
        cond, conf = "healthy", 0.0
    rec = {"pattern": "#guardrails", "stage": "photo", "is_crop_photo": round(is_leaf, 3),
           "condition_confidence": round(conf, 3), "condition": cond,
           "verdict": "proceed" if is_leaf >= 0.5 else "guide", "decider_ms": round(decider.last_latency_ms or 0)}
    if is_leaf < 0.5:
        card = {"type": "photo", "ok": False, "title": both(lambda lg: t(lg, "photo.bad")),
                "tips": both(lambda lg: [t(lg, "photo.bad.tip")])}
    elif conf < 0.5:
        card = {"type": "photo", "ok": True, "condition": cond, "confidence": round(conf, 2),
                "title": both(lambda lg: t(lg, "photo.unsure")), "tips": both(lambda lg: PHOTO_TIPS[lg][cond][:1])}
    else:
        card = {"type": "photo", "ok": True, "condition": cond, "confidence": round(conf, 2),
                "title": both(lambda lg: t(lg, "photo.healthy") if cond == "healthy"
                              else t(lg, "photo.issue", label=PHOTO_LABELS[lg][cond])),
                "tips": both(lambda lg: PHOTO_TIPS[lg][cond])}
    return card, rec
