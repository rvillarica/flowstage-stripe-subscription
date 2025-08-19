from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import stripe
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Initialize FastAPI app
app = FastAPI(title="Stripe Subscription Checker")

# Configure Stripe
stripe.api_key = os.getenv("STRIPE_API_KEY")

class EmailCheck(BaseModel):
    email: str

@app.post("/list-subscriptions")
async def list_subscriptions(request: EmailCheck):
    try:
        # Find customer by email
        customers = stripe.Customer.list(email=request.email)
        
        if not customers.data:
            raise HTTPException(status_code=404, detail="No customer found with this email")
            
        # Get all subscriptions for the customer
        subscriptions = []
        for customer in customers.data:
            customer_subs = stripe.Subscription.list(customer=customer.id)
            for sub in customer_subs.get("data"):
                # Get subscription items with plan and price details
                items = []
                try:
                    for item in sub.get("items").get("data"):
                        # Get the plan and price objects
                        plan = item.get("plan")
                        price = item.get("price")
                        
                        items.append({
                            "plan_id": plan.get("id"),
                            "plan_active": plan.get("active"),
                            "price_id": price.get("id"),
                            "price_active": price.get("active")
                        })
                except Exception as e:
                    print(f"Error processing subscription item: {str(e)}")
                    raise HTTPException(status_code=500, detail=f"Error processing subscription data: {str(e)}")
                
                subscriptions.extend(items)
        
        return subscriptions
        
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

@app.get("/")
async def root():
    return {"message": "Stripe Subscription Checker API"}
