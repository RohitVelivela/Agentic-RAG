"""
Agentic RAG System - Main FastAPI Application
"""

from fastapi import FastAPI, HTTPException, WebSocket, WebSocketDisconnect, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager
import uvicorn
import logging
from typing import List, Dict, Any, Optional
import asyncio
import json

from app.config import settings
# from app.services.stt_service import STTService  # Temporarily disabled
from app.services.rag_service import RAGService
# from app.services.web_search_service import WebSearchService  # Temporarily disabled
# from app.services.google_drive_service import GoogleDriveService  # Temporarily disabled
from app.services.document_processor import DocumentProcessor
# from app.services.multimodal_service import MultiModalService  # Temporarily disabled
from app.models.schemas import (
    QueryRequest, 
    QueryResponse, 
    Citation,
    SearchResult
)
from app.websocket.connection_manager import ConnectionManager

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Global services
stt_service = None  # Optional[STTService] = None  # Temporarily disabled
rag_service: Optional[RAGService] = None
web_search_service = None  # Optional[WebSearchService] = None  # Temporarily disabled
google_drive_service = None  # Optional[GoogleDriveService] = None  # Temporarily disabled
document_processor: Optional[DocumentProcessor] = None
multimodal_service = None  # Optional[MultiModalService] = None  # Temporarily disabled
connection_manager = ConnectionManager()

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Initialize services on startup and cleanup on shutdown"""
    global stt_service, rag_service, web_search_service, google_drive_service, document_processor, multimodal_service
    
    logger.info("Starting Agentic RAG System...")
    
    # Initialize services
    try:
        # stt_service = STTService()  # Temporarily disabled
        rag_service = RAGService()
        # web_search_service = WebSearchService()  # Temporarily disabled
        # google_drive_service = GoogleDriveService()  # Temporarily disabled
        document_processor = DocumentProcessor()
        # multimodal_service = MultiModalService()  # Temporarily disabled

        await rag_service.initialize()
        # await google_drive_service.initialize()  # Temporarily disabled
        
        logger.info("All services initialized successfully")
    except Exception as e:
        logger.error(f"Failed to initialize services: {e}")
        raise
    
    yield
    
    # Cleanup
    logger.info("Shutting down services...")
    if rag_service:
        await rag_service.cleanup()

# Create FastAPI app
app = FastAPI(
    title="Agentic RAG System",
    description="A comprehensive RAG system with voice input, multimodal document processing, and intelligent search",
    version="1.0.0",
    lifespan=lifespan
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    """Health check endpoint"""
    return {"message": "Agentic RAG System is running", "version": "1.0.0"}

@app.get("/health")
async def health_check():
    """Detailed health check for all services"""
    status = {
        "status": "healthy",
        "services": {
            "stt": stt_service is not None,
            "rag": rag_service is not None and await rag_service.is_healthy(),
            "web_search": web_search_service is not None,
            "google_drive": google_drive_service is not None,
            "document_processor": document_processor is not None
        }
    }
    return status

@app.post("/upload")
async def upload_document(file: UploadFile = File(...)):
    """Upload and process a document (PDF with images/graphs)"""
    if not document_processor:
        raise HTTPException(status_code=503, detail="Document processor not initialized")
    
    try:
        # Process the uploaded document
        result = await document_processor.process_document(file)

        # Process with multi-modal service for enhanced analysis
        if multimodal_service and result.images:
            multimodal_results = await multimodal_service.process_uploaded_images_for_multimodal(
                images=result.images,
                text_chunks=result.text_chunks
            )
            result.metadata["multimodal_analysis"] = multimodal_results

        # Index the processed content in RAG system
        await rag_service.index_document(result)
        
        return {
            "success": True,
            "document_id": result.document_id,
            "filename": result.filename,
            "pages_processed": result.pages_processed,
            "images_extracted": len(result.images),
            "text_chunks": len(result.text_chunks),
            "processing_time_ms": result.processing_time_ms,
            "message": "Document processed and indexed successfully",
            "metadata": result.metadata
        }
    except Exception as e:
        logger.error(f"Document upload failed: {e}")
        raise HTTPException(status_code=500, detail=f"Document processing failed: {str(e)}")

@app.post("/query", response_model=QueryResponse)
async def query_system(request: QueryRequest):
    """Process a text query using RAG + Web Search + Google Drive"""
    if not rag_service:
        raise HTTPException(status_code=503, detail="RAG service not initialized")
    
    try:
        # Run searches (only RAG for now)
        rag_results = await rag_service.search(request.query, request.num_results)
        web_results = []  # Temporarily disabled
        drive_results = []  # Temporarily disabled

        # Handle any exceptions
        if isinstance(rag_results, Exception):
            logger.error(f"RAG search failed: {rag_results}")
            rag_results = []
        
        # Generate response using RAG
        response = await rag_service.generate_response(
            query=request.query,
            rag_results=rag_results,
            web_results=web_results,
            drive_results=drive_results
        )
        
        return response
    except Exception as e:
        logger.error(f"Query processing failed: {e}")
        raise HTTPException(status_code=500, detail=f"Query processing failed: {str(e)}")

@app.websocket("/ws/stt")
async def websocket_stt(websocket: WebSocket):
    """WebSocket endpoint for streaming speech-to-text"""
    await connection_manager.connect(websocket)
    
    if not stt_service:
        await websocket.close(code=1011, reason="STT service not available")
        return
    
    try:
        while True:
            # Receive audio data
            data = await websocket.receive_bytes()
            
            # Process with STT
            result = await stt_service.transcribe_stream(data)
            
            # Send transcription back
            await websocket.send_json({
                "type": "transcription",
                "text": result.text,
                "confidence": result.confidence,
                "is_partial": result.is_partial
            })
            
    except WebSocketDisconnect:
        connection_manager.disconnect(websocket)
    except Exception as e:
        logger.error(f"STT WebSocket error: {e}")
        await websocket.close(code=1011, reason=str(e))

@app.websocket("/ws/chat")
async def websocket_chat(websocket: WebSocket):
    """WebSocket endpoint for real-time chat with the system"""
    await connection_manager.connect(websocket)
    
    try:
        while True:
            # Receive message
            message = await websocket.receive_json()
            
            if message["type"] == "query":
                # Process query
                request = QueryRequest(**message["data"])
                response = await query_system(request)
                
                # Send response
                await websocket.send_json({
                    "type": "response",
                    "data": response.dict()
                })
            
    except WebSocketDisconnect:
        connection_manager.disconnect(websocket)
    except Exception as e:
        logger.error(f"Chat WebSocket error: {e}")
        await websocket.close(code=1011, reason=str(e))

@app.get("/citation/{citation_id}")
async def get_citation_content(citation_id: str):
    """Get detailed content for a specific citation"""
    if not rag_service:
        raise HTTPException(status_code=503, detail="RAG service not initialized")
    
    try:
        citation_content = await rag_service.get_citation_content(citation_id)
        return citation_content
    except Exception as e:
        logger.error(f"Citation retrieval failed: {e}")
        raise HTTPException(status_code=404, detail="Citation not found")

@app.get("/documents")
async def list_documents():
    """List all uploaded and indexed documents"""
    if not rag_service:
        raise HTTPException(status_code=503, detail="RAG service not initialized")
    
    try:
        documents = await rag_service.list_documents()
        return {"documents": documents}
    except Exception as e:
        logger.error(f"Document listing failed: {e}")
        raise HTTPException(status_code=500, detail="Failed to list documents")

@app.delete("/documents/{document_id}")
async def delete_document(document_id: str):
    """Delete a document from the system"""
    if not rag_service:
        raise HTTPException(status_code=503, detail="RAG service not initialized")
    
    try:
        await rag_service.delete_document(document_id)
        return {"message": "Document deleted successfully"}
    except Exception as e:
        logger.error(f"Document deletion failed: {e}")
        raise HTTPException(status_code=500, detail="Failed to delete document")

@app.post("/multimodal/query", response_model=QueryResponse)
async def multimodal_query(request: QueryRequest):
    """Enhanced multi-modal query with visual-text reasoning"""
    if not all([rag_service, multimodal_service]):
        raise HTTPException(status_code=503, detail="Required services not initialized")

    try:
        # Run searches (only RAG for now)
        rag_results = await rag_service.search(request.query, request.num_results)
        web_results = []  # Temporarily disabled
        drive_results = []  # Temporarily disabled

        # Handle any exceptions
        if isinstance(rag_results, Exception):
            logger.error(f"RAG search failed: {rag_results}")
            rag_results = []

        # Get document images for multi-modal enhancement
        # In a real implementation, you'd retrieve images associated with the search results
        image_results = []  # Would be populated from document database

        # Enhance with multi-modal search
        enhanced_results = await multimodal_service.multi_modal_search(
            query=request.query,
            text_results=rag_results,
            image_results=image_results
        )

        # Generate response using enhanced results
        response = await rag_service.generate_response(
            query=request.query,
            rag_results=enhanced_results[:request.num_results],
            web_results=web_results,
            drive_results=drive_results
        )

        # Add multi-modal metadata
        response.metadata["multimodal_enhancement"] = True
        response.metadata["visual_context_added"] = len(image_results)

        return response

    except Exception as e:
        logger.error(f"Multi-modal query processing failed: {e}")
        raise HTTPException(status_code=500, detail=f"Multi-modal query failed: {str(e)}")

@app.post("/analyze/chart")
async def analyze_chart(file: UploadFile = File(...)):
    """Analyze a chart/graph image and extract insights"""
    if not multimodal_service:
        raise HTTPException(status_code=503, detail="Multi-modal service not initialized")

    try:
        # Read and validate image
        content = await file.read()
        from PIL import Image
        import io

        image = Image.open(io.BytesIO(content))

        # Analyze chart
        analysis = await multimodal_service.analyze_chart_to_text(image)

        return {
            "success": True,
            "chart_type": analysis.chart_type,
            "text_description": analysis.text_content,
            "data_insights": analysis.data_insights,
            "queryable_facts": analysis.queryable_facts,
            "confidence": analysis.confidence
        }

    except Exception as e:
        logger.error(f"Chart analysis failed: {e}")
        raise HTTPException(status_code=500, detail=f"Chart analysis failed: {str(e)}")

@app.post("/analyze/image")
async def analyze_image_content(file: UploadFile = File(...)):
    """Generate smart captions and analysis for technical images"""
    if not multimodal_service:
        raise HTTPException(status_code=503, detail="Multi-modal service not initialized")

    try:
        # Read and validate image
        content = await file.read()
        from PIL import Image
        import io

        image = Image.open(io.BytesIO(content))

        # Generate enhanced captions
        captions = await multimodal_service.generate_smart_image_captions(
            image=image,
            context="User uploaded image for analysis"
        )

        return {
            "success": True,
            "captions": captions,
            "filename": file.filename
        }

    except Exception as e:
        logger.error(f"Image analysis failed: {e}")
        raise HTTPException(status_code=500, detail=f"Image analysis failed: {str(e)}")

@app.get("/multimodal/visual-links/{document_id}")
async def get_visual_text_links(document_id: str):
    """Get visual-text cross-references for a document"""
    if not multimodal_service:
        raise HTTPException(status_code=503, detail="Multi-modal service not initialized")

    try:
        # In a real implementation, retrieve visual links from database
        links = multimodal_service.visual_text_links

        document_links = [
            {
                "visual_id": link.visual_id,
                "relationship": link.relationship,
                "confidence": link.confidence,
                "text_snippets": link.text_chunks[:3]  # First 3 snippets
            }
            for link in links.values()
            if document_id in link.visual_id
        ]

        return {
            "document_id": document_id,
            "visual_text_links": document_links,
            "total_links": len(document_links)
        }

    except Exception as e:
        logger.error(f"Visual link retrieval failed: {e}")
        raise HTTPException(status_code=500, detail="Failed to retrieve visual links")

@app.get("/multimodal/charts")
async def list_chart_analyses():
    """List all cached chart analyses"""
    if not multimodal_service:
        raise HTTPException(status_code=503, detail="Multi-modal service not initialized")

    try:
        charts = []
        for chart_id, analysis in multimodal_service.chart_cache.items():
            charts.append({
                "id": chart_id,
                "type": analysis.chart_type,
                "confidence": analysis.confidence,
                "facts_count": len(analysis.queryable_facts),
                "description_preview": analysis.text_content[:200] + "..."
            })

        return {
            "charts": charts,
            "total_count": len(charts)
        }

    except Exception as e:
        logger.error(f"Chart listing failed: {e}")
        raise HTTPException(status_code=500, detail="Failed to list charts")

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    ) 