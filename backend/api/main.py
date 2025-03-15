"""
FastAPI application for Docu Eater.

Provides API endpoints for crawling documentation websites and retrieving
the resulting documentation maps.
"""
from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
import uuid
import json
import os
from typing import Dict, Optional, Any, List
import sys
import pathlib
import time
import traceback
import asyncio
from datetime import datetime
import signal
import socket
import subprocess
import uvicorn

# Add parent directory to path to fix import issues
sys.path.append(str(pathlib.Path(__file__).parent.parent))

# First, let's ensure no other processes are using port 8000
def is_port_in_use(port: int) -> bool:
    """Check if port is already in use"""
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        return s.connect_ex(('127.0.0.1', port)) == 0

def kill_processes_on_port(port: int, force: bool = True):
    """Kill all processes using the specified port"""
    try:
        # Find processes using the port
        result = subprocess.run(
            f"lsof -i :{port} -t", 
            shell=True, 
            capture_output=True, 
            text=True
        )
        
        if result.stdout.strip():
            pids = [int(pid) for pid in result.stdout.strip().split('\n')]
            print(f"Found {len(pids)} process(es) using port {port}: {pids}")
            
            for pid in pids:
                try:
                    # Skip own process
                    if pid == os.getpid():
                        continue
                        
                    # Try SIGTERM first
                    print(f"Sending SIGTERM to process {pid}")
                    os.kill(pid, signal.SIGTERM)
                    
                    # If force is True, also send SIGKILL after a short delay
                    if force:
                        time.sleep(0.5)
                        try:
                            # Check if process still exists
                            os.kill(pid, 0)
                            print(f"Process {pid} still running, sending SIGKILL")
                            os.kill(pid, signal.SIGKILL)
                        except OSError:
                            # Process is already gone
                            pass
                except ProcessLookupError:
                    print(f"Process {pid} not found, it may have already terminated")
                except Exception as e:
                    print(f"Error killing process {pid}: {e}")
            
            print(f"Killed all processes using port {port}")
            # Wait a bit for the port to be fully released
            time.sleep(1)
            return True
        else:
            print(f"No processes found using port {port}")
            return True
    except Exception as e:
        print(f"Error killing processes on port {port}: {e}")
        return False

# Kill any existing processes using port 8000 before importing other modules
PORT = 8000
kill_processes_on_port(PORT)

# Import the real crawler components
from crawler.crawler import DocumentCrawler, CrawlRequest, CrawlResult
from crawler.doc_mapper import DocumentMapper, DocMap
print("Using real crawler implementation")

# Create the FastAPI app
app = FastAPI(
    title="Docu Eater API",
    description="API for crawling documentation websites and generating documentation maps",
    version="0.1.0",
)

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # For development; restrict in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Create results directory if it doesn't exist
results_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "results")
os.makedirs(results_dir, exist_ok=True)

# Dictionary to store crawl tasks
crawl_tasks = {}

# Load existing tasks from the filesystem on startup
def load_saved_tasks():
    """Load saved tasks from the filesystem on startup."""
    try:
        # Get all subdirectories in the results directory
        task_dirs = [d for d in os.listdir(results_dir) if os.path.isdir(os.path.join(results_dir, d))]
        
        loaded_count = 0
        for task_id in task_dirs:
            task_dir = os.path.join(results_dir, task_id)
            task_meta_path = os.path.join(task_dir, "task_metadata.json")
            
            if os.path.exists(task_meta_path):
                try:
                    with open(task_meta_path, "r") as f:
                        task_data = json.load(f)
                    
                    # Add to crawl_tasks
                    crawl_tasks[task_id] = task_data
                    loaded_count += 1
                except Exception as e:
                    print(f"Error loading task {task_id}: {e}")
        
        print(f"Loaded {loaded_count} tasks from filesystem")
    except Exception as e:
        print(f"Error loading tasks from filesystem: {e}")

# Load tasks on startup
load_saved_tasks()

# Create crawler and mapper instances
crawler = DocumentCrawler()
doc_mapper = DocumentMapper()

class CrawlResponse(BaseModel):
    """Response model for crawl requests."""
    task_id: str
    status: str
    url: str
    
    model_config = {"extra": "ignore"}

class CrawlStatus(BaseModel):
    """Response model for the status of a crawl task."""
    task_id: str
    status: str
    url: str
    stats: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
    duration: Optional[float] = None
    start_time: Optional[str] = None
    end_time: Optional[str] = None
    
    model_config = {"extra": "ignore"}

