import os
import time
import asyncio
from groq import Groq

MODEL = "llama-3.1-8b-instant"
client = Groq(api_key=os.getenv("GROQ_API_KEY"))

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

limiter = RateLimiter()

async def moderate(content):
    await limiter.acquire()
    response = client.chat.completions.create(
        model=MODEL,
        messages=[
            {"role": "system", "content": "Reply ALLOW or DELETE | short reason"},
            {"role": "user", "content": content}
        ],
        temperature=0,
        max_tokens=20
    )
    return response.choices[0].message.content.strip()
