import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from together import Together

app = FastAPI()

# Allow frontend to connect
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Input model
class Query(BaseModel):
    question: str
    session_id: str

# Load API key from env
together_api_key = os.getenv("TOGETHER_API_KEY")
client = Together(api_key=together_api_key)

@app.post("/analyze")
async def analyze(query: Query):
    prompt = (
        "You are a helpful UK legal assistant. The user says:\n"
        f"{query.question}\n\n"
        "Please:\n"
        "1. Explain any laws involved\n"
        "2. List penalties (if any)\n"
        "3. Suggest next steps\n\n"
        "Use clear, kind language."
    )

    try:
        response = await client.chat.completions.create(
            model="deepseek-ai/DeepSeek-R1",
            messages=[{"role": "user", "content": prompt}],
            stream=False
        )
        return {"response": response.choices[0].message.content}
    except Exception as e:
        return {"error": f"Model call failed: {str(e)}"}
