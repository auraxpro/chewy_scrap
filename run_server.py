#!/usr/bin/env python3
"""
Simple script to run the FastAPI server.

Usage:
    python run_server.py
    python run_server.py --host 0.0.0.0 --port 8000
"""

import sys
import uvicorn

if __name__ == "__main__":
    # Run the server
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
    )
