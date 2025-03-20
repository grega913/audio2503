from typing import Annotated
from langchain_groq import ChatGroq
from typing_extensions import TypedDict
from langgraph.graph import StateGraph
from langgraph.graph.message import add_messages
from langchain_deepseek import ChatDeepSeek
import time
from icecream import ic

class State(TypedDict):
    messages: Annotated[list, add_messages]


class GraphP1:
    def __init__(self):
        self.compiled = False
        self.compiled_data = None

    def compile(self):
        ic("Compiling GraphP1...")
        self.graph_builder = StateGraph(State)

        self.llm=ChatGroq(model='llama-3.3-70b-versatile')
        #llm=ChatDeepSeek()

        def chatbot(state: State):
            ic("chatbot")
            ic(state)
            return {"messages": [self.llm.invoke(state["messages"])]}

        self.graph_builder.add_node("chatbot", chatbot)
        self.graph_builder.set_entry_point("chatbot")
        self.graph_builder.set_finish_point("chatbot")
        self.graph = self.graph_builder.compile()
        
        time.sleep(1)
        self.compiled = True

        ic("GraphP1 compilation complete.")
    
    
    def get_compiled_graph(self):
        if not self.compiled:
            raise ValueError("GraphP1 is not compiled.")
        return self.graph #return the graph.


def stream_graph_updates(graph, user_input: str):
    for event in graph.stream({"messages": [{"role": "user", "content": user_input}]}):
        for value in event.values():
            ic("Assistant:", value["messages"][-1].content)

if __name__ == "__main__":
    ic("Test")

    graphP1 = GraphP1()
    graphP1.compile()
    graph = graphP1.get_compiled_graph()

    stream_graph_updates(graph=graph, user_input="5 facts about New Zeland")





    





