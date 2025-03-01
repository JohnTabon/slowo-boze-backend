from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import openai
import os
import stripe
import uvicorn
from fastapi.middleware.cors import CORSMiddleware

# Load API keys from environment variables
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
STRIPE_SECRET_KEY = os.getenv("STRIPE_SECRET_KEY")  # Ensure this is set in your Vercel environment variables
stripe.api_key = STRIPE_SECRET_KEY

# Initialize FastAPI app
app = FastAPI()

# Enable CORS to allow frontend connections
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Change this to specific frontend domain later
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Temporary in-memory storage (Replace with DB later)
user_messages = {}

# Pricing tiers
PRICING_TIERS = {
    "small": {"amount": 1000, "messages": 10},  # 10 PLN = 10 messages
    "medium": {"amount": 2500, "messages": 50}, # 25 PLN = 50 messages
    "unlimited": {"amount": 10000, "messages": float("inf")}, # 100 PLN = Unlimited messages
}

# Define request models
class ChatRequest(BaseModel):
    user_id: str
    text: str

class PaymentRequest(BaseModel):
    user_id: str
    plan: str  # small, medium, unlimited

# Chat Endpoint (with message limit)
@app.post("/chat")
def chat_with_ai(request: ChatRequest):
    user_id = request.user_id

    if not user_id:
        raise HTTPException(status_code=400, detail="User ID is required")

    # Initialize user messages if new
    if user_id not in user_messages:
        user_messages[user_id] = []

    # Add user input to conversation history
    user_messages[user_id].append({"role": "user", "content": request.text})

    # Check if user has exceeded their message limit
    if len(user_messages[user_id]) > PRICING_TIERS["small"]["messages"]:
        raise HTTPException(status_code=402, detail="Message limit reached. Please purchase more messages.")

    try:
        # Initialize OpenAI client
        openai.api_key = OPENAI_API_KEY

        # Send conversation history to OpenAI
        try:
    response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=user_messages[user_id],
        temperature=0.7,
    )

    ai_reply = response['choices'][0]['message']['content']
    user_messages[user_id].append({"role": "assistant", "content": ai_reply})
    return {"reply": ai_reply}

except openai.error.OpenAIError as e:
    raise HTTPException(status_code=500, detail=f"OpenAI API error: {str(e)}")

except Exception as e:
    raise HTTPException(status_code=500, detail=f"Unexpected server error: {str(e)}")

        # Add AI's response to conversation history
        ai_reply = response['choices'][0]['message']['content']
        user_messages[user_id].append({"role": "assistant", "content": ai_reply})

        return {"reply": ai_reply}
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Create Stripe Payment Intent (BLIK enabled)
@app.post("/create-payment-intent")
def create_payment_intent(request: PaymentRequest):
    try:
        plan = PRICING_TIERS.get(request.plan)
        if not plan:
            raise HTTPException(status_code=400, detail="Invalid plan selected")

        intent = stripe.PaymentIntent.create(
            amount=plan["amount"],  # Payment amount in PLN
            currency="pln",
            payment_method_types=["blik"],  # Enable BLIK payments
        )

        return {"clientSecret": intent["client_secret"]}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

# Unlock Messages After Payment
@app.post("/unlock-messages")
def unlock_messages(request: PaymentRequest):
    user_id = request.user_id
    plan = PRICING_TIERS.get(request.plan)

    if not plan:
        raise HTTPException(status_code=400, detail="Invalid plan selected")

    user_messages[user_id] = []  # Reset the message count for this user
    return {"status": "success", "message": "Messages unlocked!"}

# Root route to check if API is running
@app.get("/")
def read_root():
    return {"message": "Mądrość Biblii API is running."}

# Required for Vercel Deployment (Fixes 404 Issue)
def start():
    uvicorn.run(app, host="0.0.0.0", port=8000)

if __name__ == "__main__":
    start()
