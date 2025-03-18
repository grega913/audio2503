from fastapi import APIRouter
from fastapi import FastAPI, Request, WebSocket, Depends, APIRouter, HTTPException, Body, status, Response, Path
from fastapi.responses import HTMLResponse, JSONResponse, FileResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates



templates = Jinja2Templates(directory="static/templates")

audio_router = APIRouter()

@audio_router.get("/a1", response_class=HTMLResponse)
async def a1(request: Request):
    return templates.TemplateResponse(request=request, name="audio/a1.html")

