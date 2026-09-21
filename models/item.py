"""Data object passed between parsers, pipelines, and storage backends."""

from collections.abc import Mapping
from copy import deepcopy


class Item:
    def __init__(self, data: Mapping | None = None, **fields):
        if data is not None and not isinstance(data, Mapping):
            raise TypeError("data must be a mapping or None")
        self.data = dict(data or {})
        self.data.update(fields)

    def get(self, key, default=None):
        return self.data.get(key, default)

    def to_dict(self):
        return deepcopy(self.data)

    def update(self, values: Mapping | None = None, **fields):
        if values is not None:
            self.data.update(values)
        self.data.update(fields)
        return self

    def __getitem__(self, key):
        return self.data[key]

    def __setitem__(self, key, value):
        self.data[key] = value

    def __contains__(self, key):
        return key in self.data

    def __repr__(self):
        return f"Item({self.data!r})"
