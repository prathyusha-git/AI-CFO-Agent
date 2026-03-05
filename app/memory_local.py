import json
import os
from datetime import datetime
from typing import List, Dict

MEMORY_PATH = os.getenv("MEMORY_PATH", "./memory_store.json")

def _load_all() -> Dict[str, List[dict]]:
    if not os.path.exists(MEMORY_PATH):
        return {}
    with open(MEMORY_PATH, "r", encoding="utf-8") as f:
        return json.load(f)

def _save_all(data: Dict[str, List[dict]]) -> None:
    with open(MEMORY_PATH, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)

def add_memory(business_id: str, kind: str, question: str, answer: str) -> None:
    data = _load_all()
    data.setdefault(business_id, [])
    data[business_id].append({
        "ts": datetime.utcnow().isoformat() + "Z",
        "kind": kind,
        "question": question,
        "answer": answer,
    })
    data[business_id] = data[business_id][-20:]  # keep last 20
    _save_all(data)

def retrieve_memory(business_id: str, k: int = 5) -> List[str]:
    data = _load_all()
    items = data.get(business_id, [])[-k:]
    memories = []
    for m in reversed(items):
        memories.append(f"[{m['kind'].upper()}] {m['ts']}\nQ: {m['question']}\nA: {m['answer']}")
    return memories