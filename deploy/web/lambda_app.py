"""Uzhavan on AWS Lambda: the same web app (demo/server.py) behind a public Function URL.

The page and its API run here; every chat message goes to the agent on Amazon Bedrock AgentCore
Runtime (AGENTCORE_ARN). No keys are in this function: it calls AgentCore with its own IAM role.
A per-device hourly limit keeps strangers from running up the bill.
"""

import collections
import os
import time

os.environ.setdefault("DEMO_TARGET", "agentcore")

from fastapi import Request  # noqa: E402
from fastapi.responses import JSONResponse  # noqa: E402
from mangum import Mangum  # noqa: E402

from demo.server import app  # noqa: E402

LIMIT = int(os.environ.get("CHAT_LIMIT_PER_HOUR", "30"))
_hits: dict[str, collections.deque] = collections.defaultdict(collections.deque)


@app.middleware("http")
async def per_device_limit(request: Request, call_next):
    if request.method == "POST" and request.url.path in ("/api/chat", "/api/tts", "/api/reset"):
        if request.url.path == "/api/reset":
            return JSONResponse({"ok": False})  # not for the public site
        who = (request.headers.get("x-forwarded-for") or "?").split(",")[0].strip()
        q, now = _hits[who], time.time()
        while q and now - q[0] > 3600:
            q.popleft()
        if len(q) >= LIMIT:
            return JSONResponse({"error": "Too many questions from this device. Please try again in an hour."},
                                status_code=429)
        q.append(now)
    return await call_next(request)


handler = Mangum(app, lifespan="off")