class Task(BaseModel):
    """Model for a crawl task."""
    task_id: str
    status: str
    url: str
    start_time: Optional[str] = None
    end_time: Optional[str] = None
    duration: Optional[float] = None
    stats: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
    
    model_config = {"extra": "ignore"}
    
    @classmethod
    def from_task_data(cls, task_id: str, task_data: Dict[str, Any]) -> "Task":
        """Create a Task instance from task data dictionary, handling timestamp conversion."""
        # Format timestamps as strings if they are floats or ints
        start_time = task_data.get("start_time")
        if isinstance(start_time, (int, float)):
            start_time = datetime.fromtimestamp(start_time).isoformat()
            
        end_time = task_data.get("end_time")
        if isinstance(end_time, (int, float)):
            end_time = datetime.fromtimestamp(end_time).isoformat()
        
        return cls(
            task_id=task_id,
            status=task_data.get("status", "unknown"),
            url=task_data.get("url", ""),
            start_time=start_time,
            end_time=end_time,
            duration=task_data.get("duration"),
            stats=task_data.get("stats"),
            error=task_data.get("error"),
        )

class CrawlTask(BaseModel):
    id: Optional[str] = None
    url: str
    max_depth: int = 3
    max_pages: int = 100
    respect_robots_txt: bool = True
    user_agent: str = "Docu-Eater/1.0"
    detect_nav_menu: bool = True

async def perform_crawl(task_id: str, request: CrawlRequest):
    """
    Background task to perform a crawl operation.
    
    Args:
        task_id: ID of the crawl task.
        request: Crawl request parameters.
    """
    # Record the start time to track how long the crawl takes
    start_time = time.time()
    
    try:
        # Update task status
        crawl_tasks[task_id]["status"] = "initializing"
        crawl_tasks[task_id]["start_time"] = start_time
        
        # Save task metadata
        save_task_metadata(task_id)
        
        print(f"Starting crawl task {task_id} for URL: {request.url}")
        
        # Update task status
        crawl_tasks[task_id]["status"] = "crawling"
        save_task_metadata(task_id)
        
        # Perform the crawl
        try:
            crawl_result = await crawler.crawl_site(request)
            print(f"Crawl completed for task {task_id}, found {len(crawl_result.pages)} pages")
        except Exception as crawl_error:
            print(f"Error during crawling for task {task_id}: {str(crawl_error)}")
            traceback.print_exc()
            raise crawl_error
        
        # Generate documentation map
        try:
            doc_map = doc_mapper.generate_map(crawl_result)
            print(f"Doc map generated for task {task_id} with {len(doc_map.pages)} pages")
        except Exception as map_error:
            print(f"Error generating doc map for task {task_id}: {str(map_error)}")
            traceback.print_exc()
            raise map_error
        
        # Save results to file
        save_results(task_id, crawl_result, doc_map)
        
        # Update task status
        crawl_tasks[task_id]["status"] = "completed"
        crawl_tasks[task_id]["stats"] = crawl_result.crawl_stats
        
        # Ensure pages_indexed is set in stats
        if "stats" in crawl_tasks[task_id] and "total_pages" in crawl_tasks[task_id]["stats"]:
            if "pages_indexed" not in crawl_tasks[task_id]["stats"]:
                crawl_tasks[task_id]["stats"]["pages_indexed"] = crawl_tasks[task_id]["stats"]["total_pages"]
        
        crawl_tasks[task_id]["end_time"] = time.time()
        crawl_tasks[task_id]["duration"] = time.time() - start_time
        
        # Save task metadata
        save_task_metadata(task_id)
        
    except Exception as e:
        # Update task status with error
        crawl_tasks[task_id]["status"] = "failed"
        crawl_tasks[task_id]["error"] = str(e)
        crawl_tasks[task_id]["end_time"] = time.time()
        crawl_tasks[task_id]["duration"] = time.time() - start_time
        
        # Save task metadata
        save_task_metadata(task_id)
        
        print(f"Error in crawl task {task_id}: {str(e)}")
        traceback.print_exc()

def save_results(task_id: str, crawl_result: CrawlResult, doc_map: DocMap):
    """
    Save crawl results to files.
    
    Args:
        task_id: ID of the crawl task.
        crawl_result: Crawl result to save.
        doc_map: Documentation map to save.
    """
    # Create task directory
    task_dir = os.path.join(results_dir, task_id)
    os.makedirs(task_dir, exist_ok=True)
    
    # Save crawl result
    with open(os.path.join(task_dir, "crawl_result.json"), "w") as f:
        f.write(crawl_result.model_dump_json(indent=2))
    
    # Save doc map
    with open(os.path.join(task_dir, "doc_map.json"), "w") as f:
        f.write(doc_map.model_dump_json(indent=2))
    
    # Save task metadata
    save_task_metadata(task_id)

