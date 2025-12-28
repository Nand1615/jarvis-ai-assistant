# core/search_engine.py

from ddgs import DDGS
from datetime import datetime


def search_web(query: str, max_results: int = 5) -> list:
    """
    Execute a live web search and return raw results.
    """

    results = []

    with DDGS() as ddgs:
        for r in ddgs.text(query, max_results=max_results):
            results.append({
                "title": r.get("title"),
                "snippet": r.get("body"),
                "source": r.get("href"),
                "retrieved_at": datetime.utcnow().isoformat()
            })

    return results
