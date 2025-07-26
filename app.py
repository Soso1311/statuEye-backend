from fastapi import FastAPI
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
import httpx
import os

# Load OpenRouter API key from Railway environment variable
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")

app = FastAPI()

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Replace with frontend domain in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Define input model
class AnalyzeRequest(BaseModel):
    question: str
    session_id: str
    jurisdiction: str = "England"

# Root route
@app.get("/")
def read_root():
    return {"message": "Statueye backend running with OpenRouter"}

# Analyze route
@app.post("/analyze")
async def analyze_question(request: AnalyzeRequest):
    prompt = f"""
You are a UK legal assistant AI. A user asks:

"{request.question}"

The jurisdiction is: {request.jurisdiction}

Respond like a professional legal advisor in the UK.

Always follow this structure:
1. **Quote the exact relevant UK law**, using full act names and sections (e.g. "The Sexual Offences Act 2003, Section 1 states: '...'").
2. **Clearly explain the meaning of the law in plain English**.
3. **State the legal penalty or consequence**, including typical sentences.
4. Do **not** give moral or ethical advice, only legal consequences.
5. Be factual, detailed, and serious in tone. Never refer to yourself as an AI.
6. If a law is unclear or context is missing, ask a brief follow-up question.

Only cite real UK legislation. If no law applies, say “There is no known UK law that applies.”
"""

    headers = {
        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
        "Content-Type": "application/json"
    }

    payload = {
        "model": "mistralai/mistral-7b-instruct:free",  # Free, fast, no filter
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
