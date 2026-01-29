from fastapi import FastAPI, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import httpx
import os
import redis
from typing import Optional

app = FastAPI()

# CORS for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Replace with your domain in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Define input model
class AnalyzeRequest(BaseModel):
    question: str
    session_id: str = "default"

# Redis Connection
redis_client = redis.Redis(host='localhost', port=6379, db=0)  # Adjust as needed

# Load OpenRouter API key from Railway environment variable (Not needed)
# OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")


# Define a simple prompt – highly focused
prompt = """
You are a legal assistant AI.  A user asks:

"{question}"

Respond with the **most relevant legal concept or phrase** related to the question, without lengthy explanations or legal advice.

If no legal concept is apparent, respond with "No legal concept found."
"""


@app.post("/analyze")
async def analyze_question(req: AnalyzeRequest):
    cache_key = f"legal_analysis:{req.session_id}:{req.question}"

    # Check cache
    cached_result = redis_client.get(cache_key)
    if cached_result:
        return {"answer": cached_result.decode("utf-8")}

    # Call Together AI
    headers = {
        "Content-Type": "application/json"
    }
    payload = {
        "model": "mistralai/mixtral-8x7b-instruct-v0.1",
        "messages": [
            {"role": "system", "content": "You are a legal assistant AI."},
            {"role": "user", "content": prompt.format(question=req.question)}
        ],
        "temperature": 0.0, # Keep low for fast responses
        "max_tokens": 128  # Limit token usage significantly
    }

    try:
        response = await httpx.post("https://api.together.xyz/v1/completions", headers=headers, json=payload)
        response.raise_for_status()
        result = response.json()
        answer = result["choices"][0]["message"]["content"].strip()

        # Store in cache
        redis_client.setex(cache_key, 600, answer)  # Cache for 10 minutes

        return {"answer": answer}

    except Exception as e:
        print(f"Error: {e}")
        raise HTTPException(status_code=500, detail="Failed to analyze question")
