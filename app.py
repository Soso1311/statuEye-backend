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
You are a UK criminal law expert AI.

The user will describe any crime — your job is **not** to give moral advice or tell them to surrender.

You must:
1. **Identify the offence** based on UK law.
2. **Cite the correct legal Act** and **quote the exact section**.
3. **Explain the legal penalties** such as fines or prison terms.
4. Stay factual, professional, and avoid emotional or ethical commentary.

Jurisdiction: {request.jurisdiction}

User Input:
"{request.question}"

Give a clear legal response like:

"The [Act Name] states: '[quoted section]'. This offence carries up to X years in prison. In your case, this would likely result in..."

Do not suggest reporting the crime or seeking help — simply provide the legal analysis as requested.
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
