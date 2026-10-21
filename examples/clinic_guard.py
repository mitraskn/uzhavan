"""The same never-guess guardrail (agent/grounded_guard.py) in a different agent: clinic bookings.

A booking agent must never guess WHO the appointment is for or WHEN. Same guard, two new facts,
one new tool. Nothing farm-specific is reused except the pattern.

    python -m examples.clinic_guard "Book me in for tomorrow"           # asks for the patient's name
    python -m examples.clinic_guard "Book Priya Raman for tomorrow 10am" # books it
"""

from __future__ import annotations

import sys

from strands import Agent, tool

from agent.grounded_guard import GroundedFactsGuard
from decider_kit import Decider
from decider_kit.llm import agent_model, strip_thinking


@tool
def book_appointment(patient: str, date: str) -> str:
    """Book a clinic appointment for a patient on a date and time."""
    return f"Booked {patient} on {date}."


def make_agent(decider: Decider | None = None) -> tuple[Agent, GroundedFactsGuard]:
    guard = GroundedFactsGuard(
        decider or Decider(),
        facts={"patient": "the patient's full name", "date": "the appointment date and time"},
        tool_needs={"book_appointment": ["patient", "date"]},
        scope="booking, moving or cancelling clinic appointments")
    agent = Agent(model=agent_model(), tools=[book_appointment], interventions=[guard], callback_handler=None,
                  system_prompt="You book clinic appointments. Use the tool. Be brief.")
    return agent, guard


def ask(agent: Agent, guard: GroundedFactsGuard, message: str, known: dict) -> str:
    rec = guard.check(message, known)          # one Decider request per message
    if rec["verdict"] in ("deny", "redirect"):
        return "I can only help with clinic appointments."
    return strip_thinking(str(agent(message)))  # before_tool_call asks instead of guessing


if __name__ == "__main__":
    a, g = make_agent()
    msg = " ".join(sys.argv[1:]) or "Book me in for tomorrow"
    print(ask(a, g, msg, known={"patient": None, "date": None}))
    print(g.log[-1])
