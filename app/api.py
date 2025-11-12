"""FastAPI application for the AI Task Router."""
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import ValidationError
import logging
from app.schemas import TaskSpec, FinalPackage
from app.graph import execute_pipeline
from app.config import Config

# Validate configuration on startup
try:
    Config.validate()
except ValueError as e:
    logging.error(f"Configuration error: {e}")
    raise

# Initialize FastAPI app (minimal metadata for production)
app = FastAPI(
    title="AI Task Router",
    version="1.0.0",
    docs_url=None,  # Hide docs in production
    redoc_url=None  # Hide redoc in production
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify actual origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@app.get("/")
async def root():
    """Root endpoint - minimal response."""
    return {"status": "ok"}

@app.get("/health")
async def health():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "config": {
            "model": Config.MODEL_NAME,
            "temperature": Config.TEMPERATURE
        }
    }

@app.post("/generate", response_model=FinalPackage)
async def generate(task_spec: TaskSpec):
    """
    Main endpoint: Generate output for a task using the multi-agent router.
    
    Args:
        task_spec: Task specification with user query and optional parameters
    
    Returns:
        FinalPackage with routing trace, agent results, and final output
    
    Raises:
        HTTPException: If task execution fails
    """
    try:
        logger.info(f"Received task: {task_spec.user_query[:100]}...")
        
        # Validate task spec
        if not task_spec.user_query or not task_spec.user_query.strip():
            raise HTTPException(
                status_code=400,
                detail="user_query cannot be empty"
            )
        
        # Execute pipeline
        logger.info("Executing pipeline...")
        result = execute_pipeline(task_spec)
        
        logger.info("Pipeline completed successfully")
        return result
    
    except ValidationError as e:
        logger.error(f"Validation error: {e}")
        raise HTTPException(
            status_code=422,
            detail=f"Validation error: {str(e)}"
        )
    except ValueError as e:
        logger.error(f"Value error: {e}")
        raise HTTPException(
            status_code=400,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Unexpected error: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Internal server error: {str(e)}"
        )

@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    """Global exception handler."""
    logger.error(f"Unhandled exception: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={"detail": "An unexpected error occurred"}
    )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.api:app",
        host=Config.API_HOST,
        port=Config.API_PORT,
        reload=True
    )

