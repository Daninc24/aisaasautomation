#!/bin/bash

# AutomateIQ AI Engine Startup Script

echo "🤖 Starting AutomateIQ AI Engine..."

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "❌ Virtual environment not found. Please run setup first:"
    echo "   cd .. && ./setup.sh"
    exit 1
fi

# Activate virtual environment
source venv/bin/activate

# Check if dependencies are installed
if ! python -c "import fastapi" 2>/dev/null; then
    echo "📦 Installing dependencies..."
    pip install -r requirements.txt
    python -m spacy download en_core_web_sm
fi

# Set environment variables if .env exists
if [ -f "../.env" ]; then
    export $(grep -v '^#' ../.env | xargs)
fi

# Start the AI engine
echo "🚀 Starting AI Engine on http://localhost:8000"
echo "📚 API Documentation: http://localhost:8000/docs"
echo "🛑 Press Ctrl+C to stop"

uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload