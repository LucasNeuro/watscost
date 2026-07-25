"""
Main FastAPI application for WhatsApp Cost Calculator.
"""

from fastapi import FastAPI, APIRouter
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.routers import messages, pricing, classification
from app.core.database import supabase_client
from app.services.supabase_service import supabase_service
import uvicorn


def create_app() -> FastAPI:
    """
    Create and configure the FastAPI application.
    
    Returns:
        FastAPI: Configured FastAPI application instance
    """
    app = FastAPI(
        title=settings.app_name,
        version=settings.app_version,
        description="""
        # WhatsApp Cost Calculator API
        
        This API calculates the cost of WhatsApp messages by:
        1. Classifying messages using Mistral AI
        2. Looking up pricing based on country and category
        3. Updating the database with calculated costs
        
        ## Features
        
        * **Message Classification**: Automatically classify messages into categories (service, utility, authentication, marketing)
        * **Cost Calculation**: Calculate costs based on country-specific pricing
        * **Batch Processing**: Process multiple messages at once
        * **Database Integration**: Read and update messages in Supabase
        
        ## Authentication
        
        Currently, this API uses API keys configured in environment variables for:
        - Supabase (SUPABASE_URL, SUPABASE_KEY)
        - Mistral AI (MISTRAL_API_KEY)
        
        ## Rate Limiting
        
        The API respects Mistral AI's rate limits. For production use, consider:
        - Adding rate limiting middleware
        - Implementing caching for classification results
        - Using a queue system for batch processing
        """,
        docs_url="/docs",
        redoc_url="/redoc",
        openapi_url="/openapi.json"
    )
    
    # Add CORS middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],  # For development only, restrict in production
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    
    # Include routers
    main_router = APIRouter()
    main_router.include_router(messages.router)
    main_router.include_router(pricing.router)
    main_router.include_router(classification.router)
    app.include_router(main_router)
    
    # Root endpoint
    @app.get("/", tags=["Root"])
    async def root():
        """
        Root endpoint with API information.
        """
        return {
            "name": settings.app_name,
            "version": settings.app_version,
            "description": "WhatsApp Cost Calculator API",
            "docs": "/docs",
            "health": "ok"
        }
    
    # Health check endpoint
    @app.get("/health", tags=["Health"])
    async def health_check():
        """
        Health check endpoint to verify API is running.
        """
        # Test Supabase connection
        try:
            test_response = supabase_client.table("whatsapp_messages").select("id").limit(1).execute()
            db_status = "ok"
        except Exception as e:
            db_status = f"error: {str(e)}"
        
        return {
            "status": "ok",
            "database": db_status,
            "version": settings.app_version
        }
    
    return app


# Create the application instance
app = create_app()


if __name__ == "__main__":
    uvicorn.run(
        "app.main:app",
        host=settings.host,
        port=settings.port,
        reload=settings.debug,
        log_level="debug" if settings.debug else "info"
    )
