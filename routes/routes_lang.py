from fastapi import Request, Depends, APIRouter, HTTPException, Body, status, Response, Path,FastAPI, Form
from fastapi.responses import HTMLResponse, JSONResponse, FileResponse, RedirectResponse, StreamingResponse
from fastapi.templating import Jinja2Templates
import asyncio
from icecream import ic
from typing import Optional
from pydantic import BaseModel
import time
from typing import List, Dict, Any
import json

templates = Jinja2Templates(directory="static/templates")

from lang.qs.part1 import  GraphP1


# we need state object in APIRouter because of initializing some lon running operations for the first time we'll be in the route
class RouterWithState(APIRouter):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.state = type("State", (object,), {})()  # Create an empty state object

lang_router = RouterWithState()

# Initialize state at the router level
lang_router.state.lang_initialized = False
lang_router.state.graphP1 = GraphP1()


async def compile_graph_once(router):
    if not router.state.graphP1.compiled:
        router.state.graphP1.compile()


async def long_running_lang_operation():
    """Simulates a long-running operation for the /lang route."""
    print("Starting long-running language initialization...")
    await asyncio.sleep(0.2)  # Simulate a 0.2-second delay
    print("Language initialization complete.")


@lang_router.get("/lang/", response_class=HTMLResponse)
async def lang_no_ids(request: Request):
    context = {"request": request, "item_id": None}
    return templates.TemplateResponse("item.html", context)


@lang_router.get("/lang/{item_id}", response_class=HTMLResponse)
async def lang(request: Request, item_id: str):
    """Handles the /lang route, performing initialization if needed."""

        
    '''
    if not lang_router.state.lang_initialized:
        ic("in route lang, lang_router.state.lang_initialized is false")
        await long_running_lang_operation()
        lang_router.state.lang_initialized = True
    '''
   

    context = {"request": request, "item_id": item_id}
    return templates.TemplateResponse("lang/lang.html", context)

# region Routes for Lang
@lang_router.post("/api/lang/{item_id}")
async def stream_graph_results(item_id: str, data:dict):
    ic(item_id)
    user_input = data["user_input"]
    try:
        await compile_graph_once(lang_router)
        graph = lang_router.state.graphP1.get_compiled_graph()

        async def generate_stream():
            try:
                for event in graph.stream({"messages": [{"role": "user", "content": user_input}]}):
                    for value in event.values():
                        content = value["messages"][-1].content
                        ic("Assistant:", content)
                       
                        yield json.dumps({"content": content}) + "\n"  # Yield each content as JSON
            except Exception as e:
                yield json.dumps({"error": str(e)}) + "\n"

        return StreamingResponse(generate_stream(), media_type="text/event-stream")

    except ValueError as ve:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(ve))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))





# endregion
