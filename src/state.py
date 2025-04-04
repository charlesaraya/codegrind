from langgraph.graph import MessagesState

class UserInfoState(MessagesState):
    name: str
    language: str
    skill_level: str