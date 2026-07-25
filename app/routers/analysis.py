"""
Router for analysis endpoints.
These endpoints read from Supabase and provide analysis of WhatsApp messages.
"""

from fastapi import APIRouter, HTTPException, status, Query
from typing import Dict, Any, List
from app.services.analysis_service import analysis_service
from app.schemas.message import ErrorResponse


router = APIRouter(prefix="/analysis", tags=["Analysis"])


@router.get(
    "/messages",
    summary="Get all messages from Supabase",
    description="Retrieve all WhatsApp messages from the database for analysis"
)
async def get_all_messages(limit: int = Query(default=1000, ge=1, le=10000)):
    """
    Get all messages from Supabase.
    
    - **limit**: Maximum number of messages to return (default: 1000)
    """
    try:
        messages = analysis_service.get_all_messages(limit=limit)
        return {
            "count": len(messages),
            "messages": messages
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch messages: {str(e)}"
        )


@router.get(
    "/messages/without-cost",
    summary="Get messages without cost calculated",
    description="Retrieve messages that haven't had their cost calculated yet"
)
async def get_messages_without_cost(limit: int = Query(default=1000, ge=1, le=10000)):
    """
    Get messages without cost calculated.
    
    - **limit**: Maximum number of messages to return (default: 1000)
    """
    try:
        messages = analysis_service.get_messages_without_cost(limit=limit)
        return {
            "count": len(messages),
            "messages": messages
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch messages without cost: {str(e)}"
        )


@router.get(
    "/pricing",
    summary="Get all pricing entries",
    description="Retrieve all pricing entries from meta_pricing table"
)
async def get_all_pricing():
    """
    Get all pricing entries from Supabase.
    """
    try:
        pricing = analysis_service.get_all_pricing()
        return {
            "count": len(pricing),
            "pricing": pricing
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch pricing: {str(e)}"
        )


@router.get(
    "/pricing/active",
    summary="Get active pricing entries",
    description="Retrieve only active pricing entries (where end_date is null or in the future)"
)
async def get_active_pricing():
    """
    Get active pricing entries.
    """
    try:
        pricing = analysis_service.get_active_pricing()
        return {
            "count": len(pricing),
            "pricing": pricing
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch active pricing: {str(e)}"
        )


@router.post(
    "/analyze-all",
    summary="Analyze all messages",
    description="Analyze all WhatsApp messages: classify, find pricing, and calculate costs"
)
async def analyze_all_messages(limit: int = Query(default=1000, ge=1, le=10000)):
    """
    Analyze all messages from Supabase.
    
    This endpoint:
    1. Reads all messages from whatsapp_messages table
    2. Extracts text from JSONB mensagem field
    3. Classifies each message using Mistral AI
    4. Finds pricing based on country code and category
    5. Calculates costs
    6. Returns a complete analysis report
    
    - **limit**: Maximum number of messages to analyze (default: 1000)
    """
    try:
        report = analysis_service.analyze_all_messages(limit=limit)
        return report
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to analyze messages: {str(e)}"
        )


@router.post(
    "/process-and-update",
    summary="Process and update messages",
    description="Process messages without cost, calculate costs, and update them in Supabase"
)
async def process_and_update_messages(limit: int = Query(default=100, ge=1, le=1000)):
    """
    Process messages without cost and update them in Supabase.
    
    This endpoint:
    1. Finds messages without custo_total
    2. Classifies each message using Mistral AI
    3. Finds pricing based on country code and category
    4. Calculates costs
    5. Updates the messages in Supabase with the calculated costs
    6. Returns a processing report
    
    - **limit**: Maximum number of messages to process (default: 100)
    """
    try:
        report = analysis_service.process_and_update_messages(limit=limit)
        return report
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to process messages: {str(e)}"
        )


@router.get(
    "/statistics",
    summary="Get statistics",
    description="Get statistics about messages, costs, and pricing"
)
async def get_statistics():
    """
    Get statistics about the WhatsApp messages and costs.
    
    Returns:
    - Total messages
    - Messages with cost
    - Messages without cost
    - Total cost
    - Number of pricing entries
    """
    try:
        stats = analysis_service.get_statistics()
        return stats
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get statistics: {str(e)}"
        )


@router.get(
    "/analyze/{message_id}",
    summary="Analyze a specific message",
    description="Analyze a specific WhatsApp message by its UUID"
)
async def analyze_message(message_id: str):
    """
    Analyze a specific message.
    
    - **message_id**: The UUID of the message to analyze
    """
    try:
        message = analysis_service.supabase.get_message_by_id(message_id)
        if not message:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Message {message_id} not found"
            )
        
        analysis = analysis_service.analyze_message(message)
        return analysis
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to analyze message: {str(e)}"
        )
