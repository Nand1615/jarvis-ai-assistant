import os
from typing import Any, Dict, List
from openai import OpenAI

# Choose provider based on available API keys
if os.getenv("OPENROUTER_API_KEY"):
    client = OpenAI(
        base_url="https://openrouter.ai/api/v1",
        api_key=os.getenv("OPENROUTER_API_KEY"),
        default_headers={
            # Optional but recommended by OpenRouter for attribution/rate limits
            "HTTP-Referer": os.getenv("OPENROUTER_SITE_URL", "http://localhost"),
            "X-Title": os.getenv("OPENROUTER_APP_NAME", "JARVIS Assistant"),
        },
    )
    DEFAULT_MODEL = os.getenv("OPENROUTER_MODEL", "openrouter/auto")
else:
    client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
    DEFAULT_MODEL = os.getenv("OPENAI_MODEL", "gpt-4.1-mini")

BASE_SYSTEM_PROMPT = (
    "You are JARVIS, a helpful AI assistant. "
    "You answer questions clearly and concisely. "
    "You adapt tone based on affect and leverage provided memory context. "
    "You do not control applications."
)


def _format_memory_context(ctx: Dict[str, Any]) -> List[Dict[str, str]]:
    msgs: List[Dict[str, str]] = []
    if not ctx:
        return msgs
    affect = ctx.get('affect') or {}
    tone = affect.get('tone', 'neutral')
    msgs.append({
        'role': 'system',
        'content': f"Tone hint: {tone}. If 'brief-fast', be concise. If 'empathetic-reassuring', be supportive."
    })
    ltm = ctx.get('long_term') or []
    if ltm:
        facts = []
        for e in ltm:
            t = e.get('type', 'note')
            txt = e.get('text', '')
            facts.append(f"[{t}] {txt}")
        msgs.append({'role': 'system', 'content': 'Relevant long-term memory:\n' + '\n'.join(facts[:5])})
    stm = ctx.get('short_term') or []
    for m in stm[-6:]:
        role = m.get('role', 'user')
        content = m.get('content', '')
        msgs.append({'role': role, 'content': content})
    return msgs


def chat_with_llm(user_input: str, context: Dict[str, Any] | None = None) -> str:
    try:
        messages: List[Dict[str, str]] = [
            {"role": "system", "content": BASE_SYSTEM_PROMPT}
        ]
        messages += _format_memory_context(context or {})
        messages.append({"role": "user", "content": user_input})

        response = client.responses.create(
            model=DEFAULT_MODEL,
            input=messages
        )
        return response.output_text.strip()
    except Exception as e:
        return f"LLM error: {e}"
