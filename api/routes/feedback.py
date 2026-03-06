from fastapi import APIRouter, Request
from api.models.schema import ChatRequest, ChatResponse, ChatRequestFeedback
# from api.middleware.throttle import limiter

router = APIRouter()

@router.post("/feedback", response_model=ChatResponse)
async def feedback(request:Request, body:ChatRequestFeedback):
    try:
        print(f"request received: {body}")
        if body.feedback == "relevant":
            return ChatResponse(answer={"code":200, "response":"Successfuly received relevant feedback"}, source=body.source)
        else:
            return ChatResponse(answer={"code":200, "response":"Successfuly received non relevant"}, source=body.source)
    except Exception as e:
        print(f"Error: {e}")
        raise