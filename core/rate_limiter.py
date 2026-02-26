import time
import asyncio

class RateLimiter:
    def __init__(self, max_calls=28, period=60):
        self.max_calls = max_calls
        self.period = period
        self.calls = []

    async def acquire(self):
        while True:
            now = time.time()
            self.calls = [c for c in self.calls if now - c < self.period]

            if len(self.calls) < self.max_calls:
                self.calls.append(now)
                return

            await asyncio.sleep(1)
