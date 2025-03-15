#!/usr/bin/env python3
"""
Start the Docu Eater API server with automatic process killing.
This script ensures any existing processes on port 8000 are killed
before starting a fresh server instance.
"""

import os
import sys
import subprocess
import time

def main():
    """Main entry point for starting the server"""
    # Get the directory of this script
    script_dir = os.path.dirname(os.path.abspath(__file__))
    
    # First make sure no processes are using port 8000
    print("Checking for existing server processes...")
    stop_script = os.path.join(script_dir, "stop_servers.py")
    
    # Make sure the stop script is executable
    subprocess.run(["chmod", "+x", stop_script], check=True)
    
    # Run the stop script with --force to ensure all processes are killed
    subprocess.run([sys.executable, stop_script, "--force"], check=True)
    
    # Wait a moment for the port to be completely free
    time.sleep(1)
    
    # Now start the server
    print("Starting the Docu Eater API server...")
    try:
        # Use uvicorn directly for better process management
        subprocess.run([
            sys.executable, "-m", "uvicorn", 
            "api.main:app", 
            "--host", "0.0.0.0", 
            "--port", "8000",
            "--log-level", "info"
        ], cwd=script_dir, check=True)
    except KeyboardInterrupt:
        print("\nShutting down server...")
    except subprocess.CalledProcessError as e:
        print(f"Error starting server: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main() 