from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import requests
import os
from dotenv import load_dotenv

load_dotenv()

TOGETHER_API_KEY = os.getenv("c09e7c90e1732762833e76d19f4d79cc5b97eec1177ab35ccf24039994fa0122")

app = FastAPI()

# CORS for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # you can restrict this to your domain
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class QuestionRequest(BaseModel):
    question: str
    session_id: str = "default"

@app.post("/analyze")
async def analyze_question(req: QuestionRequest):
    headers = {
        "Authorization": f"Bearer {TOGETHER_API_KEY}",
        "Content-Type": "application/json"
    }

    payload = {
        "model": "mistralai/Mixtral-8x7B-Instruct-v0.1",
        "prompt": f"You are a UK legal expert AI. Answer this legal question like a human lawyer would:\n\nQuestion: {req.question}\n\nAnswer:",
        "max_tokens": 512,
        "temperature": 0.7,
        "top_p": 0.9,
    }

    res = requests.post("https://api.together.xyz/v1/completions", headers=headers, json=payload)

    if res.status_code != 200:
        return {"error": f"Model call failed: {res.text}"}

    data = res.json()
    answer = data.get("choices", [{}])[0].get("text", "").strip()
    return {"answer": answer}
