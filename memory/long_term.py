import json
import os
import time
import math
from typing import List, Dict, Any, Optional, Tuple

# Simple long-term memory store with JSONL persistence and lightweight embedding via bag-of-words tf-idf-ish
# Falls back gracefully if no embedding backend. Stored under memory/long_term.jsonl and memory/embeddings.json

BASE_DIR = os.path.dirname(__file__)
STORE_PATH = os.path.join(BASE_DIR, 'long_term.jsonl')
EMB_PATH = os.path.join(BASE_DIR, 'embeddings.json')

# Types: fact | habit | task | preference | note

def _now() -> float:
    return time.time()


def _load_json(path: str, default):
    try:
        with open(path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception:
        return default


def _save_json(path: str, data):
    tmp = path + '.tmp'
    with open(tmp, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    os.replace(tmp, path)


def _ensure_file(path: str):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    if not os.path.exists(path):
        with open(path, 'w', encoding='utf-8') as f:
            pass

# Very lightweight tokenizer

def _tok(text: str) -> List[str]:
    return [t for t in ''.join(ch.lower() if ch.isalnum() else ' ' for ch in text).split() if t]


class LongTermMemory:
    def __init__(self):
        _ensure_file(STORE_PATH)
        self.embeddings: Dict[str, Dict[str, float]] = _load_json(EMB_PATH, {})
        self.df: Dict[str, int] = self._recompute_df()

    def _recompute_df(self) -> Dict[str, int]:
        df: Dict[str, int] = {}
        for entry in self.iter_all():
            seen = set(_tok(entry.get('text','')))
            for t in seen:
                df[t] = df.get(t, 0) + 1
        return df

    def iter_all(self):
        try:
            with open(STORE_PATH, 'r', encoding='utf-8') as f:
                for line in f:
                    line = line.strip()
                    if not line:
                        continue
                    try:
                        yield json.loads(line)
                    except Exception:
                        continue
        except Exception:
            return

    def _write_entry(self, entry: Dict[str, Any]):
        with open(STORE_PATH, 'a', encoding='utf-8') as f:
            f.write(json.dumps(entry, ensure_ascii=False) + '\n')

    def add(self, text: str, mtype: str = 'note', tags: Optional[List[str]] = None, source: str = 'user', extra: Optional[Dict[str, Any]] = None) -> str:
        eid = f"mem_{int(_now()*1000)}"
        entry = {
            'id': eid,
            'type': mtype,
            'text': text.strip(),
            'tags': tags or [],
            'created_at': _now(),
            'last_seen': _now(),
            'source': source,
        }
        if extra:
            entry.update(extra)
        self._write_entry(entry)
        self._embed_entry(entry)
        # update df cache
        for t in set(_tok(entry['text'])):
            self.df[t] = self.df.get(t, 0) + 1
        return eid

    def _embed_entry(self, entry: Dict[str, Any]):
        # Compute simple tf-idf-like vector
        tokens = _tok(entry.get('text',''))
        if not tokens:
            return
        tf: Dict[str, float] = {}
        for t in tokens:
            tf[t] = tf.get(t, 0.0) + 1.0
        for t in tf:
            tf[t] /= len(tokens)
        vec: Dict[str, float] = {}
        for t, v in tf.items():
            idf = 1.0 / (1.0 + self.df.get(t, 0))
            vec[t] = v * idf
        self.embeddings[entry['id']] = vec
        _save_json(EMB_PATH, self.embeddings)

    def _embed_query(self, text: str) -> Dict[str, float]:
        tokens = _tok(text)
        if not tokens:
            return {}
        tf: Dict[str, float] = {}
        for t in tokens:
            tf[t] = tf.get(t, 0.0) + 1.0
        for t in tf:
            tf[t] /= len(tokens)
        vec: Dict[str, float] = {}
        for t, v in tf.items():
            idf = 1.0 / (1.0 + self.df.get(t, 0))
            vec[t] = v * idf
        return vec

    @staticmethod
    def _cosine(a: Dict[str, float], b: Dict[str, float]) -> float:
        if not a or not b:
            return 0.0
        dot = 0.0
        for k, v in a.items():
            dot += v * b.get(k, 0.0)
        na = math.sqrt(sum(v*v for v in a.values()))
        nb = math.sqrt(sum(v*v for v in b.values()))
        if na == 0 or nb == 0:
            return 0.0
        return dot / (na * nb)

    def retrieve(self, query: str, tags: Optional[List[str]] = None, top_k: int = 5) -> List[Dict[str, Any]]:
        qv = self._embed_query(query)
        results: List[Tuple[float, Dict[str, Any]]] = []
        tagset = set([t.lower() for t in (tags or [])])
        for entry in self.iter_all():
            if tags:
                etags = set([t.lower() for t in entry.get('tags', [])])
                if not tagset.intersection(etags):
                    continue
            ev = self.embeddings.get(entry['id'])
            sim = self._cosine(qv, ev) if ev else 0.0
            # small bonus for type preference
            if 'type' in entry and entry['type'] in ('preference','habit'):
                sim += 0.05
            if sim > 0:
                results.append((sim, entry))
        results.sort(key=lambda x: x[0], reverse=True)
        return [e for _, e in results[:top_k]]

    def update_last_seen(self, entry_id: str):
        # Append an update line to preserve immutability; simple approach: rewrite file
        entries = list(self.iter_all())
        for e in entries:
            if e['id'] == entry_id:
                e['last_seen'] = _now()
        with open(STORE_PATH, 'w', encoding='utf-8') as f:
            for e in entries:
                f.write(json.dumps(e, ensure_ascii=False) + '\n')

    def add_or_update_preference(self, key: str, value: str, tags: Optional[List[str]] = None):
        # If a preference with same key exists, add a new entry marking it updated
        text = f"preference:{key}={value}"
        return self.add(text=text, mtype='preference', tags=(tags or [key]))
