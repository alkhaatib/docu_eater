#!/usr/bin/env python3
"""
Simple script to stop all servers running on port 8000.
Useful for cleanup before starting the API server.
"""

import os
import signal
import subprocess
import time
import sys

def find_processes_on_port(port):
    """Find all processes using the specified port"""
    try:
        result = subprocess.run(
            f"lsof -i :{port} -t", 
            shell=True, 
            capture_output=True, 
            text=True
        )
        
        if result.stdout.strip():
            return [int(pid) for pid in result.stdout.strip().split('\n')]
        return []
    except Exception as e:
        print(f"Error finding processes on port {port}: {e}")
        return []

def kill_processes_on_port(port, force=False):
    """Kill all processes using the specified port"""
    pids = find_processes_on_port(port)
    
    if not pids:
        print(f"No processes found using port {port}")
        return True
    
    print(f"Found {len(pids)} process(es) using port {port}: {pids}")
    
    for pid in pids:
        try:
            # Try SIGTERM first
            print(f"Sending SIGTERM to process {pid}")
            os.kill(pid, signal.SIGTERM)
            
            # If force is True, also send SIGKILL after a short delay
            if force:
                time.sleep(0.5)
                if pid in find_processes_on_port(port):
                    print(f"Process {pid} still running, sending SIGKILL")
                    os.kill(pid, signal.SIGKILL)
        except ProcessLookupError:
            print(f"Process {pid} not found, it may have already terminated")
        except Exception as e:
            print(f"Error killing process {pid}: {e}")
    
    # Check if all processes were killed
    remaining = find_processes_on_port(port)
    if remaining:
        print(f"Warning: {len(remaining)} process(es) still using port {port}")
        return False
    
    print(f"Successfully freed port {port}")
    return True

if __name__ == "__main__":
    PORT = 8000
    if len(sys.argv) > 1:
        try:
            PORT = int(sys.argv[1])
        except ValueError:
            print(f"Invalid port number: {sys.argv[1]}")
            print(f"Using default port {PORT}")
    
    force = "--force" in sys.argv
    
    if kill_processes_on_port(PORT, force):
        print(f"Port {PORT} is now free to use")
        sys.exit(0)
    else:
        print(f"Failed to free port {PORT}")
        print("You may need to manually kill the processes or use --force")
        sys.exit(1) 