#!/bin/bash
# Startup script for Internship Matcher

echo "🎯 Starting Internship Matcher Platform..."

# Check if Python is installed
if ! command -v python &> /dev/null; then
    echo "❌ Python is not installed. Please install Python 3.8+ first."
    exit 1
fi

# Check if pip is installed
if ! command -v pip &> /dev/null; then
    echo "❌ pip is not installed. Please install pip first."
    exit 1
fi

# Install dependencies
echo "📦 Installing dependencies..."
pip install -r requirements.txt

# Check if .env file exists
if [ ! -f .env ]; then
    echo "⚠️  .env file not found. Copying from .env.example..."
    cp .env.example .env
    echo "📝 Please edit .env file and add your GROQ_API_KEY"
    echo "   You can get it from: https://groq.com"
fi

# Create data directory if it doesn't exist
mkdir -p data

echo "✅ Setup complete!"
echo ""
echo "🚀 To start the application:"
echo "   1. Backend API: cd backend && python main.py"
echo "   2. Frontend:    cd frontend && streamlit run app.py"
echo ""
echo "📖 Documentation: http://localhost:8000/docs"
echo "🌐 Web Interface: http://localhost:8501"
