# https://langchain-ai.github.io/langgraph/tutorials/introduction/#part-5-customizing-state

from typing import Annotated
from langchain_groq import ChatGroq  # Using Groq instead of Anthropic
from langchain_community.tools.tavily_search import TavilySearchResults
from langchain_core.messages import ToolMessage
from langchain_core.tools import InjectedToolCallId, tool
from typing_extensions import TypedDict
from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages
from langgraph.prebuilt import ToolNode, tools_condition
from langgraph.types import Command, interrupt
import time
import os
import sys
from icecream import ic
from prettyprinter import pprint

current_dir = os.path.dirname(__file__)
app_dir = os.path.dirname(os.path.dirname(current_dir))
sys.path.insert(0, app_dir)

from config import TAVILY_API_KEY

class State(TypedDict):
    messages: Annotated[list, add_messages]
    name: str
    birthday: str

class GraphP5:
    def __init__(self):
        self.compiled = False
        self.graph = None
        self.graph_builder = StateGraph(State)
        
        # Initialize tools and LLM
        self.tool = TavilySearchResults(max_results=2, api_key=TAVILY_API_KEY)
        self.tools = [self.tool]
        self.llm = ChatGroq(model='llama-3.3-70b-versatile')
        self.llm_with_tools = self.llm.bind_tools(self.tools)

    def compile(self):
        ic("Compile the graph for Part 5")

        @tool
        # Note that because we are generating a ToolMessage for a state update, we
        # generally require the ID of the corresponding tool call. We can use
        # LangChain's InjectedToolCallId to signal that this argument should not
        # be revealed to the model in the tool's schema.
        def human_assistance(
            name: str,
            birthday: str,
            tool_call_id: Annotated[str, InjectedToolCallId]
        ) -> str:
            """Request assistance from a human."""
            ic("in human_assistance tool")
            human_response = interrupt({
                "question": "Is this correct?",
                "name": name,
                "birthday": birthday,
            })

            ic(human_response)
            
            if human_response.get("correct", "").lower().startswith("y"):
                verified_name = name
                verified_birthday = birthday
                response = "Correct"
            else:
                verified_name = human_response.get("name", name)
                verified_birthday = human_response.get("birthday", birthday)
                response = f"Made a correction: {human_response}"
            
            state_update = {
                "name": verified_name,
                "birthday": verified_birthday,
                "messages": [ToolMessage(response, tool_call_id=tool_call_id)],
            }
            return Command(update=state_update)

        # Add human assistance tool
        self.tools.append(human_assistance)
        self.llm_with_tools = self.llm.bind_tools(self.tools)

        def chatbot(state: State):
            ic("chatbot")

            message = self.llm_with_tools.invoke(state["messages"])
            #ic(message)
            #assert len(message.tool_calls) <= 1
            return {"messages": [message]}

        # Define nodes
        self.graph_builder.add_node("chatbot", chatbot)
        tool_node = ToolNode(tools=self.tools)
        self.graph_builder.add_node("tools", tool_node)

        # Define edges
        self.graph_builder.add_conditional_edges(
            "chatbot",
            tools_condition,
        )
        self.graph_builder.add_edge("tools", "chatbot")
        self.graph_builder.add_edge(START, "chatbot")

        # Set finish point
        self.graph_builder.set_finish_point("chatbot")
        
        # Compile the graph
        memory = MemorySaver()
        self.graph = self.graph_builder.compile(checkpointer=memory)
        self.compiled = True

    def get_compiled_graph(self):
        """Return the compiled graph"""
        if not self.compiled:
            raise ValueError("Graph not compiled yet")
        return self.graph

def stream_graph_updates(graph, user_input: str, config):
    """Stream updates from the graph"""
    for event in graph.stream(
        {
            "messages": [{"role": "user", "content": user_input}],
            "name": "",
            "birthday": ""
        },
        config=config,
        stream_mode="values"
    ):
        ic(event)

if __name__ == "__main__":
    ic("Testing GraphP5...")
    
    # Initialize and compile the graph
    graphP5 = GraphP5()
    graphP5.compile()
    graph = graphP5.get_compiled_graph()

    # Test the graph

    #config = {"configurable": {"thread_id": "1"}}
    config = {"recursion_limit": 10, "configurable": {"thread_id": "1" }}


    user_input = (
        "Can you look up when LangGraph was released? When you have the answer, use the human_assistance tool for review."
    )


    user_input = (
        "Can you look up when Leonardo DaVinci was born? When you have the answer, use the human_assistance tool for review."
    )

    
    num_events=0
    events = graph.stream(
        {"messages": [{"role": "user", "content": user_input}]},
        config=config,
        stream_mode="values",
    )

    for event in events:
        num_events+=1
        ic(num_events)
        ic("--" * 50)
        ic(event)
        if "messages" in event:
            last_message = event["messages"][-1]
            ic(last_message)

    state = graph.get_state(config=config)
    ic("#" * 50)
    pprint(state)




    

    ic("#" * 50)
    time.sleep(5)
    snapshot = graph.get_state(config)
    ic(snapshot)
    ic(snapshot.next)
    ic("#" * 50)
    time.sleep(5)
    ic("now we are commanding with human_response")
    ic("#" * 50)


    human_command = Command(
        resume={
            "name": "LangGraph",
            "birthday": "Jan 19, 2024",
            },
    )

    human_command = Command(
        resume={
            "name": "LDV",
            "birthday": "Jan 10, 1555",
            },
    )

    events = graph.stream(human_command, config, stream_mode="values")
    for event in events:
        if "messages" in event:
            event["messages"][-1].pretty_print()

    ic("#" * 50)
    time.sleep(5)


    snapshot = graph.get_state(config)
    ic("snapshot at the end:")
    ic("#" * 50)

    ic(snapshot)
    ic("#" * 50)



    for key, value in snapshot.values.items():
        if "name" in key and "birthday" in key:
            pprint({key: value})



    

