"""
Simple FastAPI server for testing
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="Simple Agentic RAG API")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    return {"message": "🚀 Simple Agentic RAG API is running!", "status": "ok"}

@app.get("/health")
async def health():
    return {
        "status": "healthy",
        "services": {
            "api": True,
            "rag": False,  # Not implemented yet
            "multimodal": False  # Not implemented yet
        }
    }

@app.post("/query")
async def simple_query(request: dict):
    return {
        "answer": f"This is a test response to: {request.get('query', 'unknown query')}",
        "citations": [],
        "confidence_score": 0.8,
        "processing_time_ms": 100
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)