import streamlit as st
import requests
import uuid
import json
from pypdf import PdfReader
import io

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


uploaded_files = st.sidebar.file_uploader(
    "Upload Documents",
    type=["txt", "pdf"],
    accept_multiple_files=True
)

if uploaded_files and st.sidebar.button(
    "Upload Files"
):

    files_payload = []

    for file in uploaded_files:

        content = ""

        # =========================
        # TXT FILES
        # =========================

        if file.type == "text/plain":

            content = file.read().decode(
                "utf-8",
                errors="ignore"
            )

        # =========================
        # PDF FILES
        # =========================

        elif file.type == "application/pdf":

            pdf_reader = PdfReader(
                io.BytesIO(file.read())
            )

            for page in pdf_reader.pages:

                text = page.extract_text()

                if text:

                    content += text + "\n"

        files_payload.append({
            "filename": file.name,
            "content": content
        })

    response = requests.post(
        "http://127.0.0.1:8000/upload",
        json={
            "thread_id": st.session_state.thread_id,
            "documents": files_payload
        }
    )

    if response.status_code == 200:

        st.sidebar.success(
            "Documents uploaded"
        )

    else:

        st.sidebar.error(
            "Upload failed"
        )

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

for thread in threads[::-1]:

    thread_id = thread["thread_id"]

    title = thread["title"]

    if st.sidebar.button(
        title,
        key=thread_id
    ):

        st.session_state.thread_id = thread_id

        st.session_state.message_history = (
            load_conversation(thread_id)
        )

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