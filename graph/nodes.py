from graph.state import ChatState
from services.llm_service import llm
from tools.basic_tools import multiply, search_uploaded_documents

tools = [multiply, search_uploaded_documents]
llm_with_tools = llm.bind_tools(tools)

def chat_node(state: ChatState):
    """
    messages is picking up all the stored messages in state
    response is storing the llm response based on the stored messages
    upon returning, the new message is added via add_messages function
    
    """
    messages = state['messages']
    response = llm_with_tools.invoke(messages)
    return {"messages": [response]}