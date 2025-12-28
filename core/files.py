import os
import shutil
from typing import Optional
from core.verifier import verify_file_operation, _log_event

# Basic file operations with sandboxing and confirmation handled by verifier

def create_folder(path: str) -> str:
    if not verify_file_operation('create_folder', path):
        return "Operation cancelled."
    try:
        os.makedirs(path, exist_ok=True)
        _log_event('create_folder', 'ok', {'path': path})
        return f"Created folder: {path}"
    except Exception as e:
        _log_event('create_folder', 'error', {'path': path, 'error': str(e)})
        return f"Failed to create folder: {e}"


def create_file(path: str, content: str = "") -> str:
    if not verify_file_operation('create_file', path):
        return "Operation cancelled."
    try:
        os.makedirs(os.path.dirname(path) or '.', exist_ok=True)
        with open(path, 'w', encoding='utf-8') as f:
            f.write(content)
        _log_event('create_file', 'ok', {'path': path})
        return f"Created file: {path}"
    except Exception as e:
        _log_event('create_file', 'error', {'path': path, 'error': str(e)})
        return f"Failed to create file: {e}"


def move(path_from: str, path_to: str) -> str:
    if not verify_file_operation('move', path_to):
        return "Operation cancelled."
    try:
        os.makedirs(os.path.dirname(path_to) or '.', exist_ok=True)
        shutil.move(path_from, path_to)
        _log_event('move', 'ok', {'from': path_from, 'to': path_to})
        return f"Moved to: {path_to}"
    except Exception as e:
        _log_event('move', 'error', {'from': path_from, 'to': path_to, 'error': str(e)})
        return f"Failed to move: {e}"


def rename(path: str, new_name: str) -> str:
    base = os.path.dirname(path)
    dest = os.path.join(base, new_name)
    return move(path, dest)


def list_dir(path: str) -> str:
    if not verify_file_operation('list_dir', path):
        return "Operation cancelled."
    try:
        entries = os.listdir(path)
        _log_event('list_dir', 'ok', {'path': path, 'count': len(entries)})
        if not entries:
            return "(empty)"
        return "\n".join(entries)
    except Exception as e:
        _log_event('list_dir', 'error', {'path': path, 'error': str(e)})
        return f"Failed to list: {e}"


def delete(path: str) -> str:
    if not verify_file_operation('delete', path):
        return "Operation cancelled."
    try:
        if os.path.isdir(path):
            shutil.rmtree(path)
        elif os.path.isfile(path):
            os.remove(path)
        else:
            return "Nothing to delete."
        _log_event('delete', 'ok', {'path': path})
        return f"Deleted: {path}"
    except Exception as e:
        _log_event('delete', 'error', {'path': path, 'error': str(e)})
        return f"Failed to delete: {e}"
