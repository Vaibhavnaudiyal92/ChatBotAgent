from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_groq import ChatGroq
from dotenv import load_dotenv

load_dotenv()

# llm = ChatGoogleGenerativeAI(
#     model="gemini-2.0-flash"
# )
llm = ChatGroq(
    model="llama-3.3-70b-versatile",
    temperature=0.0
)