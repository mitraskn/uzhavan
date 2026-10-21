"""Strands Decider 2B accuracy by language (English, Tanglish, Tamil script) on agent/eval_cases.jsonl.

    .\\.venv\\Scripts\\python.exe scripts\\bench_by_language.py

One decider request per case (all of a case's questions together), paced for the free tier:
about 40 cases, 5 minutes. Writes submission/bench/by_language.md and by_language.json.
(`./kit bench` compares Decider with the LLM; this adds the per-language view.)
"""

import json
import statistics
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from decider_kit.config import load_dotenv  # noqa: E402

load_dotenv()
from decider_kit import Decider  # noqa: E402

from agent.decision import QUESTIONS  # noqa: E402


def answer(d, kind: str) -> str:
    return d.label if kind == "choice" else ("yes" if d.yes else "no")


def main() -> None:
    cases = [json.loads(x) for x in (ROOT / "agent" / "eval_cases.jsonl").read_text(encoding="utf-8").splitlines() if x.strip()]
    dec = Decider()
    rows = []
    for k, c in enumerate(cases, 1):
        qs = {n: QUESTIONS[n] for n in c["expected"]}
        for attempt in range(3):
            try:
                a = dec.ask(c["state"], qs)
                break
            except Exception as e:  # noqa: BLE001
                print("  (waiting:", str(e)[:60], ")")
                time.sleep(20)
        for n, want in c["expected"].items():
            got = answer(a[n], qs[n]["type"])
            rows.append({"lang": c.get("lang", "en"), "question": n, "want": want, "got": got, "ok": got == want,
                         "ms": dec.last_latency_ms, "message": c["state"].split("\n")[0][16:]})
        print(f"{k:2}/{len(cases)} {c.get('lang', 'en'):9} " + " ".join(
            f"{n}={'ok' if answer(a[n], qs[n]['type']) == w else 'X'}" for n, w in c["expected"].items()))
        time.sleep(6.5)
    langs = {"en": "English", "tanglish": "Tanglish", "tamil": "Tamil script"}
    out = {"by_language": {}, "by_question": {}, "overall": {}}
    for lg in langs:
        r = [x for x in rows if x["lang"] == lg]
        if r:
            out["by_language"][langs[lg]] = {"decisions": len(r), "accuracy": round(sum(x["ok"] for x in r) / len(r), 3)}
    for q in QUESTIONS:
        r = [x for x in rows if x["question"] == q]
        if r:
            out["by_question"][q] = {"decisions": len(r), "accuracy": round(sum(x["ok"] for x in r) / len(r), 3)}
    ms = [x["ms"] for x in rows if x["ms"]]
    out["overall"] = {"decisions": len(rows), "requests": len(cases), "accuracy": round(sum(x["ok"] for x in rows) / len(rows), 3),
                      "median_request_ms": round(statistics.median(ms)) if ms else None}
    out["mistakes"] = [{k: x[k] for k in ("lang", "message", "question", "want", "got")} for x in rows if not x["ok"]]
    dest = ROOT / "submission" / "bench"
    dest.mkdir(parents=True, exist_ok=True)
    before_file = dest / "by_language_before.json"
    before = json.loads(before_file.read_text()) if before_file.exists() else None
    (dest / "by_language.json").write_text(json.dumps(out, indent=1, ensure_ascii=False), encoding="utf-8")
    md = ["# Strands Decider 2B by language", ""]
    if before:
        md += ["Before = message only. After = the same message plus a short **word help** line from our code",
               "(\"'nellu' = paddy (a crop)\"), see `glossary` in agent/farm_guard.py. The decider still decides.", "",
               "| Language | Decisions | Before | After |", "|---|---|---|---|"]
        md += [f"| {k} | {v['decisions']} | {before['by_language'].get(k, {}).get('accuracy', 0):.0%} | {v['accuracy']:.0%} |"
               for k, v in out["by_language"].items()]
    else:
        md += ["| Language | Decisions | Accuracy |", "|---|---|---|"]
        md += [f"| {k} | {v['decisions']} | {v['accuracy']:.0%} |" for k, v in out["by_language"].items()]
    md += ["", "| Question | Decisions | Accuracy |", "|---|---|---|"]
    md += [f"| {k} | {v['decisions']} | {v['accuracy']:.0%} |" for k, v in out["by_question"].items()]
    o = out["overall"]
    md += ["", f"Overall: {o['accuracy']:.0%} on {o['decisions']} decisions in {o['requests']} requests "
               f"(median {o['median_request_ms']} ms per request, all questions together)."]
    if before:
        md += [f"Before: {before['overall']['accuracy']:.0%}."]
    if out["mistakes"]:
        md += ["", "Remaining mistakes:", ""] + [f"- ({m['lang']}) \"{m['message']}\": {m['question']} wanted {m['want']}, got {m['got']}"
                                                 for m in out["mistakes"]]
    (dest / "by_language.md").write_text("\n".join(md) + "\n", encoding="utf-8")
    print("\n".join(md))


if __name__ == "__main__":
    main()
