from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from dotenv import load_dotenv
import replicate
import os

load_dotenv()

REPLICATE_API_TOKEN = os.getenv("REPLICATE_API_TOKEN")
if not REPLICATE_API_TOKEN:
    raise RuntimeError("REPLICATE_API_TOKEN not found in environment variables.")

# Initialize Replicate client
replicate_client = replicate.Client(api_token=REPLICATE_API_TOKEN)

# FastAPI app setup
app = FastAPI()

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Input schema
class Query(BaseModel):
    question: str
    session_id: str

# POST /analyze endpoint
@app.post("/analyze")
async def analyze(query: Query):
    try:
        prompt = query.question

        output = replicate.run(
            "meta/meta-llama-3-70b-instruct:84f6a9d99b7d1a44a9b3e032116d7e7b118755a0b1984e3d45f44b02560b46d9",
            input={
                "prompt": f"You are a helpful legal assistant. A user asks: {prompt}",
                "temperature": 0.7,
                "top_p": 0.9,
                "max_new_tokens": 500
            }
        )

        return {"response": "".join(output)}
    
    except Exception as e:
        return {"error": f"Model call failed: {str(e)}"}

