"""Amazon Bedrock AgentCore Runtime entry point for the hackathon agent.

`make deploy` copies agent/ and decider_kit/ next to this file. The runtime gets DECIDER_MODE,
DECIDER_URL, DECIDER_API_KEY and BEDROCK_MODEL_ID as environment variables.

Payload: {"prompt": "...", "session_id": "optional", "images": ["<base64>", ...] (optional),
          "district": "Thanjavur" (optional), "crop": "Paddy" (optional), "intent": "rain|spray|water|plan" (optional)}
    ->  the HackathonAgent.chat() result as JSON.
"""

from bedrock_agentcore.runtime import BedrockAgentCoreApp

from agent.agent import HackathonAgent

app = BedrockAgentCoreApp()
_agent = HackathonAgent()


@app.entrypoint
def invoke(payload, context):
    payload = payload if isinstance(payload, dict) else {}
    prompt = payload.get("prompt")
    intent = payload.get("intent")
    if not intent and (not isinstance(prompt, str) or not prompt.strip()):
        return {"error": "send {\"prompt\": \"...\"}"}
    session = payload.get("session_id") or getattr(context, "session_id", None) or "default"
    out = _agent.chat(prompt or "", session, images=payload.get("images") or None, district=payload.get("district"),
                      crop=payload.get("crop"), intent=intent, lang=payload.get("lang"))
    out["served_by"] = "Amazon Bedrock AgentCore Runtime"
    return out


if __name__ == "__main__":
    app.run()
