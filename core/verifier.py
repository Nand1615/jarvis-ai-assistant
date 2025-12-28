import os
import re
import json
import time
from datetime import datetime
from collections import Counter
from typing import Optional, Dict, Any
from memory.auth import require_auth

# =========================
# Existing name verification utilities
# =========================

ROLE_PHRASES = {
    "Prime Minister",
    "Prime Ministers",
    "Latest News",
    "Breaking News",
    "India Today",
    "Lok Sabha",
    "Wikipedia"
}


def extract_person_names(text: str) -> list:
    """
    Extract likely human names and reject role phrases.
    """
    if not text:
        return []

    pattern = r"\b[A-Z][a-z]+(?:\s[A-Z][a-z]+)+\b"
    candidates = re.findall(pattern, text)

    cleaned = []

    for name in candidates:
        name = name.strip()

        # 1. Reject known role / non-person phrases
        if name in ROLE_PHRASES:
            continue

        # 2. Reject phrases containing role words
        if "Prime Minister" in name:
            continue

        # 3. Reject unrealistically long names
        parts = name.split()
        if len(parts) > 3:
            continue

        # 4. Accept as person name
        cleaned.append(name)

    return cleaned


def verify_prime_minister(results: list) -> dict:
    """
    Verifies who the Prime Minister is based on search results.
    Returns verification status and the most consistent name.
    """

    name_candidates = []

    for r in results:
        text = f"{r.get('title', '')} {r.get('snippet', '')}"
        names = extract_person_names(text)
        name_candidates.extend(names)

    if not name_candidates:
        return {
            "verified": False,
            "reason": "No person names found in search results."
        }

    counts = Counter(name_candidates)
    most_common_name, frequency = counts.most_common(1)[0]

    if frequency >= 2:
        return {
            "verified": True,
            "answer": most_common_name,
            "confidence": frequency,
            "candidates": counts
        }

    return {
        "verified": False,
        "reason": "No consistent agreement across sources.",
        "candidates": counts
    }


# =========================
# Safety / Verification / Modes / Sandbox / Audit Logging
# =========================

BASE_DIR = os.path.dirname(os.path.dirname(__file__))
MEM_DIR = os.path.join(BASE_DIR, 'memory')
STATE_PATH = os.path.join(MEM_DIR, 'state.json')
SECURITY_PATH = os.path.join(MEM_DIR, 'security.json')
LOG_DIR = os.path.join(BASE_DIR, 'logs')
LOG_PATH = os.path.join(LOG_DIR, 'activity.log')


# ---- Internal helpers ----

