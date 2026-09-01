#!/bin/bash

# Rei-chan AI Companion - Linux/Mac Startup Script

echo ""
echo "==============================================="
echo "れいちゃん AI Companion System"
echo "Local Setup & Launch"
echo "==============================================="
echo ""

# Check Node.js
if ! command -v node &> /dev/null; then
    echo "[ERROR] Node.js is not installed"
    echo "Please install Node.js 18+ from https://nodejs.org"
    exit 1
fi

echo "[OK] Node.js found: $(node --version)"

# Check Python
if ! command -v python3 &> /dev/null; then
    echo "[ERROR] Python 3 is not installed"
    echo "Please install Python 3.10+ from https://www.python.org"
    exit 1
fi

echo "[OK] Python found: $(python3 --version)"

# Install Node dependencies
echo ""
echo "[STEP 1/5] Installing Node.js dependencies..."
if [ -d "node_modules" ]; then
    echo "node_modules already exists, skipping..."
else
    npm install
    if [ $? -ne 0 ]; then
        echo "[ERROR] npm install failed"
        exit 1
    fi
fi

echo "[OK] Node dependencies installed"

# Install Python dependencies
echo ""
echo "[STEP 2/5] Installing Python dependencies..."
if [ -d "venv" ]; then
    echo "Python venv already exists, activating...
    source venv/bin/activate
else
    python3 -m venv venv
    source venv/bin/activate
    pip install -r requirements.txt
    if [ $? -ne 0 ]; then
        echo "[ERROR] pip install failed"
        exit 1
    fi
fi

echo "[OK] Python dependencies installed"

# Configuration
echo ""
echo "[STEP 3/5] Checking configuration..."
if [ -f ".env" ]; then
    echo ".env already exists"
else
    if [ -f ".env.example" ]; then
        cp .env.example .env
        echo "[OK] Created .env from template"
    else
        echo "[WARNING] .env.example not found, creating default"
        cat > .env << 'EOF'
NODE_ENV=development
PORT=3000
OLLAMA_URL=http://localhost:11434
OLLAMA_MODEL=mistral
SEARCH_PROVIDER=searxng_local
EOF
    fi
fi

echo "[OK] Configuration ready"

# Check Ollama
echo ""
echo "[STEP 4/5] Checking Ollama..."
if ! command -v ollama &> /dev/null; then
    echo "[INFO] Ollama not found, installing..."
    curl -fsSL https://ollama.ai/install.sh | sh
    echo "[OK] Ollama installed"
else
    echo "[OK] Ollama found"
fi

# Create directories
echo ""
echo "[STEP 5/5] Setting up directories..."
mkdir -p logs
mkdir -p memory_db
mkdir -p public/avatar

echo "[OK] Directories ready"

# Start application
echo ""
echo "==============================================="
echo "Starting Rei-chan server..."
echo "==============================================="
echo ""
echo "Server will run on http://localhost:3000"
echo "Scan QR code on phone to connect"
echo ""
echo "Press Ctrl+C to stop"
echo ""

# Start Ollama in background if not running
if ! pgrep -x "ollama" > /dev/null; then
    echo "Starting Ollama in background..."
    nohup ollama serve > /dev/null 2>&1 &
    sleep 5
fi

# Start Node server
node src/server.js
