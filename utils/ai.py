import os
import aiohttp
import json

GROQ_API_KEY = os.getenv("GROQ_API_KEY")
MODEL = "llama3-70b-8192"

async def analyze_message(content):

    prompt = f"""
You are a moderation AI.

Score this message from 0 to 100 based on toxicity.
Return STRICT JSON:

{{
"severity": number,
"category": "type",
"explanation": "short explanation"
}}

Message:
{content}
"""

    headers = {
        "Authorization": f"Bearer {GROQ_API_KEY}",
        "Content-Type": "application/json"
    }

    payload = {
        "model": MODEL,
        "messages": [
            {"role": "user", "content": prompt}
        ],
        "temperature": 0.2
    }

    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(
                "https://api.groq.com/openai/v1/chat/completions",
                headers=headers,
                json=payload
            ) as resp:

                data = await resp.json()

                raw = data["choices"][0]["message"]["content"]

                parsed = json.loads(raw)

                return parsed

    except Exception:
        return {
            "severity": 0,
            "category": "error",
            "explanation": "AI failed"
        }


def strictness_threshold(level):
    mapping = {
        1: 80,
        2: 70,
        3: 60,
        4: 50,
        5: 40
    }
    return mapping.get(level, 60)
