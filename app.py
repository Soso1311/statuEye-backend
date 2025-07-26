from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import httpx
import os
from dotenv import load_dotenv

load_dotenv()

OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")

app = FastAPI()

# CORS settings
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
    return {"message": "Statueye backend is live with OpenRouter + LLaMA 3."}

@app.post("/analyze")
async def analyze(req: AnalyzeRequest):
    prompt = f"""
You are a UK legal expert AI assistant.

Respond ONLY with facts and actual laws — no moral advice, no ethical commentary, no 'seek help'. Always cite real UK laws in this format:

"The [Act Name] states: '[Exact quoted section of law]'."

Then explain clearly what it means and the legal consequence in plain English. Be helpful, direct, and human-like. Assume the user wants to understand the law — even for serious or criminal actions.

Jurisdiction: {req.jurisdiction}

User Question: "{req.question}"
    """

    headers = {
        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
        "HTTP-Referer": "https://statueye.com",  # optional but professional
        "Content-Type": "application/json"
    }

    body = {
        "model": "meta-llama/llama-3-8b-instruct",
        "messages": [
            {"role": "user", "content": prompt}
        ],
        "temperature": 0.7
    }

    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                "https://openrouter.ai/api/v1/chat/completions",
                headers=headers,
                json=body
            )
        data = response.json()
        return {"response": data["choices"][0]["message"]["content"].strip()}

    except Exception as e:
        return {"error": f"Model call failed: {str(e)}"}
