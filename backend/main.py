"""
Main application entry point for Docu Eater.

This module provides the main entry point for running the Docu Eater
application.
"""
import uvicorn
import os
import sys
import pathlib

# Add current directory to path to fix import issues
sys.path.append(str(pathlib.Path(__file__).parent))

# Import the FastAPI app
from api.main import app

if __name__ == "__main__":
    # Get port from environment or use default
    port = int(os.environ.get("PORT", 8000))
    
    # Run the application
    uvicorn.run(
        "api.main:app",
        host="0.0.0.0",
        port=port,
        reload=True  # Enable auto-reload for development
    ) 