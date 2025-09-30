from react_state import AgentState
from nodes import reason_node, action_node
from langgraph.graph import END, StateGraph
from langchain_core.agents import AgentFinish, AgentAction
from agent import agent
from dotenv import load_dotenv
load_dotenv()


REASON_NODE = "reason_node"
ACTION_NODE = "action_node"


def should_continue(state: AgentState) -> str:
    if isinstance(state['agent_outcome'], AgentFinish):
        return END
    else:
        return ACTION_NODE


flow = StateGraph(AgentState)

flow.add_node(REASON_NODE, reason_node)
flow.add_node(ACTION_NODE, action_node)
flow.set_entry_point(REASON_NODE)
flow.add_conditional_edges(REASON_NODE, should_continue)
flow.add_edge(ACTION_NODE, REASON_NODE)

app = flow.compile()
print(app.get_graph().draw_ascii())

result = app.invoke({
    "input": "What are the latest advancements in AI research as of 2024?",
    "agent_outcome": None,
    "intermediate_steps": []
})

# print(result)
print(result['agent_outcome'].return_values['output'], 'final result')
