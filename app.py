# app.py

from fastapi import FastAPI
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
import httpx
import os

# 🔒 Load your Together API key from environment
TOGETHER_API_KEY = os.getenv("TOGETHER_API_KEY")

# 🌍 FastAPI app
app = FastAPI()

# 🔐 CORS (allow frontend)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Replace with specific domain in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 🧠 Temporary in-memory session store
session_memory = {}

# 📦 Request format
class AnalyzeRequest(BaseModel):
    question: str
    session_id: str
    jurisdiction: str = "England and Wales"

@app.post("/analyze")
async def analyze_question(req: AnalyzeRequest):
    # ⏪ Fetch session history or start new
    history = session_memory.get(req.session_id, [])
    history.append(f"User: {req.question}")

    # 🧠 Combine memory into prompt
    memory_prompt = "\n".join(history)
    full_prompt = f"""
You are a helpful legal assistant for UK law.

Jurisdiction: {req.jurisdiction}

Chat history:
{memory_prompt}

Respond with clear legal advice, and always cite the actual law like:
"The [Act Name] states: '[exact legal quote]'."

Then explain what it means and what the user should do next.
If unsure, say so honestly.
"""

    headers = {
        "Authorization": f"Bearer {TOGETHER_API_KEY}",
        "Content-Type": "application/json"
    }

    payload = {
        "model": "mistral-7b-instruct",
        "prompt": full_prompt,
        "max_tokens": 800,
        "temperature": 0.7
    }

    try:
        async with httpx.AsyncClient() as client:
            res = await client.post(
                "https://api.together.xyz/v1/completions",
                headers=headers,
                json=payload
            )
            res.raise_for_status()
            data = res.json()
            answer = data["choices"][0]["text"].strip()
    except Exception as e:
        return {"error": f"Model call failed: {str(e)}"}

    # 💾 Update session memory
    history.append(f"AI: {answer}")
    session_memory[req.session_id] = history[-6:]  # Keep last 3 turns

    return {"response": answer}
