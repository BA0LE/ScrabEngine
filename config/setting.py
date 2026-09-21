"""Configuration helpers for the scraper's supporting components."""

from collections.abc import Mapping
from copy import deepcopy


class Setting:
    """Validated, dictionary-like settings with sensible defaults."""

    DEFAULTS = {"MAX_RETRIES": 3, "TIMEOUT": 10.0, "USER_AGENT": "ScrabEngine/1.0",
                "RATE_LIMIT": 1, "RATE_WINDOW": 1.0, "STORAGE_PATH": "items.json",
                "DB_PATH": "items.sqlite3", "DB_TABLE": "items"}

    def __init__(self, config: Mapping | None = None):
        if config is not None and not isinstance(config, Mapping):
            raise TypeError("config must be a mapping or None")
        self.config = deepcopy(self.DEFAULTS)
        self.config.update(dict(config or {}))
        self._validate()

    def _validate(self):
        if self.config["MAX_RETRIES"] < 0:
            raise ValueError("MAX_RETRIES must be non-negative")
        if self.config["TIMEOUT"] <= 0:
            raise ValueError("TIMEOUT must be greater than zero")
        if self.config["RATE_LIMIT"] <= 0 or self.config["RATE_WINDOW"] <= 0:
            raise ValueError("RATE_LIMIT and RATE_WINDOW must be greater than zero")

    def get(self, key, default=None):
        return self.config.get(key, default)

    def update(self, values: Mapping):
        previous = self.config.copy()
        self.config.update(values)
        try:
            self._validate()
        except Exception:
            self.config = previous
            raise

    def __getitem__(self, key):
        return self.config[key]


Settings = Setting

    
