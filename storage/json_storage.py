import json
from pathlib import Path

from models.item import Item
from storage.base_storage import BaseStorage


class JsonStorage(BaseStorage):
    """Store items as a JSON array, creating the target directory if needed."""

    def __init__(self, config=None):
        super().__init__(config or {})
        self.path = Path(self.config.get("STORAGE_PATH", self.config.get("path", "items.json")))

    def save(self, item):
        record = item.to_dict() if isinstance(item, Item) else dict(item)
        self.path.parent.mkdir(parents=True, exist_ok=True)
        records = []
        if self.path.exists() and self.path.stat().st_size:
            with self.path.open("r", encoding="utf-8") as file:
                records = json.load(file)
            if not isinstance(records, list):
                raise ValueError("JSON storage file must contain an array")
        records.append(record)
        temporary = self.path.with_suffix(self.path.suffix + ".tmp")
        with temporary.open("w", encoding="utf-8") as file:
            json.dump(records, file, ensure_ascii=False, indent=2, default=str)
        temporary.replace(self.path)
        return record
