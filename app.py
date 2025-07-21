from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from dotenv import load_dotenv
import replicate
import os

# Load environment variables
load_dotenv()
REPLICATE_API_TOKEN = os.getenv("REPLICATE_API_TOKEN")
if not REPLICATE_API_TOKEN:
    raise RuntimeError("REPLICATE_API_TOKEN not found in environment variables.")

app = FastAPI()

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
        output = replicate.run(
            "meta/llama-2-70b-chat:5b5b12b5f8e8c5363982df4e6ac2c0b8b77130a0f1540a0c040b27d5dfb3b1be",
            input={
                "prompt": prompt,
                "max_new_tokens": 500,
                "temperature": 0.7
            }
        )

        return {"response": "".join(output)}

    except Exception as e:
        return {"error": f"Model call failed: {str(e)}"}
