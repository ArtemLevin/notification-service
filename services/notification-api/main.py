from fastapi import FastAPI

app = FastAPI(title="Notification API", version="0.1.0")

@app.get("/")
async def root():
    return {"message": "Notification API"}

@app.get("/health")
async def health_check():
    return {"status": "ok"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)