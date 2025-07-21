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
            "meta/llama-2-70b-chat:8bb2f8f2b8c646f8b3e4f2c62f16373693164f4cbaf0c1dcab6aa87fdf6f68b3",
            input={
                "prompt": prompt,
                "temperature": 0.7,
                "max_new_tokens": 500,
                "system_prompt": "You are a helpful legal assistant."
            }
        )

        return {"response": "".join(output)}
    
    except Exception as e:
        return {"error": f"Model call failed: {str(e)}"}
