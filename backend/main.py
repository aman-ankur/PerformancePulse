"""
PerformancePulse Backend - FastAPI Application Entry Point
This file serves as the main entry point for uvicorn to run the FastAPI application.
It imports the app instance from the src package.
"""

import os
import sys
from pathlib import Path

# Add src directory to Python path
src_path = Path(__file__).parent / "src"
sys.path.append(str(src_path))

# Import the FastAPI app instance from src/main.py
from src.main import app

# This allows running the app with uvicorn main:app
if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True) 