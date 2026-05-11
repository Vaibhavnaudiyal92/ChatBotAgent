import streamlit as st
import requests
import uuid
import json

# ************************ API URLs ************************

BACKEND_URL = "http://127.0.0.1:8000/chat"
THREADS_URL = "http://127.0.0.1:8000/threads"

# ************************ Utility Functions ************************

def fetch_threads():

    try:

        response = requests.get(THREADS_URL)

        if response.status_code == 200:
            return response.json()["threads"]

        return []

    except:
        return []


def load_conversation(thread_id):

    try:

        response = requests.get(
            f"http://127.0.0.1:8000/thread/{thread_id}"
        )

        if response.status_code == 200:
            return response.json()["messages"]

        return []

    except:
        return []


def create_new_chat():

    st.session_state.thread_id = str(uuid.uuid4())

    st.session_state.message_history = []

# ************************ Session Setup ************************

if "thread_id" not in st.session_state:

    st.session_state.thread_id = str(uuid.uuid4())

if "message_history" not in st.session_state:

    st.session_state.message_history = []

# ************************ Sidebar ************************

st.sidebar.title("AI Agent Chatbot")

# New chat button
if st.sidebar.button("New Chat"):

    create_new_chat()

    st.rerun()

# Current thread
st.sidebar.write("Current Thread ID")

st.sidebar.code(st.session_state.thread_id)

# Persistent thread list
st.sidebar.divider()

st.sidebar.subheader("Saved Conversations")

threads = fetch_threads()

for thread_id in threads[::-1]:

    if st.sidebar.button(thread_id):

        st.session_state.thread_id = thread_id

        st.session_state.message_history = load_conversation(thread_id)

        st.rerun()

# ************************ Main UI ************************

st.title("LangGraph AI Assistant")

# Display old messages
for message in st.session_state.message_history:

    with st.chat_message(message["role"]):

        st.markdown(message["content"])

# ************************ User Input ************************

user_input = st.chat_input("Type your message...")

if user_input:

    # Store user message
    st.session_state.message_history.append(
        {
            "role": "user",
            "content": user_input
        }
    )

    # Display user message
    with st.chat_message("user"):

        st.markdown(user_input)

    payload = {
        "query": user_input,
        "thread_id": st.session_state.thread_id
    }

    # Assistant streaming response
    with st.chat_message("assistant"):

        response = requests.post(
            BACKEND_URL,
            json=payload,
            stream=True
        )

        assistant_placeholder = st.empty()

        full_response = ""

        for line in response.iter_lines(
            decode_unicode=True
        ):

            
            if line:

                try:

                    data = json.loads(line)

                    # TOOL CALL EVENT
                    if data["type"] == "tool":

                        st.info(
                            f"Calling Tool: {data['tool_name']}"
                        )

                    # AI RESPONSE TOKENS
                    elif data["type"] == "message":

                        full_response += data["content"]

                        assistant_placeholder.markdown(
                            full_response
                        )

                except json.JSONDecodeError:

                    continue

        ai_response = full_response

    # Save assistant response
    st.session_state.message_history.append(
        {
            "role": "assistant",
            "content": ai_response
        }
    )