"""
Router for WhatsApp message endpoints.
"""

from fastapi import APIRouter, HTTPException, status, Depends
from typing import List
from app.schemas.message import (
    CostCalculationRequest,
    CostCalculationResponse,
    BatchProcessRequest,
    BatchProcessResponse,
    ErrorResponse
)
from app.services.cost_calculator import cost_calculator_service
from app.services.supabase_service import supabase_service
from app.models.message import WhatsAppMessage, WhatsAppMessageResponse


router = APIRouter(prefix="/messages", tags=["Messages"])


@router.get(
    "/unprocessed",
    response_model=List[WhatsAppMessage],
    summary="Get unprocessed messages",
    description="Retrieve WhatsApp messages that haven't had their cost calculated yet"
)
async def get_unprocessed_messages(limit: int = 100):
    """
    Get a list of unprocessed WhatsApp messages.
    
    - **limit**: Maximum number of messages to return (default: 100)
    """
    try:
        messages = supabase_service.get_unprocessed_messages(limit=limit)
        return messages
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch unprocessed messages: {str(e)}"
        )


@router.post(
    "/calculate-cost",
    response_model=CostCalculationResponse,
    responses={
        404: {"model": ErrorResponse, "description": "Message not found"},
        400: {"model": ErrorResponse, "description": "Invalid request or processing error"}
    },
    summary="Calculate cost for a message",
    description="Classify a message and calculate its cost based on country and category"
)
async def calculate_cost(request: CostCalculationRequest):
    """
    Calculate the cost for a specific message.
    
    This endpoint:
    1. Retrieves the message from the database
    2. Classifies it using Mistral AI
    3. Looks up the pricing for the country and category
    4. Calculates the total cost
    5. Updates the message in the database
    
    - **message_id**: The ID of the message to process
    """
    try:
        response = cost_calculator_service.process_message(request.message_id)
        return response
    except ValueError as e:
        if "not found" in str(e):
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=str(e)
            )
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to calculate cost: {str(e)}"
        )


@router.post(
    "/batch-process",
    response_model=BatchProcessResponse,
    summary="Process messages in batch",
    description="Process multiple unprocessed messages at once"
)
async def batch_process(request: BatchProcessRequest):
    """
    Process multiple unprocessed messages in batch.
    
    This endpoint:
    1. Retrieves unprocessed messages from the database
    2. Processes each message (classify, calculate cost, update)
    3. Returns statistics and details of processed messages
    
    - **limit**: Maximum number of messages to process (default: 100, max: 1000)
    """
    try:
        processed_count, total_cost, messages = cost_calculator_service.process_messages_batch(
            limit=request.limit
        )
        
        return BatchProcessResponse(
            processed_count=processed_count,
            total_cost=total_cost,
            messages=messages
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to process batch: {str(e)}"
        )


@router.get(
    "/{message_id}",
    response_model=WhatsAppMessageResponse,
    responses={
        404: {"model": ErrorResponse, "description": "Message not found"}
    },
    summary="Get message by ID",
    description="Retrieve a specific WhatsApp message by its ID"
)
async def get_message(message_id: int):
    """
    Get a specific message by its ID.
    
    - **message_id**: The ID of the message to retrieve
    """
    try:
        message = supabase_service.get_message_by_id(message_id)
        if message is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Message {message_id} not found"
            )
        return message
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch message: {str(e)}"
        )


@router.get(
    "/",
    response_model=List[WhatsAppMessageResponse],
    summary="Get all messages",
    description="Retrieve all WhatsApp messages from the database"
)
async def get_all_messages(limit: int = 100, offset: int = 0):
    """
    Get all WhatsApp messages.
    
    - **limit**: Maximum number of messages to return (default: 100)
    - **offset**: Number of messages to skip (default: 0)
    """
    try:
        response = supabase_service.client.table("whatsapp_messages") \
            .select("*") \
            .range(offset, offset + limit - 1) \
            .execute()
        
        messages = []
        for row in response.data:
            message = WhatsAppMessageResponse(**row)
            messages.append(message)
        
        return messages
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch messages: {str(e)}"
        )
