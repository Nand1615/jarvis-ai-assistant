from core.router import route
from ml.predict import predict_intent
from voice.listen import listen
from voice.speak import speak
from llm.chat import chat_with_llm

import os

# Optional offline QA utilities
from core.question_normalizer import normalize_question
from core.search_engine import search_web
from core.verifier import verify_prime_minister
from core.answer_generator import generate_final_answer

from core.context_manager import ContextManager
from memory.state import get_last_open_app
from memory.auth import ensure_setup
from core.verifier import set_mode, get_mode, add_allowed_directory


def get_user_input():
    """
    Handles both voice and text input.
    Press Enter to speak, or type directly.
    """
    choice = input("Press Enter to speak or type your command: ").strip()

    if choice == "":
        print("Listening...")
        text = listen()
        if text:
            print(f"You said: {text}")
        return text
    else:
        return choice


def offline_answer(user_input: str) -> str:
    """
    Offline/hybrid fallback using web search. For specific recognized
    patterns (e.g., "Prime Minister" questions) it performs verification.
    Otherwise it returns a concise snippet from top search result.
    """
    try:
        q = normalize_question(user_input)
        results = search_web(q, max_results=5)

        if not results:
            return "I couldn't retrieve any information right now."

        ql = q.lower()
        if "prime minister" in ql:
            verification = verify_prime_minister(results)
            return generate_final_answer(q, verification, concise=True)

        # Generic concise answer from top result
        top = results[0]
        title = (top.get("title") or "").strip()
        snippet = (top.get("snippet") or "").strip()
        source = (top.get("source") or "").strip()

        if title and snippet:
            return snippet
        if title:
            return title
        if snippet:
            return snippet
        return "I found an answer but cannot display details right now."

    except Exception:
        # Stay resilient in offline mode
        return "Offline mode active. I can't provide a detailed answer right now."


def main():
    # Launch web 3D UI server (Flask) and open browser
    import webbrowser
    from threading import Thread
    from ui.server import app as flask_app

    def run_server():
        flask_app.run(host='127.0.0.1', port=5000, debug=False)

    t = Thread(target=run_server, daemon=True)
    t.start()

    # Open in default browser
    webbrowser.open('http://127.0.0.1:5000/')

    # Keep a minimal Tk loop or input loop to hold the process
    # Simple console wait loop
    try:
        while t.is_alive():
            t.join(1)
    except KeyboardInterrupt:
        pass


if __name__ == "__main__":
    main()
