from IPython.display import Image, display
from langgraph.graph import StateGraph, START, END, add_messages
from langgraph.types import Command, interrupt
from typing import TypedDict, Annotated, List
from langgraph.checkpoint.memory import MemorySaver
from langchain_groq import ChatGroq
from langchain_core.messages import HumanMessage, SystemMessage, AIMessage
import uuid
from dotenv import load_dotenv
load_dotenv()

# ------------------- SETUP -------------------
memory = MemorySaver()
llm = ChatGroq(model="llama-3.1-8b-instant")


# ------------------- STATE DEFINITION -------------------
class State(TypedDict):
    twitter_topic: str
    generated_post: Annotated[List[AIMessage], add_messages]
    human_feedback: Annotated[List[str], add_messages]


# ------------------- MODEL NODE -------------------
def model(state: State):
    iteration = len(state["human_feedback"]) + 1
    print("\n" + "="*60)
    print(f"🌀 [MODEL NODE] - Iteration {iteration}")
    print("="*60)

    twitter_topic = state["twitter_topic"]
    feedback = state.get("human_feedback", ["No feedback yet"])

    prompt = f"""
    Twitter Topic: {twitter_topic}
    Latest Feedback: {feedback[-1] if feedback else "No feedback yet"}

    Generate a structured, engaging, and clear Twitter post.
    Consider the feedback to improve your response.
    """

    response = llm.invoke([
        SystemMessage(
            content="You are a helpful assistant that generates Twitter posts."),
        HumanMessage(content=prompt)
    ])

    generated_content = response.content.strip()

    print(f"\n📝 Generated Post:\n{generated_content}")
    print("="*60)

    return {
        "generated_post": [AIMessage(content=generated_content)],
        "human_feedback": feedback
    }


# ------------------- HUMAN NODE -------------------
def human_node(state: State):
    print("\n" + "-"*60)
    print("👤 [HUMAN FEEDBACK NODE]")
    print("-"*60)

    print("\n💬 Please provide feedback to refine this post.")
    print("   (Type 'done' to finalize)\n")

    user_feedback = interrupt({
        "generated_post": state["generated_post"],
        "message": "Provide feedback (or 'done' to finish): "
    })

    print(f"✅ Human Feedback Received: {user_feedback}")

    if user_feedback.lower() == "done":
        return Command(update={"human_feedback": state["human_feedback"] + ["Finalized"]}, goto="end_node")

    return Command(update={"human_feedback": state["human_feedback"] + [user_feedback]}, goto="model")


# ------------------- END NODE -------------------
def end_node(state: State):
    print("\n" + "="*60)
    print("🏁 [END NODE] - Final Result")
    print("="*60)
    print(f"\n📌 Topic: {state['twitter_topic']}")
    print(f"\n📝 Final Post:\n{state['generated_post'][-1].content}")
    print(f"\n💬 Feedback History: {state['human_feedback']}")
    print("="*60)
    return state


# ------------------- GRAPH DEFINITION -------------------
graph = StateGraph(State)
graph.add_node("model", model)
graph.add_node("human_node", human_node)
graph.add_node("end_node", end_node)

graph.set_entry_point("model")
graph.add_edge(START, "model")
graph.add_edge("model", "human_node")
graph.set_finish_point("end_node")

# ------------------- COMPILE GRAPH -------------------
checkpointer = MemorySaver()
app = graph.compile(checkpointer=checkpointer)

# Display graph structure
display(Image(app.get_graph().draw_mermaid_png()))

# ------------------- RUN WORKFLOW -------------------
thread_config = {"configurable": {"thread_id": uuid.uuid4()}}

twitter_topic = input("\n📝 Enter your Twitter topic: ")
initial_state = {
    "twitter_topic": twitter_topic,
    "generated_post": [],
    "human_feedback": []
}

# Stream the graph with interactive feedback loop
for chunk in app.stream(initial_state, config=thread_config):
    for node_id, value in chunk.items():
        if node_id == "__interrupt__":
            while True:
                user_feedback = input(
                    "\n✏️ Feedback (or type 'done' to finish): ")
                app.invoke(Command(resume=user_feedback), config=thread_config)
                if user_feedback.lower() == "done":
                    break
