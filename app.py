from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from dotenv import load_dotenv
import replicate
import os

load_dotenv()

REPLICATE_API_TOKEN = os.getenv("REPLICATE_API_TOKEN")
if not REPLICATE_API_TOKEN:
    raise RuntimeError("REPLICATE_API_TOKEN not found in environment variables.")

replicate_client = replicate.Client(api_token=REPLICATE_API_TOKEN)

app = FastAPI()

# Allow mobile apps to connect
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

class Query(BaseModel):
    question: str
    session_id: str

@app.post("/analyze")
async def analyze(query: Query):
    prompt = f"You are a helpful legal assistant. A user says: {query.question}"
    try:
        output = replicate_client.run(
            "mistralai/mistral-7b-instruct-v0.1",
            input={"prompt": prompt, "max_new_tokens": 500}
        )
        return {"response": "".join(output)}
    except Exception as e:
        return {"error": f"Model call failed: {str(e)}"}
