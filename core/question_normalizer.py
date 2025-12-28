# core/question_normalizer.py

def normalize_question(question: str) -> str:
    """
    Expands underspecified user inputs into explicit questions.
    Does NOT add facts. Only clarifies intent.
    """

    q = question.strip()

    # Single-term or short phrase inputs
    if len(q.split()) <= 3 and not q.endswith("?"):
        return f"What is {q}?"

    # Abbreviations / common shorthand
    if q.lower() in {"pm india", "india pm"}:
        return "Who is the Prime Minister of India today?"

    return question
