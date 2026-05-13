from langchain_core.tools import tool
from langchain.text_splitter import (
    RecursiveCharacterTextSplitter
)

from langchain_core.runnables import RunnableConfig

from langchain_core.documents import Document

from langchain_core.prompts import ChatPromptTemplate

from langchain_community.vectorstores import FAISS

from langchain_google_genai import (
    GoogleGenerativeAIEmbeddings
)

from db.checkpointer import conn

from services.llm_service import llm


embeddings = GoogleGenerativeAIEmbeddings(
    model="models/gemini-embedding-001"
)

@tool
def multiply(a: int, b: int) -> int:
    """
    Multiply two integers.
    """

    return a * b


from langchain.tools import tool

@tool
def search_uploaded_documents(query: str, config: RunnableConfig) -> str:
    """
    Use this tool whenever the user asks
    about uploaded PDFs, files, reports,
    notes, or documents.

    This tool has access to uploaded
    documents for the current chat.
    """

    thread_id = config["configurable"]["thread_id"]

    cursor = conn.cursor()

    rows = cursor.execute(
        """
        SELECT content
        FROM documents
        WHERE thread_id = ?
        """,
        (thread_id,)
    ).fetchall()

    if not rows:
        return "No uploaded documents found."

    # =========================
    # Convert DB rows to text
    # =========================

    docs = [row[0] for row in rows]

    # =========================
    # Chunking
    # =========================

    splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=200
    )

    split_docs = []

    for doc in docs:

        chunks = splitter.split_text(doc)

        for chunk in chunks:

            split_docs.append(
                Document(
                    page_content=chunk
                )
            )

    # =========================
    # Vector Store
    # =========================

    vector_store = FAISS.from_documents(
        split_docs,
        embeddings
    )

    # =========================
    # Retriever
    # =========================

    retriever = vector_store.as_retriever(
        search_kwargs={"k": 4}
    )

    retrieved_docs = retriever.invoke(query)

    context = "\n\n".join(
        [
            doc.page_content
            for doc in retrieved_docs
        ]
    )

    # =========================
    # Prompt
    # =========================

    prompt = ChatPromptTemplate.from_template(
        """
        Answer the question using the
        provided context only.

        Context:
        {context}

        Question:
        {query}
        """
    )

    chain = prompt | llm

    response = chain.invoke(
        {
            "context": context,
            "query": query
        }
    )

    return response.content