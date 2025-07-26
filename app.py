from fastapi import FastAPI
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
import httpx
import os
from typing import Dict, List

# Load Together API key
TOGETHER_API_KEY = os.getenv("TOGETHER_API_KEY")

app = FastAPI()

# CORS setup
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # update in prod
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Request model
class AnalyzeRequest(BaseModel):
    question: str
    session_id: str
    jurisdiction: str = "England and Wales"

# Memory store
conversations: Dict[str, List[Dict[str, str]]] = {}

# Root route
@app.get("/")
def read_root():
    return {"message": "Statueye backend is live with memory!"}

# Analyze route with memory
@app.post("/analyze")
async def analyze_question(request: AnalyzeRequest):
    session_id = request.session_id
    question = request.question
    jurisdiction = request.jurisdiction

    # Start new conversation if needed
    if session_id not in conversations:
        conversations[session_id] = []

    # Add user message
    conversations[session_id].append({
        "role": "user",
        "content": question
    })

    # System prompt
    system_prompt = {
        "role": "system",
        "content": (
            f"You are a legal assistant for UK law. Always cite UK laws exactly like this:\n"
            f"The [Act Name] states: \"...\".\n"
            f"You're advising a user in the {jurisdiction} jurisdiction. Keep answers clear, helpful, and accurate. "
            f"If unsure, say so clearly. Only follow up if absolutely needed."
        )
    }

    # Full message history
    full_messages = [system_prompt] + conversations[session_id]

    # Together.ai chat request
    headers = {
        "Authorization": f"Bearer {TOGETHER_API_KEY}",
        "Content-Type": "application/json"
    }

    payload = {
        "model": "mistralai/Mixtral-8x7B-Instruct-v0.1",
        "messages": full_messages,
        "max_tokens": 800,
        "temperature": 0.7
    }

    try:
        async with httpx.AsyncClient() as client:
            res = await client.post(
                "https://api.together.xyz/v1/chat/completions",
                headers=headers,
                json=payload
            )
        data = res.json()
        ai_response = data["choices"][0]["message"]["content"].strip()

        # Save AI response in memory
        conversations[session_id].append({
            "role": "assistant",
            "content": ai_response
        })

        return {"response": ai_response}

    except Exception as e:
        return {"error": f"Model call failed: {str(e)}"}
