#!/bin/bash

# Docu Eater Startup Script
# This script will:
# 1. Kill any existing processes running on ports 8000 and 3000/3001
# 2. Start the backend API server
# 3. Start the frontend React application

# Function to handle error and cleanup
cleanup() {
  echo "Error occurred. Cleaning up..."
  # Kill any processes we started
  pkill -f "python.*api.main" || true
  pkill -f "node.*react-scripts" || true
  exit 1
}

# Set trap for Ctrl+C to properly cleanup
trap cleanup INT TERM

# Get the directory of this script
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BACKEND_DIR="$SCRIPT_DIR/backend"
FRONTEND_DIR="$SCRIPT_DIR/frontend"

echo "=== Docu Eater Startup ==="
echo "Backend directory: $BACKEND_DIR"
echo "Frontend directory: $FRONTEND_DIR"

# Check if virtual environment exists
if [ ! -d "$SCRIPT_DIR/venv" ]; then
  echo "Creating virtual environment..."
  python3 -m venv "$SCRIPT_DIR/venv"
fi

# Activate virtual environment
echo "Activating virtual environment..."
source "$SCRIPT_DIR/venv/bin/activate"

# Kill any existing processes on port 8000 (backend)
echo "Stopping any existing backend servers..."
python3 -c "
import socket, subprocess, os, signal
try:
    port = 8000
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    result = sock.connect_ex(('127.0.0.1', port))
    if result == 0:
        # Port is in use, find and kill process
        cmd = f\"lsof -i :{port} -t\"
        pids = subprocess.check_output(cmd, shell=True).decode().strip().split('\\n')
        for pid in pids:
            if pid:
                print(f'Found process using port {port}: {pid}')
                try:
                    os.kill(int(pid), signal.SIGTERM)
                    print(f'Sent SIGTERM to process {pid}')
                except Exception as e:
                    print(f'Failed to kill process {pid}: {e}')
    sock.close()
    print(f'Port {port} is now free to use')
except Exception as e:
    print(f'Error checking/freeing port: {e}')
"

# Kill any existing processes on port 3000/3001 (frontend)
echo "Stopping any existing frontend servers..."
pkill -f "node.*react-scripts" || true

# Make sure backend dependencies are installed
echo "Checking backend dependencies..."
if [ -f "$BACKEND_DIR/requirements.txt" ]; then
  pip install -r "$BACKEND_DIR/requirements.txt"
fi

# Make sure frontend dependencies are installed
echo "Checking frontend dependencies..."
if [ -f "$FRONTEND_DIR/package.json" ]; then
  # Check if node_modules exists
  if [ ! -d "$FRONTEND_DIR/node_modules" ]; then
    echo "Installing frontend dependencies..."
    cd "$FRONTEND_DIR" && npm install
  fi
fi

# Start the backend server with better error handling
echo "Starting backend API server..."
cd "$BACKEND_DIR" && python -m api.main > "$SCRIPT_DIR/backend_log.txt" 2>&1 &
BACKEND_PID=$!

# Wait a bit for the backend to start
sleep 2

# Check if backend is running
if ! ps -p $BACKEND_PID > /dev/null; then
  echo "Error: Backend server failed to start. Check backend_log.txt for details."
  cat "$SCRIPT_DIR/backend_log.txt"
  cleanup
fi

# Start the frontend with improved stability
echo "Starting frontend application with improved stability..."
# Start with increased memory limits and timeout
cd "$FRONTEND_DIR" && NODE_OPTIONS="--max-old-space-size=4096" BROWSER=none PORT=3000 npm start > "$SCRIPT_DIR/frontend_log.txt" 2>&1 &
FRONTEND_PID=$!

# Wait for frontend to start before continuing
sleep 5

# Check if frontend is still running
if ! ps -p $FRONTEND_PID > /dev/null; then
  echo "Error: Frontend application failed to start. Check frontend_log.txt for details."
  cat "$SCRIPT_DIR/frontend_log.txt"
  cleanup
fi

echo "=== Startup Complete ==="
echo "Backend running on http://localhost:8000"
echo "Frontend running on http://localhost:3000"
echo "Backend PID: $BACKEND_PID"
echo "Frontend PID: $FRONTEND_PID"
echo ""
echo "Press Ctrl+C to stop all servers"
echo "Use 'http://localhost:3000/clear-storage.html' to clear localStorage if needed"

# Keep the script alive
echo "Monitoring servers..."
while true; do
  sleep 5
  
  # Check the backend server
  if ! ps -p $BACKEND_PID > /dev/null; then
    echo "Backend server stopped unexpectedly. Checking logs..."
    tail -n 20 "$SCRIPT_DIR/backend_log.txt"
    echo "Attempting to restart backend server..."
    cd "$BACKEND_DIR" && python -m api.main > "$SCRIPT_DIR/backend_log.txt" 2>&1 &
    BACKEND_PID=$!
    sleep 2
    if ! ps -p $BACKEND_PID > /dev/null; then
      echo "Failed to restart backend server."
      cleanup
    else
      echo "Backend server restarted successfully."
    fi
  fi
  
  # Check the frontend server
  if ! ps -p $FRONTEND_PID > /dev/null; then
    echo "Frontend server stopped unexpectedly. Checking logs..."
    tail -n 20 "$SCRIPT_DIR/frontend_log.txt"
    echo "Attempting to restart frontend server..."
    cd "$FRONTEND_DIR" && NODE_OPTIONS="--max-old-space-size=4096" BROWSER=none PORT=3000 npm start > "$SCRIPT_DIR/frontend_log.txt" 2>&1 &
    FRONTEND_PID=$!
    sleep 5
    if ! ps -p $FRONTEND_PID > /dev/null; then
      echo "Failed to restart frontend server."
      cleanup
    else
      echo "Frontend server restarted successfully."
    fi
  fi
done 