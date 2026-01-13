@echo off
REM Startup script for Internship Matcher (Windows)

echo 🎯 Starting Internship Matcher Platform...

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Python is not installed. Please install Python 3.8+ first.
    pause
    exit /b 1
)

REM Install dependencies
echo 📦 Installing dependencies...
pip install -r requirements.txt

REM Check if .env file exists
if not exist .env (
    echo ⚠️  .env file not found. Copying from .env.example...
    copy .env.example .env
    echo 📝 Please edit .env file and add your GROQ_API_KEY
    echo    You can get it from: https://groq.com
)

REM Create data directory if it doesn't exist
if not exist data mkdir data

echo ✅ Setup complete!
echo.
echo 🚀 To start the application:
echo    1. Backend API: cd backend ^&^& python main.py
echo    2. Frontend:    cd frontend ^&^& streamlit run app.py
echo.
echo 📖 Documentation: http://localhost:8000/docs
echo 🌐 Web Interface: http://localhost:8501

pause