def save_task_metadata(task_id: str):
    """
    Save task metadata to file for persistence between server restarts.
    
    Args:
        task_id: ID of the crawl task.
    """
    if task_id in crawl_tasks:
        task_dir = os.path.join(results_dir, task_id)
        os.makedirs(task_dir, exist_ok=True)
        
        with open(os.path.join(task_dir, "task_metadata.json"), "w") as f:
            json.dump(crawl_tasks[task_id], f, indent=2, default=str)

@app.post("/api/crawl", response_model=CrawlResponse)
async def start_crawl(request: CrawlRequest, background_tasks: BackgroundTasks):
    """
    Start a crawl operation.
    
    Args:
        request: Crawl request parameters.
        background_tasks: FastAPI background tasks.
        
    Returns:
        Crawl response with task ID.
    """
    try:
        # Log the request for debugging
        print(f"Received crawl request: {request.model_dump()}")
        
        # Validate URL format
        if not request.url.startswith(('http://', 'https://')):
            raise ValueError("URL must start with http:// or https://")
        
        # Generate task ID
        task_id = str(uuid.uuid4())
        
        # Store task
        crawl_tasks[task_id] = {
            "url": request.url,
            "status": "queued",
            "request": request.model_dump(),
        }
        
        # Save task metadata
        save_task_metadata(task_id)
        
        # Start crawl in background
        background_tasks.add_task(perform_crawl, task_id, request)
        
        return CrawlResponse(
            task_id=task_id,
            status="queued",
            url=request.url
        )
    except Exception as e:
        print(f"Error in start_crawl: {str(e)}")
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Failed to start crawl: {str(e)}")

@app.get("/api/crawl/{task_id}", response_model=CrawlStatus)
async def get_crawl_status(task_id: str):
    """
    Get the status of a crawl task.
    
    Args:
        task_id: ID of the crawl task.
        
    Returns:
        Status of the crawl task.
    """
    # First check if task exists in memory
    if task_id in crawl_tasks:
        task = crawl_tasks[task_id]
    else:
        # Check if task exists on disk but not loaded in memory
        task_dir = os.path.join(results_dir, task_id)
        task_meta_path = os.path.join(task_dir, "task_metadata.json")
        
        if os.path.exists(task_meta_path):
            # Try to load task metadata from disk
            try:
                with open(task_meta_path, "r") as f:
                    task = json.load(f)
                # Add to in-memory tasks
                crawl_tasks[task_id] = task
            except Exception as e:
                print(f"Error loading task {task_id} from disk: {e}")
                raise HTTPException(status_code=404, detail=f"Task {task_id} metadata could not be loaded")
        else:
            # Check if we have results files even without metadata
            doc_map_path = os.path.join(task_dir, "doc_map.json")
            crawl_result_path = os.path.join(task_dir, "crawl_result.json")
            
            if os.path.exists(doc_map_path) or os.path.exists(crawl_result_path):
                # Create minimal task info based on available files
                status = "completed" if os.path.exists(doc_map_path) else "unknown"
                
                # Try to extract URL from doc map if available
                url = "unknown"
                if os.path.exists(doc_map_path):
                    try:
                        with open(doc_map_path, "r") as f:
                            doc_map_data = json.load(f)
                            if "url" in doc_map_data:
                                url = doc_map_data["url"]
                    except:
                        pass
                
                task = {
                    "task_id": task_id,
                    "status": status,
                    "url": url
                }
                
                # Add to in-memory tasks
                crawl_tasks[task_id] = task
            else:
                # No task found in memory or on disk
                raise HTTPException(status_code=404, detail=f"Task {task_id} not found")
    
    # Use Task class method to handle timestamp conversion
    task_obj = Task.from_task_data(task_id, task)
    
    return CrawlStatus(
        task_id=task_id,
        status=task["status"],
        url=task["url"],
        stats=task.get("stats"),
        error=task.get("error"),
        duration=task.get("duration"),
        start_time=task_obj.start_time,
        end_time=task_obj.end_time
    )

