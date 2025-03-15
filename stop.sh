#!/bin/bash

# Docu Eater Shutdown Script
# This script will kill any running processes related to Docu Eater

echo "=== Stopping Docu Eater ==="

# Get the directory of this script
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BACKEND_DIR="$SCRIPT_DIR/backend"

# Kill any processes on port 8000 (backend)
echo "Stopping backend servers..."
if [ -f "$BACKEND_DIR/stop_servers.py" ]; then
  python3 "$BACKEND_DIR/stop_servers.py" --force
else
  echo "stop_servers.py not found, using pkill instead"
  pkill -f "python.*uvicorn" || true
fi

# Kill any processes running React (frontend)
echo "Stopping frontend servers..."
pkill -f "node.*react-scripts" || true

echo "=== Docu Eater Stopped ===" 