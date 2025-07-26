from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import httpx
import os
from dotenv import load_dotenv

load_dotenv()

TOGETHER_API_KEY = os.getenv("TOGETHER_API_KEY")
if not TOGETHER_API_KEY:
    raise RuntimeError("TOGETHER_API_KEY not found")

app = FastAPI()

# CORS setup
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

class AnalyzeRequest(BaseModel):
    question: str
    session_id: str
    jurisdiction: str = "England and Wales"

@app.get("/")
def read_root():
    return {"message": "Statueye backend is live!"}

@app.post("/analyze")
async def analyze_question(request: AnalyzeRequest):
    prompt = f"""You are a UK legal assistant AI. A user in {request.jurisdiction} asks:

"{request.question}"

Your job is to give a detailed legal answer. 
- DO NOT tell the user to turn themselves in.
- DO NOT give moral advice.
- Always act like a professional solicitor.
- Focus only on the law, penalties, and what the Act says.

If relevant, cite the actual law like this:
"The [Act Name] states: '[quoted law text]'."

Then explain what it means in simple terms and what penalty applies under that law.

If you don't know or it's not covered in UK law, say so clearly."""

    headers = {
        "Authorization": f"Bearer {TOGETHER_API_KEY}",
        "Content-Type": "application/json"
    }

    data = {
        "model": "mistral-7b-instruct",
        "prompt": prompt,
        "max_tokens": 900,
        "temperature": 0.6,
        "top_p": 0.9
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
