from abc import ABC, abstractmethod


class BaseParser(ABC):
    def __init__(self, config):
        self.config = config

    @abstractmethod
    def parse(self, data):
        """Convert fetched data into an item or an iterable of items."""
        raise NotImplementedError