@app.get("/api/map/{task_id}")
async def get_doc_map(task_id: str):
    """
    Get the documentation map for a completed crawl task.
    
    Args:
        task_id: ID of the crawl task.
        
    Returns:
        Documentation map.
    """
    if task_id not in crawl_tasks:
        raise HTTPException(status_code=404, detail=f"Task {task_id} not found")
    
    task = crawl_tasks[task_id]
    
    if task["status"] != "completed":
        raise HTTPException(
            status_code=400, 
            detail=f"Task {task_id} is not completed (status: {task['status']})"
        )
    
    # Load doc map from file
    doc_map_path = os.path.join(results_dir, task_id, "doc_map.json")
    
    if not os.path.exists(doc_map_path):
        raise HTTPException(status_code=404, detail=f"Documentation map not found for task {task_id}")
    
    with open(doc_map_path, "r") as f:
        doc_map_data = json.load(f)
    
    # Transform the backend DocMap format to the frontend's expected format
    frontend_doc_map = transform_doc_map_for_frontend(doc_map_data)
    
    return frontend_doc_map

def transform_doc_map_for_frontend(doc_map_data):
    """
    Transform the backend DocMap format to the frontend's expected format.
    
    Args:
        doc_map_data: DocMap data from the backend.
        
    Returns:
        DocMap data in the format expected by the frontend.
    """
    # Create the root node
    root_node = {
        "id": "root",
        "name": "Documentation",
        "url": doc_map_data.get("url", ""),
        "children": []
    }
    
    # Add sections as children
    for index, section in enumerate(doc_map_data.get("sections", [])):
        section_id = f"section-{index}"
        section_node = {
            "id": section_id,
            "name": section.get("title", "Unnamed Section"),
            "url": section.get("url", ""),
            "children": []
        }
        
        # Add pages for this section
        for page_url in section.get("pages", []):
            # Find the page details
            page_details = None
            for page in doc_map_data.get("pages", []):
                if page.get("url") == page_url:
                    page_details = page
                    break
            
            if page_details:
                page_id = f"page-{len(section_node['children'])}"
                page_node = {
                    "id": page_id,
                    "name": page_details.get("title", "Unnamed Page"),
                    "url": page_url,
                    "children": []
                }
                section_node["children"].append(page_node)
        
        # Add subsections
        for sub_index, subsection in enumerate(section.get("subsections", [])):
            subsection_id = f"{section_id}-sub-{sub_index}"
            subsection_node = {
                "id": subsection_id,
                "name": subsection.get("title", "Unnamed Subsection"),
                "url": subsection.get("url", ""),
                "children": []
            }
            
            # Add pages for this subsection
            for page_url in subsection.get("pages", []):
                # Find the page details
                page_details = None
                for page in doc_map_data.get("pages", []):
                    if page.get("url") == page_url:
                        page_details = page
                        break
                
                if page_details:
                    page_id = f"{subsection_id}-page-{len(subsection_node['children'])}"
                    page_node = {
                        "id": page_id,
                        "name": page_details.get("title", "Unnamed Page"),
                        "url": page_url,
                        "children": []
                    }
                    subsection_node["children"].append(page_node)
            
            section_node["children"].append(subsection_node)
        
        root_node["children"].append(section_node)
    
    # If there are no sections, add pages directly to the root
    if not root_node["children"] and doc_map_data.get("pages"):
        for page_index, page in enumerate(doc_map_data.get("pages", [])):
            page_id = f"page-{page_index}"
            page_node = {
                "id": page_id,
                "name": page.get("title", "Unnamed Page"),
                "url": page.get("url", ""),
                "children": []
            }
            root_node["children"].append(page_node)
    
    return root_node

@app.get("/api/tasks", response_model=List[Task])
async def get_tasks():
    """
    Get all tasks.
    
    Returns:
        List of all tasks.
    """
    # Convert task dict to list
    tasks = []
    for task_id, task_data in crawl_tasks.items():
        try:
            tasks.append(Task.from_task_data(task_id, task_data))
        except Exception as e:
            print(f"Error processing task {task_id}: {e}")
            traceback.print_exc()
    
    # Sort tasks by start_time (most recent first)
    tasks.sort(key=lambda x: x.start_time if x.start_time else "", reverse=True)
    
    return tasks

@app.post("/api/test-task")
async def create_test_task():
    """
    Create a test task for debugging.
    
    Returns:
        Test task ID.
    """
    # Generate task ID
    task_id = str(uuid.uuid4())
    
    # Store a simple test task
    crawl_tasks[task_id] = {
        "url": "https://example.com/test",
        "status": "completed",
        "start_time": time.time() - 10,  # 10 seconds ago
        "end_time": time.time(),
        "duration": 10.0,
        "error": None,
        "stats": {"pages": 1, "links": 5}
    }
    
    return {"task_id": task_id, "status": "completed"} 

