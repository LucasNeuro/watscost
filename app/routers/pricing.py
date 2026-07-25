"""
Router for pricing-related endpoints.
"""

from fastapi import APIRouter, HTTPException, status
from typing import List
from app.models.pricing import MetaPricing, PricingResponse
from app.services.supabase_service import supabase_service
from app.schemas.message import ErrorResponse


router = APIRouter(prefix="/pricing", tags=["Pricing"])


@router.get(
    "/",
    response_model=List[MetaPricing],
    summary="Get all pricing entries",
    description="Retrieve all pricing entries from the meta_pricing table"
)
async def get_all_pricing():
    """
    Get all pricing entries.
    """
    try:
        pricing_entries = supabase_service.get_all_pricing()
        return pricing_entries
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch pricing: {str(e)}"
        )


@router.get(
    "/{country_code}/{category}",
    response_model=PricingResponse,
    responses={
        404: {"model": ErrorResponse, "description": "Pricing not found"}
    },
    summary="Get pricing for country and category",
    description="Retrieve pricing information for a specific country and message category"
)
async def get_pricing(country_code: str, category: str):
    """
    Get pricing for a specific country and category.
    
    - **country_code**: The country code (e.g., "55" for Brazil)
    - **category**: The message category (service, utility, authentication, marketing)
    """
    try:
        pricing = supabase_service.get_pricing(country_code, category)
        if pricing is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"No pricing found for country_code={country_code}, category={category}"
            )
        
        return PricingResponse(
            country_code=pricing.country_code,
            category=pricing.category,
            cost_per_message=pricing.cost_per_message,
            currency=pricing.currency
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch pricing: {str(e)}"
        )
