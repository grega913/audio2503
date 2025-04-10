from typing import Annotated
from langchain_groq import ChatGroq
from langchain_community.tools.tavily_search import TavilySearchResults
from langchain_core.messages import BaseMessage
from typing_extensions import TypedDict
from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph import StateGraph
from langgraph.graph.message import add_messages
from langgraph.prebuilt import ToolNode, tools_condition
import time

import os
import sys
from icecream import ic

current_dir = os.path.dirname(__file__)
app_dir = os.path.dirname(os.path.dirname(current_dir))
sys.path.insert(0, app_dir)



from config import TAVILY_API_KEY

class State(TypedDict):
    messages: Annotated[list, add_messages]

class GraphP3:
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

        ic("Compile the graph for Part 3")
        def chatbot(state: State):
            return {"messages": [self.llm_with_tools.invoke(state["messages"])]}

        # Add nodes
        self.graph_builder.add_node("chatbot", chatbot)
        tool_node = ToolNode(tools=[self.tool])
        self.graph_builder.add_node("tools", tool_node)

        # Add edges
        self.graph_builder.add_conditional_edges(
            "chatbot",
            tools_condition,
        )
        self.graph_builder.add_edge("tools", "chatbot")
        self.graph_builder.set_entry_point("chatbot")

        # Add memory and compile the graph
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
    """The config is the **second positional argument** to stream() or invoke()!"""
    for event in graph.stream(
        {"messages": [{"role": "user", "content": user_input}]},
        config=config, 
        stream_mode = "values"):

        ic(event)

        '''
        for value in event.values():
            print("Assistant:", value["messages"][-1].content)'
        '''

if __name__ == "__main__":
    ic("Testing GraphP3...")

    config = {"configurable": {"thread_id": "1"}} # this is for letting th


    # Initialize and compile the graph
    graphP3 = GraphP3()
    graphP3.compile()
    graph = graphP3.get_compiled_graph()

    # Test with a sample query
    stream_graph_updates(
        graph=graph,
        user_input="My name is Ivan, I am 56 years old, born in Italy. Do not use tools.",
        config=config)
    
    time.sleep(2)


    stream_graph_updates(
        graph=graph,
        user_input="What is my name? How old am I, where was I born? do not use tools.",
        config=config)
    
    time.sleep(2)
    



