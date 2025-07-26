from fastapi import FastAPI, Request
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
import httpx
import os

TOGETHER_API_KEY = os.getenv("TOGETHER_API_KEY")

app = FastAPI()

# CORS settings
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Set to frontend URL in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Define the request body
class AnalyzeRequest(BaseModel):
    question: str
    session_id: str
    jurisdiction: str = "England and Wales"  # default

@app.get("/")
def read_root():
    return {"message": "Statueye backend is live!"}

@app.post("/analyze")
async def analyze_question(request: AnalyzeRequest):
    prompt = f"""You are a legal assistant AI for UK law. A user has asked:

"{request.question}"

Jurisdiction: {request.jurisdiction}

Answer with clear legal advice and **always cite the relevant law** like:

"The [Act Name] states: '[exact quoted law]'."

Then briefly explain what it means and what the user should do next.
Only cite real UK laws — if unsure, say so honestly."""

    headers = {
        "Authorization": f"Bearer {TOGETHER_API_KEY}",
        "Content-Type": "application/json"
    }

    data = {
        "model": "mistral-7b-instruct",
        "prompt": prompt,
        "max_tokens": 800,
        "temperature": 0.7
    }

    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                "https://api.together.xyz/v1/completions",
                headers=headers,
                json=data
            )

        response_json = response.json()
        ai_text = response_json["choices"][0]["text"].strip()
        return {"response": ai_text}

    except Exception as e:
        return {"error": f"Model call failed: {str(e)}"}
