from graph.state import ChatState
from langgraph.graph import StateGraph, START, END
from db.checkpointer import checkpointer
from graph.nodes import chat_node
from langgraph.prebuilt import ToolNode
from langgraph.prebuilt import tools_condition
from tools.basic_tools import multiply

graph = StateGraph(ChatState)
graph.add_node("chat_node", chat_node)
tool_node = ToolNode(
    tools=[multiply]
)

graph.add_node(
    "tools",
    tool_node
)
graph.add_edge(START, "chat_node")
graph.add_conditional_edges(
    "chat_node",
    tools_condition
)
graph.add_edge(
    "tools",
    "chat_node"
)

graph.add_edge("chat_node", END)

chatbot = graph.compile(checkpointer=checkpointer)