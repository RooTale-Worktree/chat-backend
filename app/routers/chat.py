from fastapi import APIRouter, HTTPException
from app.schemas import ChatRequest, ChatResponse
from app.core.orchestrator import handle_chat


router = APIRouter(prefix="/v1", tags=["chat"])


@router.post("/chat", response_model=ChatResponse)
async def chat_endpoint(request: ChatRequest):
    """
    Endpoint to handle chat requests.
    Args:
        request: ChatRequest object containing user message and configurations.
    Returns:
        ChatResponse: Generated chat response.
    """
    try:
        payload = request.model_dump()
        response_dict = handle_chat(payload)
        return ChatResponse(**response_dict)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))