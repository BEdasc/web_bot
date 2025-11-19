"""Auto-update module for refreshing website content."""
from apscheduler.schedulers.background import BackgroundScheduler
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


class ContentUpdater:
    """Manages automatic updates of website content."""

    def __init__(self, scraper, vector_store, update_frequency: int = 60):
        """Initialize the content updater.

        Args:
            scraper: WebScraper instance
            vector_store: VectorStore instance
            update_frequency: Update frequency in minutes
        """
        self.scraper = scraper
        self.vector_store = vector_store
        self.update_frequency = update_frequency
        self.scheduler = BackgroundScheduler()
        self.last_update: datetime = None
        self.update_count: int = 0

    def update_content(self):
        """Fetch and update website content."""
        logger.info(f"Starting content update at {datetime.now()}")

        try:
            # Scrape the website
            chunks = self.scraper.scrape()

            if chunks is None:
                logger.error("Failed to scrape content")
                return

            if not chunks:
                logger.info("No changes detected in website content")
                return

            # Update vector store
            self.vector_store.update_content(chunks)

            # Update metadata
            self.last_update = datetime.now()
            self.update_count += 1

            logger.info(
                f"Content update completed successfully. "
                f"Total chunks: {len(chunks)}, "
                f"Update count: {self.update_count}"
            )

        except Exception as e:
            logger.error(f"Error during content update: {e}")

    def start_scheduler(self):
        """Start the automatic update scheduler."""
        # Perform initial update
        logger.info("Performing initial content update...")
        self.update_content()

        # Schedule periodic updates
        self.scheduler.add_job(
            self.update_content,
            'interval',
            minutes=self.update_frequency,
            id='content_update_job'
        )

        self.scheduler.start()
        logger.info(
            f"Content updater started. "
            f"Updates will occur every {self.update_frequency} minutes."
        )

    def stop_scheduler(self):
        """Stop the automatic update scheduler."""
        if self.scheduler.running:
            self.scheduler.shutdown()
            logger.info("Content updater stopped")

    def force_update(self):
        """Force an immediate content update."""
        logger.info("Forcing immediate content update")
        self.update_content()

    def get_update_status(self) -> dict:
        """Get the current update status.

        Returns:
            Dictionary containing update status information
        """
        return {
            'last_update': self.last_update.isoformat() if self.last_update else None,
            'update_count': self.update_count,
            'update_frequency_minutes': self.update_frequency,
            'scheduler_running': self.scheduler.running,
            'collection_size': self.vector_store.get_collection_size()
        }
