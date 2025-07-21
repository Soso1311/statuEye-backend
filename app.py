from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from dotenv import load_dotenv
import replicate
import os

# Load environment variables from .env
load_dotenv()

# Get the Replicate API token from environment variables
REPLICATE_API_TOKEN = os.getenv("REPLICATE_API_TOKEN")
if not REPLICATE_API_TOKEN:
    raise RuntimeError("REPLICATE_API_TOKEN not found in environment variables.")

# Create a Replicate client
replicate_client = replicate.Client(api_token=REPLICATE_API_TOKEN)

# Initialize FastAPI app
app = FastAPI()

# Allow all CORS (mobile apps, web clients)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Define request format
class Query(BaseModel):
    question: str
    session_id: str

# Define the /analyze route
@app.post("/analyze")
async def analyze(query: Query):
    prompt = f"You are a helpful legal assistant. A user says: {query.question}"

    try:
        # Use the Mixtral model from Replicate (no version ID needed)
        output = replicate_client.run(
            "mistralai/mixtral-8x7b-instruct-v0.1",
            input={
                "prompt": prompt,
                "max_new_tokens": 500,
                "temperature": 0.7
            }
        )

        # Return AI response
        return {"response": "".join(output)}

    except Exception as e:
        # Handle any errors
        return {"error": f"Model call failed: {str(e)}"}
