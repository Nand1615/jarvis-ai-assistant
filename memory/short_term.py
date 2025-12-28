from collections import deque
from typing import Deque, Dict, List, Tuple

# Maintains a short-term dialogue memory per session

class ShortTermMemory:
    def __init__(self, max_turns: int = 8):
        self.max_turns = max_turns
        self.buffer: Deque[Tuple[str, str]] = deque(maxlen=max_turns)  # (role, content)

    def push_user(self, text: str):
        self.buffer.append(("user", text))

    def push_assistant(self, text: str):
        self.buffer.append(("assistant", text))

    def get_window(self) -> List[Tuple[str, str]]:
        return list(self.buffer)

    def clear(self):
        self.buffer.clear()
