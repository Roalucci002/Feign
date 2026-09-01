@echo off
REM Rei-chan AI Companion - Windows Startup Script
REM This script downloads and sets up everything needed to run Rei-chan locally

echo.
echo ===============================================
echo れいちゃん AI Companion System
echo Local Setup & Launch
echo ===============================================
echo.

REM Check if Node.js is installed
node --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Node.js is not installed or not in PATH
    echo Please install Node.js 18+ from https://nodejs.org
    pause
    exit /b 1
)

echo [OK] Node.js found

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python is not installed or not in PATH
    echo Please install Python 3.10+ from https://www.python.org
    pause
    exit /b 1
)

echo [OK] Python found

REM Install Node dependencies
echo.
echo [STEP 1/5] Installing Node.js dependencies...
if exist node_modules (
    echo node_modules already exists, skipping...
) else (
    call npm install
    if errorlevel 1 (
        echo [ERROR] npm install failed
        pause
        exit /b 1
    )
)

echo [OK] Node dependencies installed

REM Install Python dependencies
echo.
echo [STEP 2/5] Installing Python dependencies...
if exist venv (
    echo Python venv already exists, activating...
    call venv\Scripts\activate.bat
) else (
    python -m venv venv
    call venv\Scripts\activate.bat
    pip install -r requirements.txt
    if errorlevel 1 (
        echo [ERROR] pip install failed
        pause
        exit /b 1
    )
)

echo [OK] Python dependencies installed

REM Check if .env exists, if not copy from .env.example
echo.
echo [STEP 3/5] Checking configuration...
if exist .env (
    echo .env already exists
) else (
    if exist .env.example (
        copy .env.example .env
        echo [OK] Created .env from template
    ) else (
        echo [WARNING] .env.example not found, creating default .env
        (
            echo NODE_ENV=development
            echo PORT=3000
            echo HOST=localhost
            echo OLLAMA_URL=http://localhost:11434
            echo OLLAMA_MODEL=mistral
            echo SEARCH_PROVIDER=searxng_local
            echo SEARXNG_URL=http://localhost:8888
            echo TTS_ENGINE=piper
            echo AVATAR_SYSTEM=live2d
        ) > .env
    )
)

echo [OK] Configuration ready

REM Check if Ollama is installed
echo.
echo [STEP 4/5] Checking Ollama...
ollama --version >nul 2>&1
if errorlevel 1 (
    echo [INFO] Ollama not found, downloading...
    REM Ollama installer will be downloaded and run
    powershell -Command "& {
        $ProgressPreference = 'SilentlyContinue';
        Invoke-WebRequest -Uri 'https://ollama.ai/download/windows' -OutFile 'OllamaInstaller.exe';
        .\OllamaInstaller.exe;
        Remove-Item 'OllamaInstaller.exe';
    }"
    echo [OK] Ollama installed, please start it manually or it will start automatically
) else (
    echo [OK] Ollama found
)

REM Create necessary directories
echo.
echo [STEP 5/5] Setting up directories...
if not exist logs mkdir logs
if not exist memory_db mkdir memory_db
if not exist public\avatar mkdir public\avatar

echo [OK] Directories ready

REM Start the application
echo.
echo ===============================================
echo Starting Rei-chan server...
echo ===============================================
echo.
echo Server will run on http://localhost:3000
echo Scan QR code on phone to connect
echo.
echo Press Ctrl+C to stop
echo.

REM Start Ollama in background if not running
tasklist /FI "IMAGENAME eq ollama.exe" 2>NUL | find /I /N "ollama.exe">NUL
if errorlevel 1 (
    echo Starting Ollama in background...
    start /B ollama serve
    REM Give Ollama time to start
    timeout /t 5 /nobreak
)

REM Start the Node server
node src/server.js

pause
