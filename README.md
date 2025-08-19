# Stripe Subscription Status Checker

A FastAPI application that checks the subscription status of a user in Stripe using their email address and subscription ID. Designed for deployment on Railway.

## Local Development

1. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

2. Create a `.env` file with your Stripe API key:
   ```
   STRIPE_API_KEY=your_stripe_secret_key
   ```

3. Run the development server:
   ```bash
   uvicorn main:app --reload
   ```

## Railway Deployment

1. Create a new project on Railway
2. Connect your GitHub repository
3. Add environment variable:
   - `STRIPE_API_KEY`: Your Stripe secret API key
4. Railway will automatically detect the Dockerfile and deploy your application

## API Usage

### Check Subscription Status

Endpoint: `POST /check-subscription`

Request body:
```json
{
    "email": "user@example.com",
    "subscription_id": "sub_xxxxxxxxxxxxx"
}
```

Response (200):
```json
{
    "status": "active",
    "subscription_id": "sub_xxxxxxxxxxxxx",
    "email": "user@example.com"
}
```

### Error Handling

- 403: Email doesn't match subscription
- 404: Subscription not found
- 500: Internal server error

## API Documentation

Swagger UI documentation is available at `/docs` when the server is running.
# flowstage-stripe-subscription
