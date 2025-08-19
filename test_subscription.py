import requests
import json
from datetime import datetime

def test_subscriptions():
    # Get user input
    email = input("Enter your email address: ")
    
    # API endpoint (assuming local development server)
    url = "http://localhost:8000/list-subscriptions"
    
    # Prepare the request data
    data = {"email": email}
    
    try:
        # Send POST request to the API
        response = requests.post(url, json=data)
        
        # Print formatted response
        print("\nSubscriptions:")
        print("-" * 50)
        
        if response.status_code == 200:
            items = response.json()
            if not items:
                print("No subscription items found.")
            else:
                print(items)
        else:
            error = response.json()
            print(f"Error: {error.get('detail', 'Unknown error')}")
            print(f"Status Code: {response.status_code}")
            
    except requests.exceptions.ConnectionError:
        print("Error: Could not connect to the server. Make sure the FastAPI server is running.")
    except Exception as e:
        print(f"Error: {str(e)}")

if __name__ == "__main__":
    print("Stripe Subscription Checker")
    print("=" * 30)
    test_subscriptions()
