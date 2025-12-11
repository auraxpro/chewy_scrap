#!/bin/bash

# ============================================================================
# Dog Food Scoring API - Quick Start Script
# ============================================================================

set -e  # Exit on error

echo "🚀 Starting Dog Food Scoring API..."
echo ""

# ============================================================================
# Check Prerequisites
# ============================================================================

echo "📋 Checking prerequisites..."

# Check Python version
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is not installed"
    exit 1
fi

PYTHON_VERSION=$(python3 --version | cut -d' ' -f2 | cut -d'.' -f1,2)
echo "✅ Python $PYTHON_VERSION found"

# Check Docker
if ! command -v docker &> /dev/null; then
    echo "❌ Docker is not installed"
    exit 1
fi
echo "✅ Docker found"

# Check Docker Compose
if ! command -v docker-compose &> /dev/null; then
    echo "❌ Docker Compose is not installed"
    exit 1
fi
echo "✅ Docker Compose found"

echo ""

# ============================================================================
# Setup Virtual Environment
# ============================================================================

if [ ! -d ".venv" ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv .venv
    echo "✅ Virtual environment created"
else
    echo "✅ Virtual environment already exists"
fi

# Activate virtual environment
echo "🔌 Activating virtual environment..."
source .venv/bin/activate

echo ""

# ============================================================================
# Install Dependencies
# ============================================================================

echo "📥 Installing Python dependencies..."
pip install --upgrade pip > /dev/null 2>&1
pip install -r requirements.txt

echo "✅ Dependencies installed"
echo ""

# ============================================================================
# Setup Environment Variables
# ============================================================================

if [ ! -f ".env" ]; then
    echo "📝 Creating .env file from template..."
    cp .env.example .env
    echo "✅ .env file created"
    echo "⚠️  Please review and update .env with your settings"
else
    echo "✅ .env file already exists"
fi

echo ""

# ============================================================================
# Start Database
# ============================================================================

echo "🗄️  Starting PostgreSQL database..."
docker-compose up -d

echo "⏳ Waiting for database to be ready..."
sleep 5

# Check if database is ready
DB_READY=false
for i in {1..30}; do
    if docker-compose exec -T postgres pg_isready -U chewy_user > /dev/null 2>&1; then
        DB_READY=true
        break
    fi
    sleep 1
done

if [ "$DB_READY" = true ]; then
    echo "✅ Database is ready"
else
    echo "⚠️  Database may not be ready yet, but continuing..."
fi

echo ""

# ============================================================================
# Initialize Database
# ============================================================================

echo "🔧 Initializing database tables..."
python3 -c "from app.models.database import init_db; init_db()"
echo "✅ Database initialized"

echo ""

# ============================================================================
# Start API Server
# ============================================================================

echo "🌐 Starting API server..."
echo ""
echo "📍 API will be available at:"
echo "   - API Docs:   http://localhost:8000/docs"
echo "   - ReDoc:      http://localhost:8000/redoc"
echo "   - Health:     http://localhost:8000/health"
echo ""
echo "Press Ctrl+C to stop the server"
echo ""

# Start uvicorn server
python3 -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
