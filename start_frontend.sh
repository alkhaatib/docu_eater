#!/bin/bash

# Enhanced script to start just the frontend with maximum stability
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
FRONTEND_DIR="$SCRIPT_DIR/frontend"

echo "===== Starting Docu Eater Frontend with Enhanced Stability ====="

# Kill any existing processes on port 3000
echo "Stopping any existing frontend servers..."
pkill -f "node.*react-scripts" || true

# Clear React's cache to prevent stale build issues
echo "Clearing React cache..."
if [ -d "$FRONTEND_DIR/node_modules/.cache" ]; then
  rm -rf "$FRONTEND_DIR/node_modules/.cache"
fi

# Try to clear browser's localStorage in case of corrupted data
echo "Creating clear-storage page..."
cat > "$FRONTEND_DIR/public/clear-storage.html" << EOL
<!DOCTYPE html>
<html>
<head>
  <title>Clear Local Storage</title>
  <script>
    localStorage.clear();
    document.addEventListener('DOMContentLoaded', function() {
      document.getElementById('status').textContent = 'localStorage cleared successfully!';
    });
  </script>
</head>
<body>
  <h1>Storage Cleared</h1>
  <p id="status">Processing...</p>
  <p><a href="/">Return to application</a></p>
</body>
</html>
EOL

# Start frontend with maximum stability settings
echo "Starting frontend with maximum stability settings..."
cd "$FRONTEND_DIR" && \
  NODE_OPTIONS="--max-old-space-size=8192 --max-http-header-size=16384" \
  FAST_REFRESH=false \
  BROWSER=none \
  REACT_APP_DISABLE_SPEEDY=true \
  GENERATE_SOURCEMAP=false \
  PORT=3000 \
  npm start

echo "Frontend process exited." 