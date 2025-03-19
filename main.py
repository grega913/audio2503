# region Imports - most of them

from typing import Union
from contextlib import asynccontextmanager
from pydantic import BaseModel
from fastapi import FastAPI, Request, WebSocket, Depends, APIRouter, HTTPException, Body, status, Response, Path
from fastapi.responses import HTMLResponse, JSONResponse, FileResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from markupsafe import escape
import uvicorn
from icecream import ic
import os
import firebase_admin
from firebase_admin import credentials, firestore



# endregion


# region Lifespan - things happening before first request 

# https://fastapi.tiangolo.com/advanced/events/#lifespan

def fake_answer_to_everything_ml_model(x: float):
    return x * 42

ml_models = {}

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Load the ML model
    ic("def lifespan")
    ml_models["answer_to_everything"] = fake_answer_to_everything_ml_model

    # Firebase Admin SDK setup
    cred = credentials.Certificate("firebase_auth.json")
    firebase_admin.initialize_app(cred)

    ic("after firebase initialization")

    ic(ml_models)
    yield
    # Things happening just before app close
    # Clean up the ML models and release the resources

    ic("before mlmodels clean")
    ml_models.clear()


# endregion


# region Rotes import and App Init

from routes.routes_stripe import stripe_router
from routes.routes_auth import auth_router
from routes.routes_websockets import websocket_router
from routes.routes_basic import basic_router
from routes.routes_audio import audio_router
from routes.routes_play import play_router
from routes.routes_lang import lang_router

app = FastAPI(lifespan=lifespan)

app.include_router(stripe_router)
app.include_router(auth_router)
app.include_router(websocket_router)
app.include_router(basic_router)
app.include_router(audio_router)
app.include_router(play_router)
app.include_router(lang_router)


# mapping static file
app.mount("/static", StaticFiles(directory="static", follow_symlink=True), name="static") 
templates = Jinja2Templates(directory="static/templates")


# endregion


# region Routes - some leftoveres



@app.get("/")
async def root():
    return {"message": "Hello World"}


@app.get("/favicon.ico", include_in_schema=False)
async def favicon():
    return FileResponse("static/favicon.ico")


@app.get("/predict")
async def predict(x: float):
    result = ml_models["answer_to_everything"](x)
    return {"result": result}


@app.get("/items/{item_id}")
async def read_item(item_id: int):
    return {"item_id": item_id}

# base route  - for testing base html tempplate - all others templates extend this one
@app.get("/base", response_class=HTMLResponse)
async def home(request: Request):
    return templates.TemplateResponse(request=request, name="base.html")



@app.get("/itemz/{item_id}", response_class=HTMLResponse)
async def read_itemz(request: Request, item_id: str):
    """
    Renders an HTML template with the provided item_id in the context.

    Args:
        request: The incoming request object.
        item_id: The string path parameter representing the item ID.

    Returns:
        A TemplateResponse with the rendered HTML.
    """
    context = {"request": request, "item_id": item_id}
    return templates.TemplateResponse("item.html", context)




# endregion



if __name__ == "__main__":
    uvicorn.run("main:app", reload=True)

