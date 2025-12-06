#!/bin/bash
echo "Starting QorSense v1 (Next.js Edition)..."

# Check if virtual environment exists
if [ -d "backend/venv" ]; then
    echo "Using backend virtual environment..."
    UVICORN="backend/venv/bin/uvicorn"
elif [ -d "venv" ]; then
     echo "Using root virtual environment..."
     UVICORN="venv/bin/uvicorn"
else
    echo "Using system environment..."
    UVICORN="uvicorn"
fi

# Start Backend in background
echo "Launching Backend (FastAPI)..."
$UVICORN backend.main:app --reload --port 8000 &
BACKEND_PID=$!

# Wait for backend to initialize
echo "Waiting for backend to start..."
max_retries=30
count=0
while ! curl -s http://localhost:8000/ > /dev/null; do
    sleep 1
    count=$((count+1))
    if [ $count -ge $max_retries ]; then
        echo "Error: Backend failed to start."
        exit 1
    fi
    echo -n "."
done
echo " Backend is up!"

# Start Frontend
echo "Launching Frontend (Next.js)..."
cd frontend-next
npm run dev

# Cleanup function to kill backend when frontend exits
cleanup() {
    echo "Shutting down backend..."
    kill $BACKEND_PID
}

# Trap exit signals
trap cleanup EXIT
