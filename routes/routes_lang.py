from fastapi import Request, Depends, APIRouter, HTTPException, Body, status, Response, Path,FastAPI, Form
from langchain_core.messages import HumanMessage
from fastapi.responses import HTMLResponse, JSONResponse, FileResponse, RedirectResponse, StreamingResponse
from fastapi.templating import Jinja2Templates
import asyncio
from icecream import ic
from typing import Optional
from pydantic import BaseModel
import time
from typing import List, Dict, Any
import json
from langgraph.types import Command, interrupt
from prettyprinter import pprint

templates = Jinja2Templates(directory="static/templates")

from lang.qs.part1 import GraphP1
from lang.qs.part2 import GraphP2
from lang.qs.part3 import GraphP3
from lang.qs.part4 import GraphP4
from lang.qs.part5 import GraphP5

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
lang_router.state.graphP5 = GraphP5()


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
    elif graph_number == 5:
        if not router.state.graphP5.compiled:
            router.state.graphP5.compile()


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



# open route, working for item_id == 1 or item_id == 2
@lang_router.post("/api/lang_public/{item_id}")
async def stream_graph_results_public(item_id: str, data: dict):
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


'''
this is a reusable function for streaming results on graph
'''
@lang_router.post("/api/lang_protected/{item_id}", dependencies=[Depends(cookie)])
async def stream_graph_results_protected(item_id: str, data:dict, session_data: SessionData = Depends(verifier)):
    ic('${item_id} in stream_graph_results')
    user_input = data["user_input"]
    try:
        await compile_graph_once(lang_router, int(item_id))
        # Handle session requirement for item_id 3 or 4 or 5
        if (item_id == "3" or item_id == "4" or item_id == "5"):
            if not session_data:
                raise HTTPException(status_code=401, detail="Session required for item_id 3,4,5,or6")
            config = {"recursion_limit": 10, "configurable": {"thread_id": session_data.usr }}
        else:
            config = None

        # check if we have graphP3 or graphP4
        if item_id == "3":
            graph = lang_router.state.graphP3.get_compiled_graph()
        elif item_id == "4":
            graph = lang_router.state.graphP4.get_compiled_graph()
        elif item_id == "5":
            graph = lang_router.state.graphP5.get_compiled_graph()
        else:
            raise ValueError(f"Invalid graph number: {item_id}")

        ic("before generate stream")
        ic(config)

        

        async def generate_stream():
            num_events = 0
            try:
                if (item_id == "3" or item_id =="4" or item_id =="5"): # since we are using memory here, we should be streaming with config object
                    events = graph.stream(
                        {"messages": [{"role": "user", "content": user_input}]},
                        config=config,
                        stream_mode="values"
                        )
                    
                    # simples version for sending last message's content to the client
                    
                    for event in events:
                        if "messages" in event:
                            last_message = event["messages"][-1]

                            #content = last_message.content
                            yield json.dumps({"last_message": last_message.content}) + "\n"
                    
                    '''
                    chunk_size = 8
                    messages = []
                    for event in events:
                        num_events+=1
                        ic(event)
                        if "messages" in event:
                            last_message = event["messages"][-1]
                            ic(last_message)
                            messages.append(last_message)
                            if len(messages) >= chunk_size:
                                yield json.dumps({"messages": messages}) + "\n"
                                messages = []

                    if messages:
                        yield json.dumps({"messages": messages}) + "\n"'
                    '''




            except Exception as e:
                yield json.dumps({"error": str(e)}) + "\n"

            finally:
                state = graph.get_state(config=config)
                ic("#" * 50)
                pprint(state)


        return StreamingResponse(generate_stream(), media_type="text/event-stream")

    except ValueError as ve:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(ve))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))




@lang_router.post("/api/lang_human_assist/{item_id}", dependencies=[Depends(cookie)])
async def stream_human_assist(item_id: str, data: dict, session_data: SessionData = Depends(verifier)):
    ic(f'{item_id} in stream_human_assist')
    try:
        # Validate item_id and session
        if item_id not in ["3", "4"]:
            raise ValueError("Human assistance only available for item_id 3 or 4")
        if not session_data:
            raise HTTPException(status_code=401, detail="Session required for human assistance")
            
        # Get human response from request
        human_response = data.get("human_response")
        ic(human_response)
        
        if not human_response:
            raise ValueError("No human response provided")

        # Compile graph if needed
        await compile_graph_once(lang_router, int(item_id))
        
        # Get appropriate graph
        if item_id == "3":
            graph = lang_router.state.graphP3.get_compiled_graph()
        else:
            graph = lang_router.state.graphP4.get_compiled_graph()

        # Create config with thread_id from session
        config = {"configurable": {"thread_id": session_data.usr}}

        async def generate_stream():
            try:
                # Create human command with response
                human_command = Command(resume={"data": human_response})
                
                # Stream the human response through the graph
                events = graph.stream(
                    human_command,
                    config=config,
                    stream_mode="values"
                )
                
                for event in events:
                    if "messages" in event:
                        ic(event["messages"][-1])
                        content = event["messages"][-1].content
                        yield json.dumps({"content": content}) + "\n"
                        
            except Exception as e:
                yield json.dumps({"error": str(e)}) + "\n"

        return StreamingResponse(generate_stream(), media_type="text/event-stream")

    except ValueError as ve:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(ve))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

# endregion
