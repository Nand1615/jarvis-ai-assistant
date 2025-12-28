from flask import Flask, request, jsonify, send_from_directory
import os
import threading

from ml.predict import predict_intent
from core.router import route
from llm.chat import chat_with_llm
from core.context_manager import ContextManager
from core.question_normalizer import normalize_question
from core.search_engine import search_web
from core.verifier import verify_prime_minister
from core.answer_generator import generate_final_answer

app = Flask(__name__, static_folder=None)
ctx = ContextManager(short_window=8)


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


@app.after_request
def add_cors(resp):
    resp.headers['Access-Control-Allow-Origin'] = request.headers.get('Origin', '*')
    resp.headers['Access-Control-Allow-Methods'] = 'GET,POST,OPTIONS'
    resp.headers['Access-Control-Allow-Headers'] = 'Content-Type'
    return resp


@app.route('/api/chat', methods=['POST'])
def api_chat():
    data = request.get_json(silent=True) or {}
    text = (data.get('text') or '').strip()
    if not text:
        return jsonify({"reply": "Please provide some text."})

    ctx.push_user(text)

    intent, confidence = predict_intent(text)
    low_conf = confidence < 0.35 and intent not in ["open_app", "open_website"]

    reply = None
    if low_conf:
        api_key_present = bool(os.getenv("OPENROUTER_API_KEY") or os.getenv("OPENAI_API_KEY"))
        if api_key_present:
            try:
                reply = chat_with_llm(text, context=ctx.build_context(text))
                if isinstance(reply, str) and reply.lower().startswith("llm error"):
                    reply = None
            except Exception:
                reply = None
        if reply is None:
            reply = offline_answer(text)
    else:
        reply = route(intent, text)

    if not reply:
        reply = "I couldn't process that request."

    ctx.push_assistant(reply)
    return jsonify({"reply": reply})


@app.route('/')
def index():
    return send_from_directory(os.path.join(os.path.dirname(__file__), '..', 'web'), 'index.html')


@app.route('/<path:path>')
def static_files(path):
    web_dir = os.path.join(os.path.dirname(__file__), '..', 'web')
    return send_from_directory(web_dir, path)


if __name__ == '__main__':
    app.run(host='127.0.0.1', port=5000, debug=False)