@app.post("/api/test-task/{status}")
async def create_test_task_with_status(status: str):
    """
    Create a test task with a specific status for debugging.
    
    Args:
        status: Status for the test task (completed, failed, crawling, queued)
        
    Returns:
        Test task ID.
    """
    # Validate status
    if status not in ["completed", "failed", "crawling", "queued"]:
        raise HTTPException(status_code=400, detail="Invalid status")
    
    # Generate task ID
    task_id = str(uuid.uuid4())
    
    # Store a test task with the specified status
    crawl_tasks[task_id] = {
        "url": f"https://example.com/test/{status}",
        "status": status,
        "start_time": time.time() - 10,  # 10 seconds ago
        "end_time": time.time() if status in ["completed", "failed"] else None,
        "duration": 10.0 if status in ["completed", "failed"] else None,
        "error": "Test error message" if status == "failed" else None,
        "stats": {"pages": 1, "links": 5} if status == "completed" else None
    }
    
    return {"task_id": task_id, "status": status} 

@app.post("/api/tasks", response_model=CrawlStatus)
async def create_task(task: CrawlTask, background_tasks: BackgroundTasks):
    """Create a new crawl task"""
    task_id = task.id if task.id else str(uuid.uuid4())
    
    # Create crawl request
    request = CrawlRequest(
        url=task.url,
        max_depth=task.max_depth,
        max_pages=task.max_pages,
        respect_robots_txt=task.respect_robots_txt,
        user_agent=task.user_agent,
        detect_nav_menu=task.detect_nav_menu
    )
    
    # Create task data
    task_data = {
        "task_id": task_id,
        "url": task.url,
        "status": "pending",
        "start_time": time.time(),
        "request": request.model_dump()
    }
    
    # Store the task in memory
    crawl_tasks[task_id] = task_data
    
    # Save task metadata
    save_task_metadata(task_id)
    
    # Start background task
    background_tasks.add_task(perform_crawl, task_id, request)
    
    # Return status
    return await get_crawl_status(task_id)

@app.get("/api/tasks/{task_id}", response_model=CrawlStatus)
def get_task_status(task_id: str):
    """Get status of a specific task"""
    if task_id not in crawl_tasks:
        raise HTTPException(status_code=404, detail="Task not found")
    
    task_data = crawl_tasks[task_id]
    
    # Use Task class method for consistent timestamp handling
    task_obj = Task.from_task_data(task_id, task_data)
    
    return CrawlStatus(
        task_id=task_id,
        status=task_data.get("status", "unknown"),
        url=task_data.get("url", ""),
        stats=task_data.get("stats"),
        error=task_data.get("error"),
        duration=task_data.get("duration"),
        start_time=task_obj.start_time,
        end_time=task_obj.end_time
    )

@app.get("/api/tasks-simple")
def list_tasks_simple():
    """List all crawl tasks in a simplified format"""
    result = []
    for task_id, task_data in crawl_tasks.items():
        try:
            # Create a simple dictionary with minimal fields
            task_dict = {
                "task_id": task_id,
                "status": task_data.get("status", "unknown"),
                "url": task_data.get("url", "")
            }
            result.append(task_dict)
        except Exception as e:
            print(f"Error processing task {task_id}: {e}")
    
    return result

@app.get("/api/tasks")
def list_tasks():
    """List all crawl tasks"""
    result = []
    for task_id, task_data in crawl_tasks.items():
        try:
            # Use Task class method to handle timestamp conversion
            task = Task.from_task_data(task_id, task_data)
            result.append(task)
        except Exception as e:
            print(f"Error processing task {task_id}: {e}")
            traceback.print_exc()
    
    return result

@app.get("/api/test")
async def test_endpoint():
    """
    Simple test endpoint to verify the API is working.
    
    Returns:
        A simple success message.
    """
    return {"status": "ok", "message": "API is working correctly"}

# Add this explicit server startup code
if __name__ == "__main__":
    import uvicorn
    
    # Check one more time if port 8000 is already in use
    # Sometimes processes can start between initial check and here
    if is_port_in_use(PORT):
        print(f"Port {PORT} is still in use after initial cleanup. Attempting to kill processes again.")
        kill_processes_on_port(PORT, force=True)
        
        # Final check
        if is_port_in_use(PORT):
            print(f"Error: Port {PORT} is still in use after multiple attempts to free it.")
            print("Please free up the port manually and try again.")
            exit(1)
    
    print(f"Starting Docu Eater API server on http://0.0.0.0:{PORT}...")
    
    # Add improved logging
    uvicorn.run(
        app, 
        host="0.0.0.0", 
        port=PORT,
        log_level="info",
        access_log=True
    ) 