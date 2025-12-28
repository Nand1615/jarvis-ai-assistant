import os
import json
import time
import secrets
import hashlib
from typing import Optional
from getpass import getpass

BASE_DIR = os.path.dirname(__file__)
AUTH_PATH = os.path.join(BASE_DIR, 'auth.json')

# Session cache to avoid repeated prompts within a short window
_auth_ok_until: float = 0.0


def _load() -> dict:
    try:
        with open(AUTH_PATH, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception:
        return {}


def _save(data: dict):
    os.makedirs(os.path.dirname(AUTH_PATH), exist_ok=True)
    tmp = AUTH_PATH + '.tmp'
    with open(tmp, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    os.replace(tmp, AUTH_PATH)


def _hash_pin(pin: str, salt: bytes, iterations: int = 120000) -> str:
    dk = hashlib.pbkdf2_hmac('sha256', pin.encode('utf-8'), salt, iterations)
    return dk.hex()


def set_pin_interactive():
    print("Security setup: create a PIN for sensitive actions.")
    while True:
        pin1 = getpass("Enter new PIN (4-8 digits): ").strip()
        if not (pin1.isdigit() and 4 <= len(pin1) <= 8):
            print("Invalid PIN format. Use 4-8 digits.")
            continue
        pin2 = getpass("Confirm PIN: ").strip()
        if pin1 != pin2:
            print("PINs do not match. Try again.")
            continue
        break
    salt = secrets.token_bytes(16)
    iterations = 150000
    h = _hash_pin(pin1, salt, iterations)
    data = {
        'salt': salt.hex(),
        'hash': h,
        'iterations': iterations,
        'created_at': time.time(),
    }
    _save(data)
    print("PIN set successfully.")


def has_pin() -> bool:
    data = _load()
    return bool(data.get('hash') and data.get('salt'))


def verify_pin(pin: str) -> bool:
    data = _load()
    if not data:
        return False
    try:
        salt = bytes.fromhex(data['salt'])
        iterations = int(data.get('iterations', 120000))
        target = data['hash']
        return secrets.compare_digest(_hash_pin(pin, salt, iterations), target)
    except Exception:
        return False


def require_auth(reason: str = "", ttl_seconds: int = 900) -> bool:
    global _auth_ok_until
    now = time.time()
    if now < _auth_ok_until:
        return True
    print(("Authentication required. " + reason).strip())
    for _ in range(3):
        pin = getpass("Enter PIN: ")
        if verify_pin(pin):
            _auth_ok_until = time.time() + ttl_seconds
            print("Authentication successful.")
            return True
        else:
            print("Invalid PIN.")
    print("Authentication failed.")
    return False


def ensure_setup():
    if has_pin():
        return
    ans = input("No PIN configured. Set up a PIN now? (y/n): ").strip().lower()
    if ans in {"y", "yes"}:
        set_pin_interactive()
    else:
        print("Warning: sensitive operations will be unavailable until you set a PIN.")
