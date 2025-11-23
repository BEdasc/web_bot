"""FastAPI application for the AI web reader."""
from fastapi import FastAPI, HTTPException
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from typing import Optional, List, Dict
import logging
import json

from config import settings
from scraper import WebScraper
from vector_store import VectorStore
from qa_engine import QAEngine
from updater import ContentUpdater

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="AI Web Reader",
    description="AI application that reads website content and answers questions with anti-hallucination features",
    version="1.0.0"
)

# Global instances (will be initialized on startup)
scraper: Optional[WebScraper] = None
vector_store: Optional[VectorStore] = None
qa_engine: Optional[QAEngine] = None
updater: Optional[ContentUpdater] = None


class QuestionRequest(BaseModel):
    """Request model for asking questions."""
    question: str
    n_sources: int = 5


class QuestionResponse(BaseModel):
    """Response model for answers."""
    answer: str
    sources: List[Dict]
    confidence: str
    question: str


class StatusResponse(BaseModel):
    """Response model for system status."""
    status: str
    target_url: str
    last_update: Optional[str]
    update_count: int
    collection_size: int
    update_frequency_minutes: int


@app.on_event("startup")
async def startup_event():
    """Initialize all components on application startup."""
    global scraper, vector_store, qa_engine, updater

    logger.info("Initializing AI Web Reader...")

    try:
        # Initialize components
        scraper = WebScraper(
            settings.target_url,
            verify_ssl=settings.verify_ssl,
            crawl_mode=settings.crawl_mode,
            max_pages=settings.max_pages,
            max_depth=settings.max_depth,
            crawl_delay=settings.crawl_delay,
            same_domain_only=settings.same_domain_only,
            exclude_patterns=settings.exclude_patterns
        )
        vector_store = VectorStore(settings.chroma_persist_directory)
        qa_engine = QAEngine(settings.anthropic_api_key, vector_store)
        updater = ContentUpdater(scraper, vector_store, settings.update_frequency)

        # Start the auto-updater
        updater.start_scheduler()

        logger.info("AI Web Reader initialized successfully")

    except Exception as e:
        logger.error(f"Failed to initialize application: {e}")
        raise


@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on application shutdown."""
    global updater

    if updater:
        updater.stop_scheduler()
        logger.info("AI Web Reader shutdown complete")


@app.get("/", response_model=dict)
async def root():
    """Root endpoint with API information."""
    return {
        "name": "AI Web Reader",
        "version": "1.0.0",
        "description": "Ask questions about website content with anti-hallucination features",
        "endpoints": {
            "POST /ask": "Ask a question about the website content",
            "POST /ask/stream": "Ask a question with streaming response",
            "GET /status": "Get system status",
            "POST /update": "Force content update",
            "GET /health": "Health check"
        }
    }


@app.post("/ask", response_model=QuestionResponse)
async def ask_question(request: QuestionRequest):
    """Ask a question about the website content.

    Args:
        request: QuestionRequest containing the question

    Returns:
        QuestionResponse with answer, sources, and confidence
    """
    if not qa_engine:
        raise HTTPException(status_code=503, detail="QA engine not initialized")

    if not request.question.strip():
        raise HTTPException(status_code=400, detail="Question cannot be empty")

    try:
        result = qa_engine.answer_question(
            request.question,
            n_sources=request.n_sources
        )
        return QuestionResponse(**result)

    except Exception as e:
        logger.error(f"Error answering question: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/ask/stream")
async def ask_question_stream(request: QuestionRequest):
    """Ask a question with streaming response.

    Args:
        request: QuestionRequest containing the question

    Returns:
        StreamingResponse with answer chunks
    """
    if not qa_engine:
        raise HTTPException(status_code=503, detail="QA engine not initialized")

    if not request.question.strip():
        raise HTTPException(status_code=400, detail="Question cannot be empty")

    async def generate():
        try:
            for chunk in qa_engine.answer_with_streaming(
                request.question,
                n_sources=request.n_sources
            ):
                yield json.dumps(chunk) + "\n"
        except Exception as e:
            logger.error(f"Error in streaming response: {e}")
            yield json.dumps({"type": "error", "content": str(e)}) + "\n"

    return StreamingResponse(generate(), media_type="application/x-ndjson")


@app.get("/status", response_model=StatusResponse)
async def get_status():
    """Get the current system status.

    Returns:
        StatusResponse with system information
    """
    if not updater:
        raise HTTPException(status_code=503, detail="System not initialized")

    try:
        update_status = updater.get_update_status()

        return StatusResponse(
            status="running" if update_status['scheduler_running'] else "stopped",
            target_url=settings.target_url,
            last_update=update_status['last_update'],
            update_count=update_status['update_count'],
            collection_size=update_status['collection_size'],
            update_frequency_minutes=update_status['update_frequency_minutes']
        )

    except Exception as e:
        logger.error(f"Error getting status: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/update")
async def force_update():
    """Force an immediate content update.

    Returns:
        Dictionary with update status
    """
    if not updater:
        raise HTTPException(status_code=503, detail="Updater not initialized")

    try:
        updater.force_update()
        return {"status": "success", "message": "Content update triggered"}

    except Exception as e:
        logger.error(f"Error forcing update: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/health")
async def health_check():
    """Health check endpoint.

    Returns:
        Dictionary with health status
    """
    health_status = {
        "status": "healthy",
        "components": {
            "scraper": scraper is not None,
            "vector_store": vector_store is not None,
            "qa_engine": qa_engine is not None,
            "updater": updater is not None
        }
    }

    all_healthy = all(health_status["components"].values())
    if not all_healthy:
        health_status["status"] = "unhealthy"
        raise HTTPException(status_code=503, detail=health_status)

    return health_status
