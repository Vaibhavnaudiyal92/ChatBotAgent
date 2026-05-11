from fastapi import FastAPI
from api.routes import router

app = FastAPI(
    title="AI Agent Backend",
    description="LangGraph + Gemini + FastAPI Backend",
    version="1.0.0"
)

@app.get("/")
def home():
    return {
        "message": "AI Backend Running"
    }

app.include_router(router)