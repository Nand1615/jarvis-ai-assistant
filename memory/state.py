import json
import os
from typing import Optional, Dict, Any

BASE_DIR = os.path.dirname(__file__)
STATE_PATH = os.path.join(BASE_DIR, 'state.json')


def _load() -> Dict[str, Any]:
    try:
        with open(STATE_PATH, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception:
        return {}


def _save(data: Dict[str, Any]):
    os.makedirs(os.path.dirname(STATE_PATH), exist_ok=True)
    tmp = STATE_PATH + '.tmp'
    with open(tmp, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    os.replace(tmp, STATE_PATH)


def set_last_open_app(name: str):
    data = _load()
    data['last_open_app'] = name
    _save(data)


def get_last_open_app() -> Optional[str]:
    return _load().get('last_open_app')
