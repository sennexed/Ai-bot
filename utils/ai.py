import os
from groq import Groq

client = Groq(api_key=os.getenv("GROQ_API_KEY"))

async def moderate(content, strictness):
    prompt = f"""
    Analyze this message for toxicity.
    Return JSON with:
    toxicity (0-100),
    category,
    explanation.

    Message:
    {content}
    """

    response = client.chat.completions.create(
        model="llama3-70b-8192",
        messages=[{"role": "user", "content": prompt}],
    )

    return response.choices[0].message.content
