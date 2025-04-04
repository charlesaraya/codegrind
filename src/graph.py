import json

from langgraph.graph import StateGraph, START, END
from langchain_openai import ChatOpenAI
from langchain_core.messages import SystemMessage, HumanMessage

from state import (
    UserInfoState
)

from prompts import (
    PROMPT_SYSTEM_WELCOME,
    PROMPT_SYSTEM_INIT,
)

model = ChatOpenAI(model="gpt-4o", temperature=0)

def parse_response(content):
    try:
        result = json.loads(content)
    except json.JSONDecodeError as e:
        print(f"JSON parsing failed. Raw content: {content}")
        raise ValueError(f"Invalid JSON: {e}")
    return result

def welcome_node(state: UserInfoState):
    messages = [SystemMessage(content=PROMPT_SYSTEM_WELCOME)] + state["messages"]
    response = model.invoke(messages)
    return {"messages": response}

def initialize_node(state: UserInfoState):
    name = state.get("name", "")
    language = state.get("language", "")
    skill_level = state.get("skill_level", "")

    messages = [SystemMessage(content=PROMPT_SYSTEM_INIT)]
    messages.append(state['messages'][-1])

    response = model.invoke(messages)
    result = parse_response(response.content)

    name = result.get("name", "") if not name else name
    language = result.get("language", "") if not language else language
    skill_level = result.get("skill_level", "") if not skill_level else skill_level

    return {"messages": state['messages'], "name": name, "language": language, "skill_level": skill_level}

def planning_node(state: UserInfoState):
    pass

def check_initialization(state: UserInfoState):
    state["name"] = state.get("name", "")
    state["language"] = state.get("language", "")
    state["skill_level"] = state.get("skill_level", "")
    if state["name"] and state["language"] and state["skill_level"]:
        return "init_complete"
    return "init_pending"

def build_graph():
    # Create Graph
    builder = StateGraph(UserInfoState)
    builder.add_node("welcome", welcome_node)
    builder.add_node("initializer", initialize_node)
    builder.add_node("planner", planning_node)
    # Logic
    builder.add_conditional_edges(START, check_initialization, {"init_pending": "welcome", "init_complete": "planner"})
    builder.add_edge("welcome", "initializer")
    builder.add_conditional_edges("initializer", check_initialization, {"init_pending": END, "init_complete": "planner"})
    builder.add_edge("planner", END)
    # Compile
    return builder.compile()