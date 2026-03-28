"""
Stripe configuration: environment variables, price ID mapping, retry settings.
"""
import os

# --- API keys ---
STRIPE_SECRET_KEY = os.environ.get("STRIPE_SECRET_KEY", "")
STRIPE_WEBHOOK_SECRET = os.environ.get("STRIPE_WEBHOOK_SECRET", "")
STRIPE_PUBLISHABLE_KEY = os.environ.get("STRIPE_PUBLISHABLE_KEY", "")

# --- Frontend URLs for Checkout redirect ---
FRONTEND_URL = os.environ.get("FRONTEND_URL", "http://localhost:3000")
CHECKOUT_SUCCESS_URL = f"{FRONTEND_URL}/billing/success?session_id={{CHECKOUT_SESSION_ID}}"
CHECKOUT_CANCEL_URL = f"{FRONTEND_URL}/billing/cancel"
BILLING_PORTAL_RETURN_URL = f"{FRONTEND_URL}/billing"

# --- Plan → Stripe Price ID mapping ---
# Override with env vars for production; defaults are test-mode placeholders.
PRICE_IDS = {
    "starter": os.environ.get("STRIPE_PRICE_STARTER", "price_starter_test"),
    "pro": os.environ.get("STRIPE_PRICE_PRO", "price_pro_test"),
    "cabinet": os.environ.get("STRIPE_PRICE_CABINET", "price_cabinet_test"),
}

# --- Plan metadata (mirrors SubscriptionPlan rows) ---
PLAN_METADATA = {
    "starter": {"price_eur": 29.0, "calculation_limit": 50, "user_limit": 1},
    "pro": {"price_eur": 79.0, "calculation_limit": None, "user_limit": 1},
    "cabinet": {"price_eur": 199.0, "calculation_limit": None, "user_limit": 10},
}

# --- Retry configuration for failed payments ---
MAX_PAYMENT_RETRIES = 3
RETRY_INTERVALS_DAYS = [1, 3, 7]  # Days between retry attempts

# --- Grace period: allow 10% overage before hard-blocking ---
GRACE_OVERAGE_PCT = 0.10

# --- Trial period ---
TRIAL_DAYS = 14
