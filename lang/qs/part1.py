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

def part1_compile_graph():
    ic("def part1_compile_graph")

    graph_builder = StateGraph(State)

    llm=ChatGroq(model='llama-3.3-70b-versatile')
    #llm=ChatDeepSeek()



    def chatbot(state: State):
        return {"messages": [llm.invoke(state["messages"])]}


    # The first argument is the unique node name
    # The second argument is the function or object that will be called whenever
    # the node is used.
    graph_builder.add_node("chatbot", chatbot)
    graph_builder.set_entry_point("chatbot")
    graph_builder.set_finish_point("chatbot")
    graph = graph_builder.compile()

    return graph


def part1_stream_graph(graph, user_input: str):

    ic(f"{user_input} in def part1_stream_graph")


    for event in graph.stream({"messages": [("user", user_input)]}):
        for value in event.values():
            content = value["messages"][-1].content
            ic(content)
            
            return content



'''
graph As Class
'''
class GraphPart1:
    def __init__(self):
        ic("def init Graph1")

        self.graph_builder = StateGraph(State)
        self.llm = ChatGroq()

    def compile_graph(self):
        ic("def compile_graph")
        
        self.graph_builder.add_node("chatbot", self.chatbot)
        self.graph_builder.set_entry_point("chatbot")
        self.graph_builder.set_finish_point("chatbot")

        self.graph = self.graph_builder.compile()

    def chatbot(self, state: State):
        ic("def chatbot")
        return {"messages": [self.llm.invoke(state["messages"])]}

    def stream(self, user_input: str):
        ic(f"def stream with: {user_input}")
        ic(f"{user_input} in Graph1.stream")
        for event in self.graph.stream({"messages": [("user", user_input)]}):
            for value in event.values():
                content = value["messages"][-1].content
                ic(event)
                ic(value)
                ic(content)
                return content
   
    def get_stream(self, user_input: str):
        ic("def get_stream")
        return self.graph.stream({"messages": [("user", user_input)]})




# grapht1.py
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


        # The first argument is the unique node name
        # The second argument is the function or object that will be called whenever
        # the node is used.
        
        self.graph_builder.add_node("chatbot", chatbot)
        self.graph_builder.set_entry_point("chatbot")
        self.graph_builder.set_finish_point("chatbot")
        self.graph = self.graph_builder.compile()
        
        time.sleep(1)
        self.compiled = True

        ic("GraphP1 compilation complete.")
    

    def get_compiled_graph(self): #added method
        if not self.compiled:
            raise ValueError("GraphP1 is not compiled.")
        return self.graph #return the graph.




if __name__ == "__main__":
    ic("def main")

    graphPart1 = GraphPart1()
    graphPart1.compile_graph()

    generator =  graphPart1.get_stream("Some facts about Canada")

    for chunk in generator:
        ic(chunk)
        time.sleep(0.5)

    





