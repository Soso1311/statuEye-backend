from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from dotenv import load_dotenv
import replicate
import os

# Load environment variables (for local testing)
load_dotenv()

# Get Replicate API token
REPLICATE_API_TOKEN = os.getenv("REPLICATE_API_TOKEN")
if not REPLICATE_API_TOKEN:
    raise RuntimeError("REPLICATE_API_TOKEN not found in environment variables.")

replicate_client = replicate.Client(api_token=REPLICATE_API_TOKEN)

# Set up FastAPI app
app = FastAPI()

# Allow CORS (for mobile frontend)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Define input schema
class Query(BaseModel):
    question: str
    session_id: str

# Define analyze endpoint
@app.post("/analyze")
async def analyze(query: Query):
    prompt = f"You are a helpful legal assistant. A user says: {query.question}"

    try:
        # Use Mixtral 8x7B (stable public instruct model)
output = replicate.run(
    "mistralai/mixtral-8x7b-instruct-v0.1",
    input={
        "prompt": prompt,
        "max_new_tokens": 500,
        "temperature": 0.7
    }
)

        return {"response": "".join(output)}

    except Exception as e:
        return {"error": f"Model call failed: {str(e)}"}
