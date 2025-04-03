from langgraph.graph import MessagesState, StateGraph, START, END
from langchain_openai import ChatOpenAI
from langchain_core.messages import SystemMessage

from prompts import (
    system_prompt_init
)

model = ChatOpenAI(model="gpt-4o")

class InitState(MessagesState):
    language: str
    skill_level: str

def initialization_node(state: InitState):
    language = state.get("language", "")
    skill_level = state.get("skill_level", "")

    messages = [SystemMessage(content=system_prompt_init)] + state["messages"]

    response = model.invoke(messages)
    return {"messages": response, "language": language, "skill_level": skill_level}

# Create Graph
builder = StateGraph(InitState)
builder.add_node("initialization", initialization_node)
# Logic
builder.add_edge(START, "initialization")
builder.add_edge("initialization", END)
# Compile
graph = builder.compile()