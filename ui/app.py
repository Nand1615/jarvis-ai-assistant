import tkinter as tk
from tkinter import scrolledtext
import os
from datetime import datetime

from ml.predict import predict_intent
from core.router import route
from voice.listen import listen
from voice.speak import speak
from llm.chat import chat_with_llm

from core.context_manager import ContextManager
from core.question_normalizer import normalize_question
from core.search_engine import search_web
from core.verifier import verify_prime_minister
from core.answer_generator import generate_final_answer
from memory.state import get_last_open_app


def offline_answer(user_input: str) -> str:
    try:
        q = normalize_question(user_input)
        results = search_web(q, max_results=5)
        if not results:
            return "I couldn't retrieve any information right now."
        ql = q.lower()
        if "prime minister" in ql:
            verification = verify_prime_minister(results)
            return generate_final_answer(q, verification, concise=True)
        top = results[0]
        title = (top.get("title") or "").strip()
        snippet = (top.get("snippet") or "").strip()
        if snippet:
            return snippet
        if title:
            return title
        return "I found an answer but cannot display details right now."
    except Exception:
        return "Offline mode active. I can't provide a detailed answer right now."


class JarvisUI:
    def __init__(self, root: tk.Tk):
        self.root = root
        self.root.title("JARVIS Assistant")
        self.root.geometry("820x600")

        # Context manager
        self.ctx = ContextManager(short_window=8)

        # Seed context with last open item
        last = get_last_open_app()
        if last:
            kind, _, name = last.partition(':')
            self.ctx.ltm.add(text=f"last_open={kind}:{name}", mtype='fact', tags=['last_open'])

        # UI Elements
        self.chat = scrolledtext.ScrolledText(self.root, wrap=tk.WORD, state=tk.DISABLED)
        self.chat.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        input_frame = tk.Frame(self.root)
        input_frame.pack(fill=tk.X, padx=10, pady=(0,10))

        self.entry = tk.Entry(input_frame)
        self.entry.pack(side=tk.LEFT, fill=tk.X, expand=True)
        self.entry.bind('<Return>', self._on_send)

        self.send_btn = tk.Button(input_frame, text="Send", command=self.on_send)
        self.send_btn.pack(side=tk.LEFT, padx=5)

        self.mic_btn = tk.Button(input_frame, text="🎤", command=self.on_mic)
        self.mic_btn.pack(side=tk.LEFT)

        # Greet on startup
        self.greet_user()

    def append(self, role: str, text: str):
        self.chat.configure(state=tk.NORMAL)
        prefix = "You" if role == 'user' else "JARVIS"
        self.chat.insert(tk.END, f"{prefix}: {text}\n")
        self.chat.configure(state=tk.DISABLED)
        self.chat.see(tk.END)

    def greet_user(self):
        hour = datetime.now().hour
        if hour < 12:
            t = "Good morning"
        elif hour < 18:
            t = "Good afternoon"
        else:
            t = "Good evening"
        greet = f"{t}! How was your day? How may I help you today?"
        self.append('assistant', greet)
        try:
            speak(greet)
        except Exception:
            pass

    def _on_send(self, event):
        self.on_send()

    def on_send(self):
        text = self.entry.get().strip()
        if not text:
            return
        self.entry.delete(0, tk.END)
        self.process_input(text)

    def on_mic(self):
        try:
            heard = listen()
        except Exception:
            heard = None
        if heard:
            self.process_input(heard)

    def process_input(self, user_input: str):
        self.append('user', user_input)
        self.ctx.push_user(user_input)

        # Predict intent + confidence
        intent, confidence = predict_intent(user_input)

        # Low-confidence => online or offline fallback
        low_conf = confidence < 0.35 and intent not in ["open_app", "open_website"]
        response = None
        if low_conf:
            api_key_present = bool(os.getenv("OPENROUTER_API_KEY") or os.getenv("OPENAI_API_KEY"))
            if api_key_present:
                try:
                    response = chat_with_llm(user_input, context=self.ctx.build_context(user_input))
                    if isinstance(response, str) and response.lower().startswith("llm error"):
                        response = None
                except Exception:
                    response = None
            if response is None:
                response = offline_answer(user_input)
        else:
            response = route(intent, user_input)

        if not response:
            response = "I couldn't process that request."

        self.append('assistant', response)
        try:
            speak(response)
        except Exception:
            pass
        self.ctx.push_assistant(response)


def run_ui():
    root = tk.Tk()
    app = JarvisUI(root)
    root.mainloop()
