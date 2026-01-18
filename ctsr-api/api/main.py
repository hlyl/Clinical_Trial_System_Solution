"""Main FastAPI application for CTSR API."""

import logging
from contextlib import asynccontextmanager
from typing import AsyncGenerator

from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from api import __version__
from api.config import get_settings
from api.db import close_db, init_db
from api.exceptions import CTSRException

# Configure logging
logging.basicConfig(
    level=get_settings().log_level,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator:
    """Application lifespan events."""
    # Startup
    logger.info("Starting CTSR API...")
    init_db()
    logger.info("Database initialized")
    
    yield
    
    # Shutdown
    logger.info("Shutting down CTSR API...")
    await close_db()
    logger.info("Database connections closed")


# Create FastAPI app
app = FastAPI(
    title="Clinical Trial Systems Register (CTSR) API",
    description="REST API for the Clinical Trial Systems Register - maintaining inventory of "
    "computerized systems used in clinical trials per ICH E6(R3) requirements.",
    version=__version__,
    lifespan=lifespan,
)

# Configure CORS
settings = get_settings()
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Exception handlers
@app.exception_handler(CTSRException)
async def ctsr_exception_handler(request: Request, exc: CTSRException) -> JSONResponse:
    """Handle custom CTSR exceptions."""
    logger.error(f"CTSR Exception: {exc.error_code} - {exc.message}", extra={"details": exc.details})
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": exc.error_code,
            "message": exc.message,
            "details": exc.details,
        },
    )


@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """Handle unexpected exceptions."""
    logger.exception("Unhandled exception", exc_info=exc)
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "error": "INTERNAL_SERVER_ERROR",
            "message": "An unexpected error occurred",
            "details": {},
        },
    )


# Register routers
from api.routers import admin, confirmations, health, lookups, systems, trials, vendors

app.include_router(health.router, tags=["Health"])
app.include_router(lookups.router, prefix="/api/v1", tags=["Lookups"])
app.include_router(vendors.router, prefix="/api/v1", tags=["Vendors"])
app.include_router(systems.router, prefix="/api/v1", tags=["Systems"])
app.include_router(trials.router, prefix="/api/v1", tags=["Trials"])
app.include_router(confirmations.router, prefix="/api/v1", tags=["Confirmations"])
app.include_router(admin.router, prefix="/api/v1/admin", tags=["Admin"])


@app.get("/", include_in_schema=False)
async def root():
    """Root endpoint - redirect to docs."""
    return {
        "message": "CTSR API",
        "version": __version__,
        "docs": "/docs",
        "health": "/health",
    }


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "api.main:app",
        host=settings.api_host,
        port=settings.api_port,
        reload=settings.api_debug,
    )
