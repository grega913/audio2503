from fastapi import APIRouter
from fastapi import FastAPI, Request, WebSocket, Depends, APIRouter, HTTPException, Body, status, Response, Path
from fastapi.responses import HTMLResponse, JSONResponse, FileResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles

import os
import stripe
from config import stripe_keys, YOUR_DOMAIN
from icecream import ic

from fastapi.templating import Jinja2Templates

stripe.api_key = stripe_keys["secret_key"]

templates = Jinja2Templates(directory="static/templates")

stripe_router = APIRouter()

# region Stripe


@stripe_router.get("/stripe123", response_class=HTMLResponse)
async def stripe123(request: Request):
    return templates.TemplateResponse(request=request, name="stripe/stripe123.html")

@stripe_router.get("/stripe_success", response_class=HTMLResponse)
async def stripe_success(request: Request):
    return templates.TemplateResponse(request=request, name="stripe/stripe_success.html")

@stripe_router.get("/stripe_cancelled", response_class=HTMLResponse)
async def stripe_cancelled(request: Request):
    return templates.TemplateResponse(request=request, name="stripe/stripe_cancelled.html")

@stripe_router.get("/stripe_checkout", response_class=HTMLResponse)
async def stripe_checkout(request: Request):
    return templates.TemplateResponse(request=request, name="stripe/stripe_checkout.html")

@stripe_router.get("/stripe_checkout2", response_class=HTMLResponse)
async def stripe_checkout2(request: Request):
    return templates.TemplateResponse(request=request, name="stripe/stripe_checkout2.html")

@stripe_router.get("/stripe_config")
def get_publishable_key():
    stripe_config = {"publicKey": stripe_keys["publishable_key"]}
    return JSONResponse(stripe_config)

@stripe_router.post('/create-checkout-session')
def create_checkout_session():
    try:
        checkout_session = stripe.checkout.Session.create(
            line_items=[
                {
                    # Provide the exact Price ID (for example, pr_1234) of the product you want to sell
                    'price': 'price_1R17DJB4j30g5cZMjWNlbREF',
                    'quantity': 1,
                },
            ],
            mode='payment',
            success_url=YOUR_DOMAIN + '/stripe_success',
            cancel_url=YOUR_DOMAIN + '/stripe_cancel'
        )

        ic(checkout_session)

        return JSONResponse({"sessionId": checkout_session.id})

        

    except Exception as e:
        return str(e)



# endregion