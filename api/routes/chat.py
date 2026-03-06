from fastapi import APIRouter, Request
from api.models.schema import ChatRequest, ChatResponse
# from api.middleware.throttle import limiter
from fitness_application.rag import get_answer

router = APIRouter()

@router.post("/chat", response_model=ChatResponse)
# @limiter.limit("5/minute")
async def chat(request:Request, body: ChatRequest):
    try:
        answer = await get_answer(body.query)
        return ChatResponse(answer=answer, source=body.source)
    except Exception as e:
        print(f"Error: {e}")
        raise
