#!/bin/bash
# Backend Server Startup Script

cd "$(dirname "$0")"
source venv/bin/activate

echo "🚀 Starting Portfolio Backend Server..."
echo "📍 Server will be available at: http://localhost:8000"
echo "📚 API Documentation: http://localhost:8000/docs"
echo ""
echo "Press Ctrl+C to stop the server"
echo ""

uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
