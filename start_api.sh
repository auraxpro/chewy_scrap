#!/bin/bash
# Start the FastAPI server

# Activate virtual environment if it exists
if [ -d ".venv" ]; then
    source .venv/bin/activate
fi

# Kill any existing process on port 8000
PORT=8000
PID=$(lsof -ti:$PORT)
if [ ! -z "$PID" ]; then
    echo "Killing existing process on port $PORT (PID: $PID)"
    kill -9 $PID 2>/dev/null || true
    sleep 1
fi

# Run the server using uvicorn
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
