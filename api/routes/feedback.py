from fastapi import APIRouter, Request
from api.models.schema import ChatRequest, ChatResponse, ChatRequestFeedback
from fitness_application import db 
from api.middleware.throttle import limiter

router = APIRouter()

@router.post("/feedback", response_model=ChatResponse)
@limiter.limit("2/minute")
async def feedback(request:Request, body:ChatRequestFeedback):
    try:
        print(f"request received: {body}")
        # Save feedback
        db.save_feedback(
            body.conversation_id,
            1 if body.feedback == "relevant" else -1
        )

        if body.feedback == "relevant":
            return ChatResponse(answer={"code":200, "response":"Successfuly received relevant feedback"}, source=body.source)
        else:
            return ChatResponse(answer={"code":200, "response":"Successfuly received non relevant"}, source=body.source)
    except Exception as e:
        print(f"Error: {e}")
        raise