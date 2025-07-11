from fastapi import FastAPI, Request
from pydantic import BaseModel
import httpx
import asyncio
import ipinfo

app = FastAPI()

# Memory store per user
session_memory = {}

# IPInfo token (public demo, optional — for production use your token)
ipinfo_handler = ipinfo.getHandler()  # If you have a token: ipinfo.getHandler("your_token_here")

class Query(BaseModel):
    question: str
    session_id: str

@app.post("/analyze")
async def analyze(query: Query, request: Request):
    user_input = query.question.strip()
    session_id = query.session_id.strip()

    # 🧠 Store memory
    if session_id not in session_memory:
        session_memory[session_id] = []
    session_memory[session_id].append(f"User: {user_input}")

    # 📍 Detect user IP location
    client_ip = request.client.host
    try:
        details = ipinfo_handler.getDetails(client_ip)
        country = details.country_name or "UK"
    except:
        country = "UK"

    # 🧵 Build context-aware memory prompt
    memory_context = "\n".join(session_memory[session_id][-10:])  # last 10 turns

    prompt = (
        f"You are a helpful, compassionate legal assistant AI.\n"
        f"The user is likely in: {country}.\n"
        f"Below is your conversation history:\n{memory_context}\n\n"
        "If the user's situation lacks critical info (like location, timeline, age, evidence, relationship), "
        "ask follow-up questions one at a time. Do not proceed until you understand the context.\n\n"
        "Once ready, clearly explain:\n"
        "1. What law(s) may have been broken\n"
        "2. The potential penalties\n"
        "3. What the user should do next (police, legal aid, evidence, etc)\n\n"
        "Always respond in a calm, clear, and empathetic tone, using plain language.\n\n"
        "AI:"
    )

    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(
                "http://localhost:11434/api/generate",
                json={
                    "model": "mistral",
                    "prompt": prompt,
                    "stream": False
                },
                timeout=60.0
            )
        except Exception as e:
            return {"error": f"Model call failed: {str(e)}"}

    if response.status_code == 200:
        try:
            result = response.json()
            ai_reply = result["response"].strip()
            session_memory[session_id].append(f"AI: {ai_reply}")
            return {"response": ai_reply}
        except Exception:
            return {"error": "AI returned unreadable response"}
    else:
        return {"error": f"Model returned error {response.status_code}"}
