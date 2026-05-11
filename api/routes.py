from fastapi import APIRouter
from pydantic import BaseModel
from fastapi.responses import StreamingResponse

from langchain_core.messages import HumanMessage

from graph.builder import chatbot
from db.checkpointer import checkpointer
import json

router = APIRouter()


class ChatRequest(BaseModel):
    query: str
    thread_id: str


@router.get("/")
def home():
    return {"message": "AI Backend Running"}


@router.get("/threads")
def get_threads():

    all_threads = set()

    for checkpoint in checkpointer.list(None):

        thread_id = checkpoint.config["configurable"]["thread_id"]

        all_threads.add(thread_id)

    return {
        "threads": list(all_threads)
    }


@router.get("/thread/{thread_id}")
def get_thread_messages(thread_id: str):

    state = chatbot.get_state(
        config={
            "configurable": {
                "thread_id": thread_id
            }
        }
    )

    messages = []

    for msg in state.values.get("messages", []):

        role = "assistant"

        if msg.type == "human":
            role = "user"

        messages.append({
            "role": role,
            "content": msg.content
        })

    return {
        "messages": messages
    }


@router.post("/chat")
def chat(request: ChatRequest):

    def generate():

        for message_chunk, metadata in chatbot.stream(
            {
                "messages": [
                    HumanMessage(content=request.query)
                ]
            },
            config={
                "configurable": {
                    "thread_id": request.thread_id
                }
            },
            stream_mode="messages"
        ):

            # TOOL CALL DETECTION
            if hasattr(message_chunk, "tool_calls"):

                if message_chunk.tool_calls:

                    for tool in message_chunk.tool_calls:

                        yield json.dumps({
                            "type": "tool",
                            "tool_name": tool["name"]
                        }) + "\n"


            if message_chunk.content:
                yield json.dumps({
                    "type": "message",
                    "content": message_chunk.content
                }) + "\n"

    return StreamingResponse(generate(), media_type="text/plain")