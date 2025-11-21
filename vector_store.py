"""Vector database module for storing and retrieving website content."""
import chromadb
from typing import List, Dict, Optional
import logging
import os

logger = logging.getLogger(__name__)


class VectorStore:
    """Manages the vector database for semantic search over website content."""

    def __init__(self, persist_directory: str = "./chroma_db"):
        """Initialize the vector store.

        Args:
            persist_directory: Directory to persist the ChromaDB database
        """
        self.persist_directory = persist_directory

        # Create directory if it doesn't exist
        os.makedirs(persist_directory, exist_ok=True)

        # Use PersistentClient for ChromaDB 0.5.x
        self.client = chromadb.PersistentClient(
            path=persist_directory
        )
        self.collection_name = "website_content"
        self.collection = None
        self._initialize_collection()

    def _initialize_collection(self):
        """Initialize or get the collection for website content."""
        try:
            self.collection = self.client.get_collection(name=self.collection_name)
            logger.info(f"Loaded existing collection: {self.collection_name}")
        except Exception:
            self.collection = self.client.create_collection(
                name=self.collection_name,
                metadata={"description": "Website content for Q&A"}
            )
            logger.info(f"Created new collection: {self.collection_name}")

    def add_documents(self, chunks: List[Dict[str, str]]):
        """Add document chunks to the vector store.

        Args:
            chunks: List of dictionaries containing text chunks and metadata
        """
        if not chunks:
            logger.warning("No chunks to add to vector store")
            return

        documents = [chunk['text'] for chunk in chunks]
        metadatas = [
            {
                'source': chunk['source'],
                'title': chunk['title'],
                'chunk_id': chunk['id']
            }
            for chunk in chunks
        ]
        ids = [chunk['id'] for chunk in chunks]

        try:
            self.collection.add(
                documents=documents,
                metadatas=metadatas,
                ids=ids
            )
            logger.info(f"Added {len(chunks)} documents to vector store")
        except Exception as e:
            logger.error(f"Failed to add documents to vector store: {e}")

    def search(self, query: str, n_results: int = 5) -> List[Dict[str, any]]:
        """Search for relevant content based on a query.

        Args:
            query: The search query
            n_results: Number of results to return

        Returns:
            List of relevant documents with metadata and similarity scores
        """
        try:
            results = self.collection.query(
                query_texts=[query],
                n_results=n_results
            )

            # Format results
            formatted_results = []
            if results['documents'] and results['documents'][0]:
                for i, doc in enumerate(results['documents'][0]):
                    formatted_results.append({
                        'text': doc,
                        'metadata': results['metadatas'][0][i] if results['metadatas'] else {},
                        'distance': results['distances'][0][i] if results['distances'] else None
                    })

            logger.info(f"Found {len(formatted_results)} results for query: {query[:50]}...")
            return formatted_results

        except Exception as e:
            logger.error(f"Search failed: {e}")
            return []

    def clear_collection(self):
        """Clear all documents from the collection."""
        try:
            self.client.delete_collection(name=self.collection_name)
            self._initialize_collection()
            logger.info("Cleared vector store collection")
        except Exception as e:
            logger.error(f"Failed to clear collection: {e}")

    def update_content(self, chunks: List[Dict[str, str]]):
        """Update the vector store with new content.

        Args:
            chunks: List of dictionaries containing text chunks and metadata
        """
        logger.info("Updating vector store with new content")
        self.clear_collection()
        self.add_documents(chunks)

    def get_collection_size(self) -> int:
        """Get the number of documents in the collection.

        Returns:
            Number of documents in the collection
        """
        try:
            return self.collection.count()
        except Exception:
            return 0
