from fastapi import APIRouter, Request
from api.models.schema import ChatRequest, ChatResponse
from fitness_application.rag import get_answer
import uuid
from fitness_application import db 
from api.middleware.throttle import limiter

router = APIRouter()

@router.post("/chat", response_model=ChatResponse)
@limiter.limit("2/minute")
async def chat(request:Request, body: ChatRequest):
    try:
        answer = await get_answer(body.query)
        conversation_id = str(uuid.uuid4())

        answer_request = {
            "message":answer["message"],
            "image_urls": answer["image_urls"],
            "conversation_id":conversation_id
        }

        ## Save to database
        answer_data = {
            "answer":f'{answer["message"] + "/n".join(answer["image_urls"])}',
            "interface":body.source,
            "user":body.user,
            **answer  
        }
        db.save_conversation(
            conversation_id=conversation_id, 
            question=body.query, 
            answer_data=answer_data 
        )

        ## Response from request
        return ChatResponse(answer=answer_request, source=body.source)
    except Exception as e:
        print(f"Error: {e}")
        raise
