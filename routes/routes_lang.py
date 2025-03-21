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

from lang.qs.part1 import GraphP1
from lang.qs.part2 import GraphP2
from lang.qs.part3 import GraphP3
from lang.qs.part4 import GraphP4

from helperz import cookie, backend, verifier, SessionData, ModelName, Item

# we need state object in APIRouter because of initializing some lon running operations for the first time we'll be in the route
class RouterWithState(APIRouter):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.state = type("State", (object,), {})()  # Create an empty state object

lang_router = RouterWithState()

# Initialize state at the router level
lang_router.state.lang_initialized = False
lang_router.state.graphP1 = GraphP1()
lang_router.state.graphP2 = GraphP2()
lang_router.state.graphP3 = GraphP3()
lang_router.state.graphP4 = GraphP4()


async def compile_graph_once(router, graph_number: int = 1):
    """Compile the specified graph if not already compiled"""
    if graph_number == 1:
        if not router.state.graphP1.compiled:
            router.state.graphP1.compile()
    elif graph_number == 2:
        if not router.state.graphP2.compiled:
            router.state.graphP2.compile()
    elif graph_number == 3:
        if not router.state.graphP3.compiled:
            router.state.graphP3.compile()
    elif graph_number == 4:
        if not router.state.graphP4.compiled:
            router.state.graphP4.compile()


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



'''this is route for Part 3 - where we need to have config element'
    We are checking the SessionData, extraqcing usr from that object and using it as thread_id so that each user can have its own memory
    Users should obviously be looged, have an active session
    Some
'''

@lang_router.post("/api/lang_protected/{item_id}", dependencies=[Depends(cookie)])
async def stream_graph_results(item_id: str, data:dict, session_data: SessionData = Depends(verifier)):
    ic('${item_id} in stream_graph_results')

    user_input = data["user_input"]
    try:
        await compile_graph_once(lang_router, int(item_id))

        # Handle session requirement for item_id 3
        if item_id == "3":
            if not session_data:
                raise HTTPException(status_code=401, detail="Session required for item_id 3")

            config = {"configurable": {"thread_id": session_data.usr }}
        else:
            config = None


        if item_id == "3":
            graph = lang_router.state.graphP3.get_compiled_graph()
        elif item_id == "4":
            graph = lang_router.state.graphP4.get_compiled_graph()
        else:
            raise ValueError(f"Invalid graph number: {item_id}")

        async def generate_stream():
            try:
                if item_id == "3": # since we are using memory here, we should be streaming with config object
                    #config = {"configurable": {"thread_id": "1"}}
                    ic (config)
                    events= graph.stream(
                        {"messages": [{"role": "user", "content": user_input}]},
                        config=config,
                        stream_mode="values"
                        )
                    for event in events:
                        ic(event)
                        last_message = event["messages"][-1]
                        ic(last_message)

                        content = event["messages"][-1].content
                        yield json.dumps({"content": content}) + "\n"

                else:
                    for event in graph.stream({"messages": [{"role": "user", "content": user_input}]}):
                        for value in event.values():
                            ic(value)
                            content = value["messages"][-1].content
                            yield json.dumps({"content": content}) + "\n"
            except Exception as e:
                yield json.dumps({"error": str(e)}) + "\n"

        return StreamingResponse(generate_stream(), media_type="text/event-stream")

    except ValueError as ve:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(ve))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


# open route, working for item_id == 1 or item_id == 2
@lang_router.post("/api/lang_private/{item_id}")
async def stream_graph_public(item_id: str, data: dict):
    """Public route for item_id 1 and 2"""
    ic(f'{item_id} in stream_graph_public')
    user_input = data["user_input"]
    try:
        await compile_graph_once(lang_router, int(item_id))

        if item_id == "1":
            graph = lang_router.state.graphP1.get_compiled_graph()
        elif item_id == "2":
            graph = lang_router.state.graphP2.get_compiled_graph()
        elif item_id == "4":
            graph = lang_router.state.graphP4.get_compiled_graph()
        else:
            raise ValueError(f"Invalid graph number: {item_id}")

        async def generate_stream():
            try:
                for event in graph.stream({"messages": [{"role": "user", "content": user_input}]}):
                    for value in event.values():
                        ic(value)
                        content = value["messages"][-1].content
                        yield json.dumps({"content": content}) + "\n"
            except Exception as e:
                yield json.dumps({"error": str(e)}) + "\n"

        return StreamingResponse(generate_stream(), media_type="text/event-stream")

    except ValueError as ve:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(ve))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))




# endregion
