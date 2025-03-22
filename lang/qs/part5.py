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

import os
import sys
from icecream import ic

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
        def human_assistance(
            name: str,
            birthday: str,
            tool_call_id: Annotated[str, InjectedToolCallId]
        ) -> str:
            """Request assistance from a human."""
            human_response = interrupt({
                "question": "Is this correct?",
                "name": name,
                "birthday": birthday,
            })
            
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
            message = self.llm_with_tools.invoke(state["messages"])
            assert len(message.tool_calls) <= 1
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
    config = {"configurable": {"thread_id": "1"}}
    user_input = "My name is John and my birthday is 1990-01-01. Is this correct?"
    
    events = graph.stream(
        {
            "messages": [{"role": "user", "content": user_input}],
            "name": "John",
            "birthday": "1990-01-01"
        },
        config,
        stream_mode="values",
    )
    
    for event in events:
        if "messages" in event:
            ic(event["messages"][-1])
