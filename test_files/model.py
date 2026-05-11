from langchain_google_genai import ChatGoogleGenerativeAI
from dotenv import load_dotenv
import os

load_dotenv()
api_key = os.getenv("GOOGLE_API_KEY")

model = ChatGoogleGenerativeAI(model = "gemini-3-flash-preview")

result = model.invoke('What is capital of India?')

print(result.text)