def _load_json(path: str, default):
    try:
        with open(path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception:
        return default


def _save_json(path: str, data: Dict[str, Any]):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    tmp = path + '.tmp'
    with open(tmp, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    os.replace(tmp, path)


def _now_iso() -> str:
    return datetime.utcnow().isoformat()


def _log_event(action: str, status: str, details: Optional[Dict[str, Any]] = None):
    os.makedirs(LOG_DIR, exist_ok=True)
    entry = {
        'ts': _now_iso(),
        'action': action,
        'status': status,
        'details': details or {},
    }
    try:
        with open(LOG_PATH, 'a', encoding='utf-8') as f:
            f.write(json.dumps(entry, ensure_ascii=False) + '\n')
    except Exception:
        pass


# ---- Modes ----

def get_mode() -> str:
    state = _load_json(STATE_PATH, {})
    mode = str(state.get('mode') or 'normal').lower()
    return 'pro' if mode == 'pro' else 'normal'


def set_mode(mode: str):
    mode = 'pro' if str(mode).lower() == 'pro' else 'normal'
    # Changing mode requires auth
    if not require_auth(f"Change mode to {mode}"):
        _log_event('set_mode', 'denied', {'mode': mode})
        return
    state = _load_json(STATE_PATH, {})
    state['mode'] = mode
    _save_json(STATE_PATH, state)
    _log_event('set_mode', 'ok', {'mode': mode})


# ---- Confirmation prompts ----

def confirm(prompt: str) -> bool:
    """Ask the user for a y/n confirmation in console."""
    try:
        ans = input(f"{prompt} (y/n): ").strip().lower()
        return ans in {'y', 'yes'}
    except Exception:
        return False


def confirm_strict(prompt: str) -> bool:
    """Require explicit CONFIRM typed by user for very dangerous ops."""
    try:
        ans = input(f"{prompt} Type CONFIRM to proceed: ").strip()
        return ans == 'CONFIRM'
    except Exception:
        return False


# ---- Destructive action detection ----

def is_destructive_action(text_or_action: str) -> bool:
    t = (text_or_action or '').lower()
    keywords = [
        'delete', 'remove', 'erase', 'wipe', 'format', 'rm ', 'rmdir', 'del ', 'truncate', 'destroy'
    ]
    return any(k in t for k in keywords)


# ---- Sandbox for file operations ----

def _security_defaults():
    return {
        'allowed_paths': [],  # directories allowed for file ops
        'protected_paths': [  # common dangerous roots
            'C:\\', 'C:/', '/'
        ]
    }


def _load_security():
    return _load_json(SECURITY_PATH, _security_defaults())


def add_allowed_directory(path: str) -> bool:
    if not path:
        return False
    sec = _load_security()
    norm = os.path.abspath(path)
    if norm not in sec['allowed_paths']:
        sec['allowed_paths'].append(norm)
        _save_json(SECURITY_PATH, sec)
        _log_event('sandbox_allow', 'ok', {'path': norm})
    return True


def is_path_allowed(path: str) -> bool:
    if not path:
        return False
    sec = _load_security()
    norm = os.path.abspath(path)
    # Disallow protected roots explicitly
    for p in sec.get('protected_paths', []):
        try:
            if os.path.abspath(norm).rstrip('\\/') == os.path.abspath(p).rstrip('\\/'):
                return False
        except Exception:
            continue
    # Allow if path is inside one of allowed_paths
    for base in sec.get('allowed_paths', []):
        try:
            base_abs = os.path.abspath(base)
            if os.path.commonpath([norm, base_abs]) == base_abs:
                return True
        except Exception:
            continue
    return False


# ---- High-level verification gates ----

def verify_file_operation(op: str, target_path: str) -> bool:
    """
    Verify that file operation is safe:
      - Ensure sandbox allows the path
      - In normal mode, ask confirmation for all system-level ops
      - For destructive ops (delete/wipe/format), ask strict confirmation
    Returns True if allowed to proceed, False otherwise.
    """
    details = {'op': op, 'path': target_path}
    mode = get_mode()

    if not is_path_allowed(target_path):
        _log_event('file_op_denied', 'denied', {**details, 'reason': 'path_not_allowed'})
        print("Operation blocked: path is not in allowed directories.")
        print("Tip: add the directory to sandbox allow-list in memory/security.json")
        return False

    destructive = is_destructive_action(op)

    if destructive:
        if not confirm_strict(f"This looks destructive ({op}). Are you absolutely sure?"):
            _log_event('file_op_denied', 'denied', {**details, 'reason': 'destructive_not_confirmed'})
            return False
        # Require authentication for destructive file ops
        if not require_auth("Destructive file operation"):
            _log_event('file_op_denied', 'denied', {**details, 'reason': 'auth_failed'})
            return False

    if mode == 'normal':
        if not confirm(f"Proceed with file operation '{op}' on {target_path}?"):
            _log_event('file_op_denied', 'denied', {**details, 'reason': 'user_rejected'})
            return False
        # For sensitive but non-destructive ops, optionally require auth
        if op in {'move', 'rename'}:
            if not require_auth("File operation authorization"):
                _log_event('file_op_denied', 'denied', {**details, 'reason': 'auth_failed'})
                return False

    _log_event('file_op_allowed', 'ok', details)
    return True


def verify_system_action(action: str, risk: str = 'low') -> bool:
    """
    Verify a system-level action.
      - Normal mode: ask before all system-level actions
      - Pro mode: auto-run low-risk; confirm for medium/high-risk
    risk in {'low','medium','high'}
    """
    details = {'action': action, 'risk': risk}
    mode = get_mode()

    if mode == 'normal':
        if not confirm(f"About to execute: {action}. Proceed?"):
            _log_event('sys_action_denied', 'denied', {**details, 'reason': 'user_rejected'})
            return False
        # Require auth for medium/high risk actions
        if risk in {'medium', 'high'} and not require_auth("System action authorization"):
            _log_event('sys_action_denied', 'denied', {**details, 'reason': 'auth_failed'})
            return False
        _log_event('sys_action_allowed', 'ok', details)
        return True

    # pro mode
    if risk not in {'low', 'medium', 'high'}:
        risk = 'low'

    if risk == 'low':
        _log_event('sys_action_allowed', 'ok', details)
        return True

    # medium/high require confirmation even in pro mode
    if not confirm(f"[{risk.upper()}] Execute: {action}?"):
        _log_event('sys_action_denied', 'denied', {**details, 'reason': 'user_rejected'})
        return False
    # And require auth
    if not require_auth("System action authorization"):
        _log_event('sys_action_denied', 'denied', {**details, 'reason': 'auth_failed'})
        return False

    _log_event('sys_action_allowed', 'ok', details)
    return True


# Convenience wrapper for generic destructive string detection

def verify_destructive_text(text: str) -> bool:
    if is_destructive_action(text):
        return confirm_strict("Destructive operation detected.")
    return True
