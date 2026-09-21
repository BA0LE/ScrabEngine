import time
from collections import deque
import asyncio

class RateLimiter:
    def __init__(self, 
                 max_requests: int, #maximum number of requests allowed 
                 time_window=1.0 #time window in seconds
                 ):
        self.max_requests = max_requests
        self.time_window = time_window
        if max_requests <= 0 or time_window <= 0:
            raise ValueError("max_requests and time_window must be greater than zero")
        self.request_times = deque()

    def set_delay(self, delay: float):
        if delay <= 0:
            raise ValueError("delay must be greater than zero")
        self.time_window = delay

    def is_allowed(self) -> bool:
        current_time = time.time()
        # Remove requests that are outside the time window
        while self.request_times and current_time - self.request_times[0] >= self.time_window:
            self.request_times.popleft()
        
        if len(self.request_times) < self.max_requests:
            self.request_times.append(current_time)
            return True
        return False

    async def wait(self, domain=None):
        while not self.is_allowed():
            sleep_for = self.time_window - (time.time() - self.request_times[0])
            asyncio.sleep(max(0.001, sleep_for))
        return True
