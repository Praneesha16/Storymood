import uvicorn
from fastapi import FastAPI, Depends, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
import logging
import sys
import asyncio
import os

# Import configuration
import config

# Import routers
from routers import api_router
from database.dynamodb import dynamodb_client

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)

logger = logging.getLogger(__name__)

# Create FastAPI application
app = FastAPI(
    title="StoryArc API",
    description="AI-powered storytelling app that delivers personalized, emotionally resonant stories",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with actual origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global exception handler
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error(f"Unhandled exception: {str(exc)}")
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error. Please try again later."}
    )

# Startup event to initialize DynamoDB tables and create directories
@app.on_event("startup")
async def startup_db_client():
    try:
        # Initialize DynamoDB tables
        logger.info("Initializing DynamoDB tables...")
        await dynamodb_client.create_tables_if_not_exist()
        logger.info("DynamoDB tables initialized successfully")
        
        # Ensure audio directory exists
        logger.info("Ensuring audio directory exists...")
        os.makedirs(config.AUDIO_FILES_DIR, exist_ok=True)
        logger.info(f"Audio directory ready: {config.AUDIO_FILES_DIR}")
    except Exception as e:
        logger.error(f"Failed to initialize server resources: {str(e)}")

# Include all routers with API prefix
app.include_router(api_router, prefix=config.API_V1_PREFIX)

# Mount static files directory for serving audio files
static_dir = os.path.join(os.path.dirname(__file__), "static")
app.mount("/static", StaticFiles(directory=static_dir), name="static")

# Health check endpoint
@app.get("/health", tags=["Health"])
async def health_check():
    return {"status": "healthy"}

# Run the application with Uvicorn
if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
