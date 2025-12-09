#!/bin/bash

echo "Setting up Chewy Scraper Project..."

# Check if virtual environment exists
if [ ! -d ".venv" ]; then
    echo "Creating virtual environment..."
    python3.10 -m venv .venv
fi

# Activate virtual environment
echo "Activating virtual environment..."
source .venv/bin/activate

# Install dependencies
echo "Installing Python dependencies..."
pip install -r requirements.txt

# Install Playwright browsers
echo "Installing Playwright browsers..."
playwright install chromium

# Start PostgreSQL
echo "Starting PostgreSQL database..."
docker-compose up -d

# Wait for database to be ready
echo "Waiting for database to be ready..."
sleep 5

echo ""
echo "Setup complete!"
echo ""
echo "To run the scraper:"
echo "  1. Activate virtual environment: source .venv/bin/activate"
echo "  2. Run scraper: python main.py"
echo ""

