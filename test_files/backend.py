from langgraph.graph import StateGraph, START, END
from typing import TypedDict, Annotated
from langchain_core.messages import BaseMessage
from langchain_google_genai import ChatGoogleGenerativeAI
from langgraph.checkpoint.memory import InMemorySaver
from langgraph.graph.message import add_messages
from dotenv import load_dotenv
import sqlite3
import os
from langgraph.checkpoint.sqlite import SqliteSaver

load_dotenv()
api_key = os.getenv("GOOGLE_API_KEY")

#print(api_key)
llm = ChatGoogleGenerativeAI(model = "gemini-3-flash-preview")

class ChatState(TypedDict):
    """
    add_messages is the name of function to add messages in the list
    BaseMessage is the object (complex data type)
    """
    messages: Annotated[list[BaseMessage], add_messages]

def chat_node(state: ChatState):
    """
    messages is picking up all the stored messages in state
    response is storing the llm response based on the stored messages
    upon returning, the new message is added via add_messages function
    
    """
    messages = state['messages']
    response = llm.invoke(messages)
    return {"messages": [response]}

conn = sqlite3.connect(database='chatbot.db', check_same_thread=False)
# Checkpointer
checkpointer = SqliteSaver(conn=conn)

graph = StateGraph(ChatState)
graph.add_node("chat_node", chat_node)
graph.add_edge(START, "chat_node")
graph.add_edge("chat_node", END)

chatbot = graph.compile(checkpointer=checkpointer)

def retrieve_all_threads():
    all_threads = set()
    for checkpoint in checkpointer.list(None):
        all_threads.add(checkpoint.config['configurable']['thread_id'])

    return list(all_threads)