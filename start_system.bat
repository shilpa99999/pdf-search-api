@echo off
echo ================================================
echo         PDF Search System - Quick Start
echo ================================================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python 3.8+ and try again
    pause
    exit /b 1
)

echo Checking dependencies...
python -c "import flask, sentence_transformers, faiss" >nul 2>&1
if %errorlevel% neq 0 (
    echo Installing dependencies...
    pip install -r requirements.txt
    if %errorlevel% neq 0 (
        echo ERROR: Failed to install dependencies
        pause
        exit /b 1
    )
)

echo Checking PDF data...
if not exist "pdf_search_data.pkl" (
    echo.
    echo WARNING: PDF search data not found!
    echo Please run the Jupyter notebook first:
    echo   jupyter notebook pdf_search_system.ipynb
    echo.
    echo Then execute all cells to process your PDFs.
    echo.
    pause
    exit /b 1
)

echo.
echo Starting PDF Search System...
echo ================================================
echo  API Documentation: http://localhost:5000
echo  Chat Interface:    http://localhost:5000/chat-ui
echo ================================================
echo.
echo Press Ctrl+C to stop the server
echo.

python app.py

pause
