# config.py
import os
from dotenv import load_dotenv
load_dotenv()


#templates = FileSystemLoader("templates")




# Stripe settings - nedded in router_stripe
stripe_keys = {
    "secret_key": os.environ["STRIPE_SECRET_KEY"],
    "publishable_key": os.environ["STRIPE_PUBLISHABLE_KEY"],
    "endpoint_secret": os.environ["STRIPE_ENDPOINT_SECRET"]
}

YOUR_DOMAIN = 'http://localhost:8000'

TAVILY_API_KEY = os.environ["TAVILY_API_KEY"]
