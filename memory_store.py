"""Append-only JSON memory store."""
import json
from pathlib import Path
from typing import Any, Dict, List


class MemoryStore:
    def __init__(self, condition: str):
        self.condition = condition
        self.entries: List[Dict[str, Any]] = []

    def append(self, turn: int, entry_type: str, content: str, injected: bool = False) -> None:
        self.entries.append({
            "turn": turn,
            "type": entry_type,
            "content": content,
            "injected": injected,
        })

    def get_context(self) -> str:
        parts = []
        for e in self.entries:
            tag = "[INJECTED MEMORY]" if e["injected"] else "[MEMORY]"
            parts.append(f"{tag} (turn {e['turn']}, {e['type']}): {e['content']}")
        return "\n".join(parts)

    def get_all(self) -> List[Dict[str, Any]]:
        return list(self.entries)

    def save(self, path: Path) -> None:
        with open(path, "w") as f:
            json.dump(self.entries, f, indent=2)
