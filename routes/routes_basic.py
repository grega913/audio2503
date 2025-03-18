from fastapi import APIRouter
from fastapi import FastAPI, Request, WebSocket, Depends, APIRouter, HTTPException, Body, status, Response, Path
from fastapi.responses import HTMLResponse, JSONResponse, FileResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
import os
import stripe
from config import stripe_keys
from icecream import ic
from uuid import UUID, uuid4
import firebase_admin
from firebase_admin import credentials, firestore, auth
from config import YOUR_DOMAIN
from helperz import cookie, backend, verifier, SessionData, ModelName, Item

templates = Jinja2Templates(directory="static/templates")

basic_router = APIRouter()

@basic_router.get("/home", response_class=HTMLResponse)
async def home(request: Request):
    return templates.TemplateResponse(request=request, name="basic/home.html")

@basic_router.get("/terms", response_class=HTMLResponse)
async def terms(request: Request):
    return templates.TemplateResponse(request=request, name="basic/terms.html")

@basic_router.get("/privacy", response_class=HTMLResponse)
async def privacy(request: Request):
    return templates.TemplateResponse(request=request, name="basic/privacy.html")

@basic_router.get("/about", response_class=HTMLResponse)
async def about(request: Request):
    return templates.TemplateResponse(request=request, name="basic/about.html")
