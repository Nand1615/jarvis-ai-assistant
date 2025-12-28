from typing import Dict

# Simple affect detector using keyword heuristics

URGENCY = {"asap", "urgent", "hurry", "quick", "now", "immediately", "fast", "quickly"}
FRUSTRATION = {"not working", "broken", "annoyed", "frustrated", "why", "again?", "error", "doesn't work", "doesnt work"}


def detect_affect(text: str) -> Dict[str, str]:
    t = text.lower()
    tone = "neutral"
    if any(w in t for w in URGENCY):
        tone = "brief-fast"
    if any(w in t for w in FRUSTRATION):
        tone = "empathetic-reassuring"
    return {
        "tone": tone,
        "urgency": "high" if tone == "brief-fast" else "normal",
    }
