#!/usr/bin/env python3
"""Simple script to run the API server locally."""
import uvicorn
from app.config import Config

if __name__ == "__main__":
    try:
        Config.validate()
    except ValueError as e:
        print(f"Error: {e}")
        print("Please set OPENAI_API_KEY in your .env file")
        exit(1)
    
    print(f"Starting AI Task Router API on {Config.API_HOST}:{Config.API_PORT}")
    print(f"API Documentation: http://{Config.API_HOST}:{Config.API_PORT}/docs")
    print(f"Health Check: http://{Config.API_HOST}:{Config.API_PORT}/health")
    
    uvicorn.run(
        "app.api:app",
        host=Config.API_HOST,
        port=Config.API_PORT,
        reload=True
    )

