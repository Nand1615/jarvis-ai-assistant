import sys
import subprocess
import webbrowser
import os
from datetime import datetime
from core.websites import WEBSITES
from core.apps import APPS
from memory.context import (
        set_context,
        get_current_context,
        get_last_context,
        clear_current_context
)
from memory.state import set_last_open_app, get_last_open_app
from core.verifier import verify_system_action, _log_event


# ---------- BASIC RESPONSES ----------

def greet():
    return "Hello! How can I help you?"


def get_time():
    return datetime.now().strftime("Current time is %H:%M:%S")


def exit_app():
    if not verify_system_action("exit application", risk='medium'):
        return "Exit cancelled."
    print("JARVIS: Shutting down.")
    _log_event('exit', 'ok', {})
    sys.exit()


# ---------- WEBSITE ACTION ----------

def open_website(text: str):
    text = text.lower()
    for name, url in WEBSITES.items():
        if name in text:
            if not verify_system_action(f"open website {name}", risk='low'):
                return "Cancelled."
            webbrowser.open(url)
            set_context("open_website", name)
            set_last_open_app(f"website:{name}")
            _log_event('open_website', 'ok', {'name': name})
            return f"Opening {name}."
    return "Website not found."


# ---------- SYSTEM APP ACTION ----------

def open_app(text: str):
    text = text.lower()
    for name, info in APPS.items():
        if name in text:
            try:
                if not verify_system_action(f"open app {name}", risk='low'):
                    return "Cancelled."
                subprocess.Popen(info["command"], shell=True)
                set_context("open_app", name)
                set_last_open_app(f"app:{name}")
                _log_event('open_app', 'ok', {'name': name})
                return f"Opening {name}."
            except Exception:
                _log_event('open_app', 'error', {'name': name})
                return f"Failed to open {name}."
    return "Application not found."


# ---------- CLOSE LAST APP (CONTEXT BASED) ----------

def close_last_app():
    action, target = get_current_context()

    if action != "open_app" or not target:
        return "I don't know what to close."

    app_info = APPS.get(target)
    if not app_info:
        return "Closing this application is not supported."

    process = app_info.get("process")
    if not process:
        return "Cannot determine how to close this app."

    if not verify_system_action(f"close app {target}", risk='low'):
        return "Cancelled."

    result = os.system(f"taskkill /im {process} /f >nul 2>&1")

    if result != 0:
        _log_event('close_app', 'not_running', {'name': target})
        return f"{target} is not running."

    clear_current_context()
    _log_event('close_app', 'ok', {'name': target})
    return f"Closed {target}."


def close_app_by_name(text: str):
    text = text.lower()

    for name, info in APPS.items():
        if name in text:
            process = info.get("process")
            if not process:
                return "I cannot close this app."

            if not verify_system_action(f"close app {name}", risk='low'):
                return "Cancelled."

            result = os.system(f"taskkill /im {process} /f >nul 2>&1")

            if result != 0:
                _log_event('close_app', 'not_running', {'name': name})
                return f"{name} is not running."

            clear_current_context()
            _log_event('close_app', 'ok', {'name': name})
            return f"Closed {name}."

    return "I couldn't find the application to close."


def open_again():
    action, target = get_last_context()

    if not action or not target:
        last = get_last_open_app()
        if last:
            kind, _, name = last.partition(':')
            if kind == 'app':
                info = APPS.get(name)
                if info:
                    if not verify_system_action(f"reopen app {name}", risk='low'):
                        return "Cancelled."
                    subprocess.Popen(info["command"], shell=True)
                    set_context("open_app", name)
                    set_last_open_app(f"app:{name}")
                    _log_event('open_again', 'ok', {'type': 'app', 'name': name})
                    return f"Opening {name} again."
            if kind == 'website':
                url = WEBSITES.get(name)
                if url:
                    if not verify_system_action(f"reopen website {name}", risk='low'):
                        return "Cancelled."
                    webbrowser.open(url)
                    set_context("open_website", name)
                    set_last_open_app(f"website:{name}")
                    _log_event('open_again', 'ok', {'type': 'website', 'name': name})
                    return f"Opening {name} again."
        return "I don't know what to open again."

    if action == "open_app":
        info = APPS.get(target)
        if not info:
            return "I can't reopen that app."

        if not verify_system_action(f"reopen app {target}", risk='low'):
            return "Cancelled."

        subprocess.Popen(info["command"], shell=True)
        set_context("open_app", target)
        set_last_open_app(f"app:{target}")
        _log_event('open_again', 'ok', {'type': 'app', 'name': target})
        return f"Opening {target} again."

    if action == "open_website":
        url = WEBSITES.get(target)
        if not url:
            return "I can't reopen that website."

        if not verify_system_action(f"reopen website {target}", risk='low'):
            return "Cancelled."

        webbrowser.open(url)
        set_context("open_website", target)
        set_last_open_app(f"website:{target}")
        _log_event('open_again', 'ok', {'type': 'website', 'name': target})
        return f"Opening {target} again."

    return "Cannot reopen the last action."
