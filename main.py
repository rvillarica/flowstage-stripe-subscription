from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import stripe
import os
from dotenv import load_dotenv
import uvicorn

# Load environment variables
load_dotenv()

# Initialize FastAPI app
app = FastAPI()

# Get port from environment variable or default to 8000
port = int(os.getenv("PORT", 8000))

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all subdomains of theflowstage.com
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods
    allow_headers=["*"],  # Allows all headers
)

# Initialize FastAPI app with title
app.title = "Stripe Subscription Checker"

# Configure Stripe
stripe.api_key = os.getenv("STRIPE_API_KEY")

class EmailCheck(BaseModel):
    email: str

@app.get("/health")
async def health_check():
    try:
        # Check if Stripe API key is configured
        if not stripe.api_key:
            return {"status": "warning", "message": "Stripe API key not configured"}
            
        # Try to make a simple Stripe API call
        stripe.Account.retrieve()
        return {"status": "healthy", "stripe": "connected"}
    except Exception as e:
        return {"status": "unhealthy", "stripe": str(e)}

@app.post("/list-subscriptions")
async def list_subscriptions(request: EmailCheck):
    print("Starting subscription lookup...")
    try:
        # Validate Stripe API key
        if not stripe.api_key:
            print("Error: No Stripe API key configured")
            raise HTTPException(status_code=500, detail="Stripe API key not configured")
            
        print(f"Searching for customer with email: {request.email}")
        # Find customer by email
        try:
            customers = stripe.Customer.list(email=request.email)
            print(f"Found {len(customers.get('data', []))} customers")
        except stripe.error.StripeError as e:
            print(f"Stripe API error during customer lookup: {str(e)}")
            raise HTTPException(status_code=500, detail=f"Stripe API error: {str(e)}")
        except Exception as e:
            print(f"Unhandled error: {str(e)}")
            raise HTTPException(status_code=500, detail="Internal server error")

        if not customers.get('data', []):
            print("No customers found")
            raise HTTPException(status_code=404, detail="No customer found with this email")
            
        # Get all subscriptions for the customer
        all_items = []
        try:
            print("Fetching subscriptions...")
            for customer in customers.get('data', []):
                print(f"Processing customer {customer.get('id')}")
                try:
                    customer_subs = stripe.Subscription.list(customer=customer.get('id'))
                    print(f"Found {len(customer_subs.get('data', []))} subscriptions")
                    
                    for sub in customer_subs.get('data', []):
                        print(f"Processing subscription {sub.get('id')}")
                        for item in sub.get('items', {}).get('data', []):
                            try:
                                all_items.append({
                                    "plan_id": item.get('plan', {}).get('id'),
                                    "plan_active": item.get('plan', {}).get('active'),
                                    "price_id": item.get('price', {}).get('id'),
                                    "price_active": item.get('price', {}).get('active')
                                })
                            except Exception as e:
                                print(f"Error processing subscription item: {str(e)}")
                                continue
                except stripe.error.StripeError as e:
                    print(f"Stripe API error during subscription fetch: {str(e)}")
                    continue
                except Exception as e:
                    print(f"Error processing customer subscriptions: {str(e)}")
                    continue
            
            print(f"Successfully processed {len(all_items)} subscription items")
            return all_items
            
        except Exception as e:
            print(f"Fatal error processing subscriptions: {str(e)}")
            raise HTTPException(status_code=500, detail="Error processing subscription data")
        
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

@app.get("/")
async def root():
    return {"message": "Stripe Subscription Checker API"}
