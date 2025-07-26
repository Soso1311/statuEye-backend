from fastapi import FastAPI
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
import httpx
import os

# Load OpenRouter API key from Railway environment variables
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")

app = FastAPI()

# Enable CORS for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class AnalyzeRequest(BaseModel):
    question: str
    session_id: str
    jurisdiction: str = "England"

@app.post("/analyze")
async def analyze_question(request: AnalyzeRequest):
    prompt = f"""
You are a UK criminal defence solicitor AI. Respond like a professional human lawyer.

User: "{request.question}"
Jurisdiction: {request.jurisdiction}

Always reply with a clear legal explanation, including full quotes from UK legislation like:

"The [Act Name] states: '[exact quote]'."

Do NOT moralize. Just explain the legal consequences and penalties.
"""

    headers = {
        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
        "Content-Type": "application/json"
    }

    payload = {
        "model": "mistralai/mistral-7b-instruct:free",  # you can swap to another free model
        "messages": [
            {"role": "system", "content": "You are a UK legal expert AI."},
            {"role": "user", "content": prompt}
        ],
        "temperature": 0.7,
        "max_tokens": 800
    }

    try:
        async with httpx.AsyncClient() as client:
            res = await client.post("https://openrouter.ai/api/v1/chat/completions", headers=headers, json=payload)

        res.raise_for_status()
        result = res.json()
        answer = result["choices"][0]["message"]["content"]
        return {"answer": answer}

    except Exception as e:
        return {"error": f"Model call failed: {str(e)}"}
