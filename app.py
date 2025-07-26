from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import requests
import os

app = FastAPI()

# Allow all frontend origins (you can restrict this later)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# ✅ Load Together API key from environment
TOGETHER_API_KEY = os.getenv("TOGETHER_API_KEY")

# ✅ Root route
@app.get("/")
def read_root():
    return {"message": "Statueye backend is live"}

# ✅ Main AI analysis route
@app.post("/analyze")
async def analyze(request: Request):
    try:
        data = await request.json()
        question = data.get("question")
        session_id = data.get("session_id", "default-session")

        if not question:
            return JSONResponse(content={"error": "Missing question"}, status_code=400)

        # ✅ Call Together AI (chat model)
        headers = {
            "Authorization": f"Bearer {TOGETHER_API_KEY}",
            "Content-Type": "application/json"
        }

        payload = {
            "model": "mistralai/Mistral-7B-Instruct-v0.1",
            "messages": [
                {"role": "system", "content": "You are a helpful UK legal assistant."},
                {"role": "user", "content": question}
            ],
            "temperature": 0.7,
            "top_p": 0.7,
            "max_tokens": 512
        }

        response = requests.post(
            "https://api.together.xyz/v1/chat/completions",
            headers=headers,
            json=payload
        )

        if response.status_code != 200:
            return JSONResponse(
                content={"error": f"Model call failed: {response.text}"},
                status_code=500
            )

        result = response.json()
        answer = result['choices'][0]['message']['content']

        return {"response": answer}

    except Exception as e:
        return JSONResponse(content={"error": str(e)}, status_code=500)
