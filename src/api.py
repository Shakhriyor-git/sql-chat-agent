from fastapi import FastAPI
from pydantic import BaseModel
from src.agent import ask_agent


app = FastAPI(
    title="SQL Chat Agent",
    description="Ask questions about credit risk data in natural language",
    version="1.0"
)


# --- Request/Response models ---
class QuestionRequest(BaseModel):
    question: str


class AnswerResponse(BaseModel):
    question: str
    answer: str


# --- Endpoints ---
@app.get("/")
def health():
    """Health check — is the service running?"""
    return {"status": "ok", "message": "SQL Agent is running"}


@app.post("/ask", response_model=AnswerResponse)
def ask(request: QuestionRequest):
    """Ask the SQL agent a question about the credit database."""
    answer = ask_agent(request.question)
    return AnswerResponse(question=request.question, answer=answer)