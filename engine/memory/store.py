import sqlite3
from pathlib import Path

class MemoryStore:
    def __init__(self, path: str = "data/jelon.db"):
        Path(path).parent.mkdir(parents=True, exist_ok=True)
        self.db = sqlite3.connect(path)
        self.db.execute("CREATE TABLE IF NOT EXISTS memories (id INTEGER PRIMARY KEY, kind TEXT, content TEXT NOT NULL, created_at TEXT DEFAULT CURRENT_TIMESTAMP)")
        self.db.commit()

    def remember(self, kind: str, content: str) -> None:
        self.db.execute("INSERT INTO memories(kind, content) VALUES (?, ?)", (kind, content))
        self.db.commit()

    def recent(self, limit: int = 20) -> list[tuple]:
        return self.db.execute("SELECT kind, content, created_at FROM memories ORDER BY id DESC LIMIT ?", (limit,)).fetchall()
