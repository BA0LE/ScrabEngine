from abc import ABC, abstractmethod


class BaseStorage(ABC):
    def __init__(self, config):
        self.config = config

    @abstractmethod
    def save(self, item):
        raise NotImplementedError
