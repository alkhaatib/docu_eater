#!/usr/bin/env python3
"""
Test script to debug API issues.
"""

import os
import sys
import json
from datetime import datetime

# Add the parent directory to the path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import the API models
from api.main import CrawlStatus, Task

# Create a test task
task_id = "test-task-id"
task_data = {
    "task_id": task_id,
    "status": "completed",
    "url": "https://example.com",
    "start_time": 1741955843.179609,
    "end_time": 1741955845.183081,
    "duration": 2.0034732818603516,
    "stats": {
        "total_pages": 10,
        "success_rate": 1.0,
        "crawl_time": 2.0,
        "url": "https://example.com",
        "start_time": "2025-03-14T13:37:25.181818"
    },
    "error": None
}

# Try to create a CrawlStatus object
try:
    # Format timestamps
    start_time = task_data.get("start_time", "")
    if isinstance(start_time, (int, float)):
        start_time = datetime.fromtimestamp(start_time).isoformat()
        
    end_time = task_data.get("end_time")
    if isinstance(end_time, (int, float)):
        end_time = datetime.fromtimestamp(end_time).isoformat()
    
    # Create CrawlStatus
    status = CrawlStatus(
        task_id=task_id,
        status=task_data.get("status", "unknown"),
        url=task_data.get("url", ""),
        stats=task_data.get("stats"),
        error=task_data.get("error"),
        duration=task_data.get("duration"),
        start_time=start_time,
        end_time=end_time
    )
    
    print("Successfully created CrawlStatus object:")
    print(status.model_dump_json(indent=2))
    
except Exception as e:
    print(f"Error creating CrawlStatus: {e}")
    import traceback
    traceback.print_exc()

# Print the model schema
print("\nCrawlStatus schema:")
print(CrawlStatus.model_json_schema()) 