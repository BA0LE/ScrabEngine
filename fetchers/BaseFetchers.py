from abc import ABC, abstractmethod

class BaseFetcher(ABC):
    def __init__(self, config):
        self.config = config

    @abstractmethod
    def fetch(self, URL):
        raise NotImplementedError