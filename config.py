# config.py
import os
from dotenv import load_dotenv
load_dotenv()

#Jinja2 directory . . needed in routers and main
from fastapi.templating import Jinja2Templates
from jinja2 import FileSystemLoader

#templates = FileSystemLoader("templates")




# Stripe settings - nedded in router_stripe
stripe_keys = {
    "secret_key": os.environ["STRIPE_SECRET_KEY"],
    "publishable_key": os.environ["STRIPE_PUBLISHABLE_KEY"],
    "endpoint_secret": os.environ["STRIPE_ENDPOINT_SECRET"]
}

YOUR_DOMAIN = 'http://localhost:8000'
