import json
import re
import sqlite3
from pathlib import Path

from models.item import Item
from storage.base_storage import BaseStorage


class DBStorage(BaseStorage):
    """SQLite backend: mỗi item lưu dạng JSON.

    Mở rộng cho Crawler:
    - Cột `url` có UNIQUE constraint -> `INSERT OR IGNORE` sẽ tự bỏ qua nếu url đã tồn tại,
      an toàn ngay cả khi visited-set trong RAM (Engine.visited) bị mất do restart giữa chừng.
    - `has_url()` cho phép Engine kiểm tra 1 URL đã crawl ở lần chạy TRƯỚC chưa, để crawl
      tiếp (resume) mà không phải làm lại từ đầu.
    """

    def __init__(self, config=None):
        super().__init__(config or {})
        get = self.config.get if hasattr(self.config, "get") else dict(self.config or {}).get
        self.path = Path(get("DB_PATH", get("path", "items.sqlite3")))
        self.table = get("DB_TABLE", "items")
        if not re.fullmatch(r"[A-Za-z_][A-Za-z0-9_]*", self.table):
            raise ValueError("DB_TABLE must be a valid SQLite identifier")

    def connect(self):
        self.path.parent.mkdir(parents=True, exist_ok=True)
        connection = sqlite3.connect(self.path)
        connection.execute(
            f"""CREATE TABLE IF NOT EXISTS {self.table} (
                id INTEGER PRIMARY KEY,
                url TEXT UNIQUE,
                data TEXT NOT NULL,
                crawled_at TEXT DEFAULT CURRENT_TIMESTAMP
            )"""
        )
        return connection

    def save(self, item):
        record = item.to_dict() if isinstance(item, Item) else dict(item)
        url = record.get("url")
        connection = self.connect()
        try:
            cursor = connection.execute(
                f"INSERT OR IGNORE INTO {self.table} (url, data) VALUES (?, ?)",
                (url, json.dumps(record, ensure_ascii=False, default=str)),
            )
            connection.commit()
            return cursor.lastrowid
        finally:
            connection.close()

    def has_url(self, url):
        """True nếu url này đã được crawl (ở lần chạy này hoặc lần trước, vì DB persistent)."""
        connection = self.connect()
        try:
            cursor = connection.execute(f"SELECT 1 FROM {self.table} WHERE url = ? LIMIT 1", (url,))
            return cursor.fetchone() is not None
        finally:
            connection.close()

    def all_urls(self):
        """Lấy toàn bộ url đã lưu -> dùng để nạp lại vào Engine.visited khi resume crawl."""
        connection = self.connect()
        try:
            cursor = connection.execute(f"SELECT url FROM {self.table} WHERE url IS NOT NULL")
            return {row[0] for row in cursor.fetchall()}
        finally:
            connection.close()


DbStorage = DBStorage
