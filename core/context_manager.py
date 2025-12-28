from typing import Dict, Any, List, Tuple
from memory.short_term import ShortTermMemory
from memory.long_term import LongTermMemory
from memory.affect import detect_affect

class ContextManager:
    def __init__(self, short_window: int = 8):
        self.stm = ShortTermMemory(max_turns=short_window)
        self.ltm = LongTermMemory()

    def push_user(self, text: str):
        self.stm.push_user(text)

    def push_assistant(self, text: str):
        self.stm.push_assistant(text)

    def build_context(self, user_input: str) -> Dict[str, Any]:
        # Affect
        affect = detect_affect(user_input)
        # Long-term retrieval using the query
        ltm_hits = self.ltm.retrieve(user_input, top_k=5)
        # Short-term window
        window = self.stm.get_window()
        return {
            'affect': affect,
            'short_term': [{'role': r, 'content': c} for r, c in window],
            'long_term': ltm_hits,
        }
