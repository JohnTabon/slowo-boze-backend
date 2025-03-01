from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import openai
import os
from fastapi.middleware.cors import CORSMiddleware

# Load API key (set this in your environment variables)
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# Initialize FastAPI app
app = FastAPI()

# Allow frontend to connect
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Request model
class ChatRequest(BaseModel):
    text: str

@app.post("/chat")
def chat_with_ai(request: ChatRequest):
    try:
        client = openai.OpenAI(api_key=OPENAI_API_KEY)  # Initialize OpenAI client

        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": "Jesteś asystentem duchowym o nazwie Słowo Boże. Odpowiadasz tylko po polsku, udzielając wskazówek biblijnych, modlitw i mądrości duchowej."},
                {"role": "user", "content": request.text}
            ],
            temperature=0.7
        )

        return {"reply": response.choices[0].message.content}
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ✅ Define the root `/` route
@app.get("/")
def read_root():
    return {"message": "Słowo Boże API is running."}
