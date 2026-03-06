from pydantic import BaseModel
from typing import Literal

class ChatRequest(BaseModel):
    query: str
    source: Literal["telegram", "streamlit","cmd"]

class ChatResponse(BaseModel):
    answer: dict
    source:str

class HealthResponse(BaseModel):
    status: str
    version: str

class ChatRequestFeedback(BaseModel):
    feedback: str
    source: str