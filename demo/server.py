"""Demo UI for Uzhavan: a phone-style farm app, with every Strands Decider 2B decision shown live.

    .\\kit.cmd demo        # http://localhost:8501
    DEMO_TARGET=agentcore AGENTCORE_ARN=arn:... ./kit demo     # talk to the agent deployed on AWS
"""

from __future__ import annotations

import json
import os
import sys
import traceback
import uuid
from pathlib import Path
from typing import Any

from fastapi import FastAPI
from fastapi.responses import FileResponse, JSONResponse
from pydantic import BaseModel

from decider_kit.config import load_dotenv

load_dotenv()
STATIC = Path(__file__).parent / "static"
app = FastAPI(title="Uzhavan demo")
_agent: Any = None


class Turn(BaseModel):
    message: str = ""
    session_id: str = "demo"
    images: list[str] = []
    district: str | None = None
    crop: str | None = None
    intent: str | None = None
    lang: str | None = None


def agent() -> Any:
    global _agent
    if _agent is None:
        if os.environ.get("DEMO_TARGET") == "agentcore":
            _agent = AgentCoreClient(os.environ["AGENTCORE_ARN"])
        else:
            from agent.agent import HackathonAgent

            _agent = HackathonAgent()
    return _agent


class AgentCoreClient:
    """The same `chat()` interface, served by the agent deployed on Amazon Bedrock AgentCore Runtime."""

    def __init__(self, arn: str):
        import boto3

        self.arn = arn
        self.client = boto3.client("bedrock-agentcore", region_name=os.environ.get("AWS_REGION", "us-east-1"))
        self.sessions: dict[str, str] = {}

    def chat(self, message: str, session_id: str = "demo", images: list[str] | None = None,
             district: str | None = None, crop: str | None = None, intent: str | None = None,
             lang: str | None = None) -> dict[str, Any]:
        sid = self.sessions.setdefault(session_id, f"demo-{session_id}-{uuid.uuid4().hex}")
        payload = {"prompt": message or intent or "", "district": district, "crop": crop, "intent": intent, "lang": lang,
                   **({"images": images} if images else {})}
        r = self.client.invoke_agent_runtime(agentRuntimeArn=self.arn, runtimeSessionId=sid,
                                             payload=json.dumps(payload).encode())
        body = r["response"].read() if hasattr(r["response"], "read") else r["response"]
        out = json.loads(body)
        out["served_by"] = "Amazon Bedrock AgentCore Runtime"
        return out


@app.get("/")
def index() -> FileResponse:
    return FileResponse(STATIC / "index.html")


@app.get("/api/info")
def info() -> dict[str, Any]:
    from decider_kit.config import settings
    from decider_kit.llm import describe

    s = settings()
    llm = describe()
    if os.environ.get("DEMO_TARGET") == "agentcore":
        llm = f"Amazon Bedrock ({s.bedrock_model})"
    from agent.agent import NAME

    return {"agent": NAME, "llm": llm, "bedrock_model": s.bedrock_model, "decider": s.decider_mode,
            "target": os.environ.get("DEMO_TARGET", "local")}


@app.get("/api/districts")
def districts() -> dict[str, Any]:
    from agent.tools import CROPS, TN_DISTRICTS

    from agent.i18n import CROP_TA, DISTRICT_TA

    return {"districts": [{"name": n, "ta": DISTRICT_TA.get(n, n), "lat": la, "lon": lo} for n, (la, lo) in TN_DISTRICTS.items()],
            "crops": [{"name": c, "ta": CROP_TA.get(c, c)} for c in CROPS[:6]]}


@app.get("/api/tools")
def tools() -> dict[str, Any]:
    """The tool buttons: icon, labels and group, in English and Tamil."""
    from agent.tools import GROUPS, REGISTRY

    return {"tools": [{"intent": k, "tool": v[0], "needs_crop": v[2], "group": v[3], "icon": v[4], "en": v[5], "ta": v[6]}
                      for k, v in REGISTRY.items()],
            "groups": {k: {"en": en, "ta": ta} for k, (en, ta) in GROUPS.items()}}


@app.get("/api/weather")
def weather(district: str) -> dict[str, Any]:
    """Weather only (no advice), for the side panel when a district is picked."""
    from agent.tools import WeatherError, alert_for, weather_card

    try:
        return {"weather": weather_card(district), "alert": alert_for(district)}
    except WeatherError as e:
        return {"weather": None, "alert": None, "error": e.text}


@app.get("/api/alert")
def alert(district: str) -> dict[str, Any]:
    from agent.tools import WeatherError, alert_for

    try:
        return {"alert": alert_for(district)}
    except WeatherError as e:
        return {"alert": None, "error": e.text}


@app.post("/api/chat")
def chat(t: Turn) -> JSONResponse:
    try:
        import inspect

        a = agent()
        params = inspect.signature(a.chat).parameters
        if t.images and "images" not in params:
            return JSONResponse({"error": "agent does not support images"}, status_code=400)
        kw: dict[str, Any] = {k: v for k, v in (("district", t.district), ("crop", t.crop), ("intent", t.intent), ("lang", t.lang))
                              if k in params and v is not None}
        if t.images:
            kw["images"] = t.images
        return JSONResponse(a.chat(t.message, t.session_id, **kw))
    except Exception as e:  # noqa: BLE001
        print(f"ERROR in /api/chat:\n{traceback.format_exc()}", file=sys.stderr, flush=True)
        return JSONResponse({"error": f"{type(e).__name__}: {e}"}, status_code=500)


class Speech(BaseModel):
    text: str
    lang: str = "ta"


_TTS: dict[tuple[str, str], bytes] = {}


@app.post("/api/tts")
def tts(sp: Speech):
    """Read a reply aloud when the browser has no voice for the language (Tamil on Windows Chrome).
    Uses gTTS (Google Translate's speech); needs the internet."""
    from fastapi.responses import Response

    key = ("ta" if sp.lang.startswith("ta") else "en", sp.text[:1500])
    if key not in _TTS:
        try:
            import io

            from gtts import gTTS

            buf = io.BytesIO()
            gTTS(text=key[1], lang=key[0]).write_to_fp(buf)
            _TTS[key] = buf.getvalue()
        except Exception as e:  # noqa: BLE001
            print(f"TTS failed: {type(e).__name__}: {e}", file=sys.stderr, flush=True)
            return JSONResponse({"error": "speech not available"}, status_code=503)
    return Response(_TTS[key], media_type="audio/mpeg")


@app.post("/api/reset")
def reset() -> dict[str, bool]:
    global _agent
    _agent = None
    return {"ok": True}
