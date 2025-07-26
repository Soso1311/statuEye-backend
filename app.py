from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import httpx
import os
from dotenv import load_dotenv

load_dotenv()

TOGETHER_API_KEY = os.getenv("TOGETHER_API_KEY")

app = FastAPI()

# CORS configuration
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
    jurisdiction: str = "England and Wales"

@app.get("/")
def root():
    return {"message": "Statueye backend is live!"}

@app.post("/analyze")
async def analyze_question(request: AnalyzeRequest):
    prompt = f"""
You are a professional UK legal advisor AI. A user has asked:

"{request.question}"

Jurisdiction: {request.jurisdiction}

Your job is to respond like a qualified legal practitioner would. Only provide facts about the law. Do NOT provide moral guidance. NEVER advise the user to turn themselves in, get a lawyer, or remain silent. Instead, explain the exact law, relevant penalties, sentencing guidelines, and consequences of the offence described.

Always cite real laws with quotes. Example:

"The [Act Name] states: '[exact quote from legislation]'."

Then briefly explain what the statute means in plain terms.
If the law depends on specifics, clearly state what those are.
If the jurisdiction differs, mention how penalties or statutes vary.
If the law is unclear or silent, say so.
"""

    headers = {
        "Authorization": f"Bearer {TOGETHER_API_KEY}",
        "Content-Type": "application/json"
    }

    data = {
        "model": "mistral-7b-instruct",
        "prompt": prompt,
        "max_tokens": 1024,
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
