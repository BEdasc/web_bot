"""Main entry point for the AI Web Reader application."""
import uvicorn
import logging
from config import settings

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)


def main():
    """Run the FastAPI application."""
    logger.info("Starting AI Web Reader application...")
    logger.info(f"Target URL: {settings.target_url}")
    logger.info(f"Update frequency: {settings.update_frequency} minutes")
    logger.info(f"API will be available at http://{settings.api_host}:{settings.api_port}")

    uvicorn.run(
        "api:app",
        host=settings.api_host,
        port=settings.api_port,
        reload=False,
        log_level="info"
    )


if __name__ == "__main__":
    main()
