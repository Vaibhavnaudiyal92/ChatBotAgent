from graph.state import ChatState
from services.llm_service import llm
from tools.basic_tools import multiply

tools = [multiply]
llm_with_tools = llm.bind_tools(tools)

def chat_node(state: ChatState):
    """
    messages is picking up all the stored messages in state
    response is storing the llm response based on the stored messages
    upon returning, the new message is added via add_messages function
    
    """
    messages = state['messages']
    response = llm.invoke(messages)
    return {"messages": [response]}