from openai import OpenAI
import re, json
from app.config import OPENAI_API_KEY

openai_client = OpenAI(api_key=OPENAI_API_KEY)

def call_openai(prompt: str) -> dict:
    response = openai_client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": "You are a JSON generator. Output only JSON."},
            {"role": "user", "content": prompt}
        ],
        temperature=0
    )
    raw = response.choices[0].message.content
    clean = re.sub(r"^```json|```$", "", raw, flags=re.MULTILINE).strip()
    return json.loads(clean)
