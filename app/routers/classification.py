"""
Router for message classification endpoints.
"""

from fastapi import APIRouter, HTTPException, status
from app.schemas.message import MessageClassificationRequest, MessageClassificationResponse
from app.services.mistral_service import mistral_service


router = APIRouter(prefix="/classify", tags=["Classification"])


@router.post(
    "/",
    response_model=MessageClassificationResponse,
    summary="Classify a message",
    description="Classify a WhatsApp message into one of the predefined categories using Mistral AI"
)
async def classify_message(request: MessageClassificationRequest):
    """
    Classify a message into a category.
    
    This endpoint uses Mistral AI to classify the message content into one of:
    - service
    - utility
    - authentication
    - marketing
    
    - **message**: The message content to classify
    """
    try:
        category = mistral_service.classify_message_with_fallback(request.message)
        
        return MessageClassificationResponse(
            message=request.message,
            category=category,
            confidence=None  # Mistral doesn't provide confidence scores in this implementation
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to classify message: {str(e)}"
        )
