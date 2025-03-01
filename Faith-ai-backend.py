from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import openai
import os
import stripe
import uvicorn
from fastapi.middleware.cors import CORSMiddleware

# ✅ Load API keys from environment variables
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
STRIPE_SECRET_KEY = os.getenv("STRIPE_SECRET_KEY")
stripe.api_key = STRIPE_SECRET_KEY

# ✅ Initialize FastAPI app
app = FastAPI()

# ✅ Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], 
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ✅ Test Route (For Debugging)
@app.get("/")
def read_root():
    return {"message": "Mądrość Biblii API is running."}

# ✅ Required for Vercel Deployment (Fixes 404 Issue)
if __name__ == "__main__":
    uvicorn.run("Faith-ai-backend:app", host="0.0.0.0", port=8000, reload=True)
