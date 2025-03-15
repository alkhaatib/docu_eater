#!/bin/bash

# Setup script for Docu Eater backend

echo "Setting up Docu Eater backend..."

# Create virtual environment
echo "Creating virtual environment..."
python -m venv venv

# Activate virtual environment
echo "Activating virtual environment..."
source venv/bin/activate

# Install dependencies
echo "Installing dependencies..."
pip install -r requirements.txt

# Create results directory
echo "Creating results directory..."
mkdir -p results

# Copy .env.example to .env if .env doesn't exist
if [ ! -f .env ]; then
    echo "Creating .env file from .env.example..."
    cp .env.example .env
    echo "Please edit .env file with your configuration."
fi

echo "Setup complete!"
echo "To start the server, run: python main.py" 