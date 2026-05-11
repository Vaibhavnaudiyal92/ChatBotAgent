from typing import TypedDict, Annotated
from langgraph.graph.message import add_messages
from langchain_core.messages import BaseMessage


class ChatState(TypedDict):
    """
    add_messages is the name of function to add messages in the list
    BaseMessage is the object (complex data type)
    """
    messages: Annotated[list[BaseMessage], add_messages]