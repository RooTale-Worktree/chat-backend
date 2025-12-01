from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse
from app.schemas import ChatRequest, ChatResponse
from app.core.orchestrator import handle_chat


router = APIRouter(prefix="/v1", tags=["chat"])


@router.post("/chat")
async def chat_endpoint(request: ChatRequest):
    """
    Endpoint to handle chat requests.
    Args:
        request: ChatRequest object containing user message and configurations.
    Returns:
        StreamingResponse: Generated chat response stream.
    """
    try:
        payload = request.model_dump()
        return StreamingResponse(handle_chat(payload), media_type="text/event-stream")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))