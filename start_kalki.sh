#!/bin/bash

# Create logs directory if it doesn't exist
mkdir -p logs

# Activate virtual environment if it exists
if [ -d "venv" ]; then
    source venv/bin/activate
elif [ -d ".venv" ]; then
    source .venv/bin/activate
fi

# Check if Jan.ai is running
if ! curl -s http://0.0.0.0:8080/v1/models > /dev/null; then
    echo "⚠️  Warning: Jan.ai API server doesn't seem to be running"
    echo "Please start Jan.ai and enable the API server in settings"
    exit 1
fi

# Check for Tesseract
if ! command -v tesseract &> /dev/null; then
    echo "⚠️  Warning: Tesseract OCR not found"
    echo "Please install tesseract-ocr package for your system"
    exit 1
fi

# Start Kalki
echo "🤖 Starting Kalki..."
python main.py "$@" 

systemctl --user restart kalki.service 

systemctl --user stop kalki.service 