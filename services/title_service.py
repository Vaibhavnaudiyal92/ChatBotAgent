from services.llm_service import llm

IGNORE_MESSAGES = [
    "hi",
    "hello",
    "hey",
    "hii",
    "yo"
]


def generate_chat_title(query: str):

    if query.lower().strip() in IGNORE_MESSAGES:
        return None

    prompt = f"""
    Generate a short chat title
    in 3-4 words maximum.

    Query:
    {query}

    Examples:
    - Uttarakhand Weather Discussion
    - FastAPI Deployment Help
    - LangGraph RAG Architecture

    Only return the title.
    """

    response = llm.invoke(prompt)

    return response.content.strip()