from typing import Annotated
from langchain_anthropic import ChatAnthropic
from langchain_community.tools.tavily_search import TavilySearchResults
from langchain_core.messages import BaseMessage
from typing_extensions import TypedDict
from langgraph.graph import StateGraph
from langgraph.graph.message import add_messages
from langgraph.prebuilt import ToolNode, tools_condition

class State(TypedDict):
    messages: Annotated[list, add_messages]

class GraphP2:
    def __init__(self):
        self.compiled = False
        self.graph = None
        self.graph_builder = StateGraph(State)
        
        # Initialize tools and LLM
        self.tool = TavilySearchResults(max_results=2)
        self.tools = [self.tool]
        self.llm = ChatAnthropic(model="claude-3-5-sonnet-20240620")
        self.llm_with_tools = self.llm.bind_tools(self.tools)

    def compile(self):
        """Compile the graph for Part 2"""
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

        # Compile the graph
        self.graph = self.graph_builder.compile()
        self.compiled = True

    def get_compiled_graph(self):
        """Return the compiled graph"""
        if not self.compiled:
            raise ValueError("Graph not compiled yet")
        return self.graph
