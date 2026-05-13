from fastapi import APIRouter
from pydantic import BaseModel
from fastapi.responses import StreamingResponse

from langchain_core.messages import HumanMessage

from graph.builder import chatbot
from db.checkpointer import checkpointer, conn
import json
from services.title_service import generate_chat_title

router = APIRouter()


class ChatRequest(BaseModel):
    query: str
    thread_id: str

class UploadRequest(BaseModel):
    thread_id: str
    documents: list[dict]

@router.get("/")
def home():
    return {"message": "AI Backend Running"}


@router.get("/threads")
def get_threads():

    cursor = conn.cursor()

    rows = cursor.execute("""
        SELECT thread_id, title
        FROM thread_titles
    """).fetchall()

    threads = []

    for row in rows:

        threads.append({
            "thread_id": row[0],
            "title": row[1]
        })

    return {
        "threads": threads
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

    cursor = conn.cursor()

    existing_title = cursor.execute(
        """
        SELECT title
        FROM thread_titles
        WHERE thread_id = ?
        """,
        (request.thread_id,)
    ).fetchone()

    if not existing_title:

        generated_title = generate_chat_title(
            request.query
        )

        if generated_title:

            cursor.execute(
                """
                INSERT INTO thread_titles (
                    thread_id,
                    title
                )
                VALUES (?, ?)
                """,
                (
                    request.thread_id,
                    generated_title
                )
            )

            conn.commit()
    #     cursor.execute(
    #     """
    #     INSERT OR IGNORE INTO thread_titles (
    #         thread_id,
    #         title
    #     )
    #     VALUES (?, ?)
    #     """,
    #     (
    #         request.thread_id,
    #         "New Chat"
    #     )
    # )

    #     conn.commit()

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

@router.post("/upload")
def upload_documents(request: UploadRequest):

    cursor = conn.cursor()

    for doc in request.documents:

        cursor.execute(
            """
            INSERT INTO documents (
                thread_id,
                filename,
                content
            )
            VALUES (?, ?, ?)
            """,
            (
                request.thread_id,
                doc["filename"],
                doc["content"]
            )
        )

    conn.commit()

    return {
        "status": "success"
    }