from fastapi import FastAPI
import uvicorn

app = FastAPI()

@app.get("/")
async def root():
    return {"message": "Docu Eater Test Server is running!"}

@app.get("/test")
async def test():
    return {"status": "ok", "message": "Test endpoint is working!"}

if __name__ == "__main__":
    print("Starting test server on http://0.0.0.0:8000...")
    uvicorn.run(app, host="0.0.0.0", port=8000) 