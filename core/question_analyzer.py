# jarvis/core/question_analyzer.py

from enum import Enum
import re


# =========================
# Question Types
# =========================

class QuestionType(Enum):
    TIMELESS_FACT = "timeless_fact"
    TIME_SENSITIVE_FACT = "time_sensitive_fact"
    REAL_TIME_NUMERIC = "real_time_numeric"
    OPINION = "opinion"
    UNANSWERABLE = "unanswerable"


# =========================
# Keywords for detection
# =========================

TIME_KEYWORDS = [
    "today", "current", "now", "latest", "present",
    "this year", "this month", "right now"
]

REAL_TIME_KEYWORDS = [
    "price", "rate", "cost", "weather", "score", "stock"
]


# =========================
# Question Classification
# =========================

def classify_question(question: str) -> QuestionType:
    q = question.lower()

    # Unanswerable / private
    if re.search(r"\b(password|otp|my account|my email)\b", q):
        return QuestionType.UNANSWERABLE

    # Real-time numeric (highest risk)
    for word in REAL_TIME_KEYWORDS:
        if word in q:
            return QuestionType.REAL_TIME_NUMERIC

    # Time-sensitive factual
    for word in TIME_KEYWORDS:
        if word in q:
            return QuestionType.TIME_SENSITIVE_FACT

    # Opinion / explanation
    if q.startswith(("why", "how", "should", "is it", "do you think")):
        return QuestionType.OPINION

    # Default safe case
    return QuestionType.TIMELESS_FACT


# =========================
# Answer Strategy
# =========================

def get_answer_strategy(question_type: QuestionType) -> dict:
    if question_type == QuestionType.TIMELESS_FACT:
        return {
            "allowed": True,
            "needs_search": False,
            "needs_verification": False,
            "answer_method": "local_llm"
        }

    if question_type == QuestionType.OPINION:
        return {
            "allowed": True,
            "needs_search": False,
            "needs_verification": False,
            "answer_method": "local_llm"
        }

    if question_type == QuestionType.TIME_SENSITIVE_FACT:
        return {
            "allowed": True,
            "needs_search": True,
            "needs_verification": True,
            "answer_method": "search_then_llm"
        }

    if question_type == QuestionType.REAL_TIME_NUMERIC:
        return {
            "allowed": True,
            "needs_search": True,
            "needs_verification": True,
            "answer_method": "search_multi_source"
        }

    return {
        "allowed": False,
        "reason": "This question cannot be answered safely."
    }
