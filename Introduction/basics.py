from typing import List, Sequence
from dotenv import load_dotenv
from langchain_core.messages import BaseMessage, HumanMessage
from langgraph.graph import END,MessageGraph
from chains import generation_chain,reflection_chain


load_dotenv()

def generation_node(state):
    return generation_chain.invoke({"messages": state})


def reflection_node(state):
    response= reflection_chain.invoke({"messages": state})
    return [HumanMessage(content=response.content)]



graph = MessageGraph()

graph.add_node("generate", generation_node)
graph.add_node("reflect", reflection_node)

graph.set_entry_point("generate")

def should_continue(state):
    if(len(state)>= 4):
        return END
    return "reflect"


    
graph.add_conditional_edges("generate", should_continue, {"reflect": "reflect", END: END})

graph.add_edge("reflect", "generate")

app = graph.compile()


print(app.get_graph().draw_ascii())

response = app.invoke(HumanMessage(content="Write a viral tweet about learning langgraph."))
print(response)