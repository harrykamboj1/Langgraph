from langgraph.graph import StateGraph, END
from langgraph.types import Command


class MyState:
    messages: list = []


def node_a(state: MyState):
    print("Called A")
    # Update state and go to node_b
    return Command(update={"messages": state.messages + ["a"]}, goto="node_b")


def node_b(state: MyState):
    print("Called B")
    # Update state and go to END
    return Command(update={"messages": state.messages + ["b"]}, goto=END)


graph = StateGraph(MyState)
graph.add_node("node_a", node_a)
graph.add_node("node_b", node_b)

graph.set_entry_point("node_a")

# No explicit edges are defined between node_a and node_b, or node_b and END.
# The routing is handled by the Command objects returned by the nodes.

app = graph.compile()

final_state = app.invoke({"messages": []})
print(final_state.messages)  # Expected: ['a', 'b']
