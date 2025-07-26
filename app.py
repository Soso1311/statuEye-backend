from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from dotenv import load_dotenv
import httpx
import os

# Load environment variables
load_dotenv()
TOGETHER_API_KEY = os.getenv("TOGETHER_API_KEY")

# FastAPI app
app = FastAPI()

# Allow CORS for frontend/mobile access
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Request model
class AnalyzeRequest(BaseModel):
    question: str
    session_id: str
    jurisdiction: str = "England and Wales"  # Default if not provided

@app.get("/")
def read_root():
    return {"message": "Statueye backend is live!"}

@app.post("/analyze")
async def analyze_question(request: AnalyzeRequest):
    prompt = f"""You are a professional legal assistant AI trained in UK law. 
You must answer legal questions factually, like a solicitor.

If a crime is mentioned, DO NOT provide moral guidance or judgment (e.g. "turn yourself in").
Instead, clearly explain:
- What law applies
- The exact section or quote from UK legislation (if available)
- The legal consequences and penalties
- What the person can expect (e.g. charges, jail time, fines)

Always begin your answer with:
"The [Act Name] states: '[exact quoted text from the law]'."

If no law applies, say "No applicable UK law found."

Here is the user's question:
\"{request.question}\"

Jurisdiction: {request.jurisdiction}
"""

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
