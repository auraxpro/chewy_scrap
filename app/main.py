"""
Main FastAPI application for the Dog Food Scoring API.

This module initializes and configures the FastAPI application, including
middleware, routers, and startup/shutdown events.
"""

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.api.v1.router import api_router
from app.config import (
    API_DESCRIPTION,
    API_TITLE,
    API_VERSION,
    CORS_ORIGINS,
    DEBUG_MODE,
)
from app.models.database import init_db


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Lifespan context manager for startup and shutdown events.

    This function runs when the application starts up and shuts down,
    handling initialization and cleanup tasks.
    """
    # Startup
    print("🚀 Starting Dog Food Scoring API...")
    print("📊 Initializing database...")
    init_db()
    print("✅ Database initialized successfully!")

    yield

    # Shutdown
    print("👋 Shutting down Dog Food Scoring API...")


# Create FastAPI application
app = FastAPI(
    title=API_TITLE,
    description=API_DESCRIPTION,
    version=API_VERSION,
    lifespan=lifespan,
    debug=DEBUG_MODE,
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
)

# Configure CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Include API routers
app.include_router(api_router, prefix="/api/v1")


@app.get("/", tags=["Root"])
async def root():
    """
    Root endpoint providing API information.

    Returns:
        dict: API information including name, version, and status
    """
    return {
        "name": API_TITLE,
        "version": API_VERSION,
        "status": "running",
        "docs": "/docs",
        "redoc": "/redoc",
    }


@app.get("/health", tags=["Health"])
async def health_check():
    """
    Health check endpoint for monitoring.

    Returns:
        dict: Health status of the API
    """
    return {
        "status": "healthy",
        "version": API_VERSION,
    }


@app.exception_handler(404)
async def not_found_handler(request, exc):
    """
    Custom 404 error handler.

    Args:
        request: The request object
        exc: The exception

    Returns:
        JSONResponse: Custom 404 error response
    """
    return JSONResponse(
        status_code=404,
        content={
            "error": "Not Found",
            "message": f"The requested resource at {request.url.path} was not found",
            "status_code": 404,
        },
    )


@app.exception_handler(500)
async def internal_error_handler(request, exc):
    """
    Custom 500 error handler.

    Args:
        request: The request object
        exc: The exception

    Returns:
        JSONResponse: Custom 500 error response
    """
    return JSONResponse(
        status_code=500,
        content={
            "error": "Internal Server Error",
            "message": "An unexpected error occurred. Please try again later.",
            "status_code": 500,
        },
    )


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=DEBUG_MODE,
    )
