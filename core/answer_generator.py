# core/answer_generator.py

from datetime import datetime


def generate_final_answer(
    question: str,
    verification: dict,
    concise: bool = False
) -> str:
    """
    Generates the final user-facing answer.
    If concise=True, returns ONLY the answer text.
    """

    timestamp = datetime.utcnow().strftime("%d %B %Y")

    # Case 1: Verification failed → refuse safely
    if not verification.get("verified"):
        reason = verification.get("reason", "Unable to verify reliably.")
        return (
            f"I cannot answer this question reliably right now.\n"
            f"Reason: {reason}"
        )

    answer = verification.get("answer")
    confidence = verification.get("confidence", 1)

    # Concise mode → ONLY the answer
    if concise:
        return answer

    # Full safe mode → answer + metadata
    return (
        f"As of {timestamp}, the answer is:\n"
        f"{answer}\n\n"
        f"(Verified across {confidence} independent sources)"
    )
