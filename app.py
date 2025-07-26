from fastapi import FastAPI
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
import httpx
import os

TOGETHER_API_KEY = os.getenv("TOGETHER_API_KEY")

app = FastAPI()

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# In-memory chat history
chat_sessions = {}

# Request body
class AnalyzeRequest(BaseModel):
    question: str
    session_id: str
    jurisdiction: str = "England and Wales"

@app.get("/")
def read_root():
    return {"message": "Statueye backend with memory is live!"}

@app.post("/analyze")
async def analyze_question(request: AnalyzeRequest):
    # Use or create chat history
    if request.session_id not in chat_sessions:
        chat_sessions[request.session_id] = []

    # Append user question
    chat_sessions[request.session_id].append({"role": "user", "content": request.question})

    # Build full prompt
    chat_history = "\n".join(
        f"{entry['role'].capitalize()}: {entry['content']}"
        for entry in chat_sessions[request.session_id]
    )

    prompt = f"""You are a helpful legal assistant AI with deep knowledge of UK law.

Jurisdiction: {request.jurisdiction}

Chat History:
{chat_history}

Now, based on the above, continue the conversation. 
If the user hasn't given enough detail, ask a short, useful follow-up question.
Always cite laws like: 'The [Act Name] states: "[quoted section]"' where appropriate.
Be concise, clear, and helpful."""

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

        # Add AI response to memory
        chat_sessions[request.session_id].append({"role": "assistant", "content": ai_text})

        return {"response": ai_text}

    except Exception as e:
        return {"error": f"Model call failed: {str(e)}"}
