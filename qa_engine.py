"""Question-answering engine with anti-hallucination features."""
import anthropic
from typing import List, Dict, Optional
import logging

logger = logging.getLogger(__name__)


class QAEngine:
    """Question-answering engine that uses RAG to prevent hallucinations."""

    def __init__(self, api_key: str, vector_store):
        """Initialize the QA engine.

        Args:
            api_key: Anthropic API key
            vector_store: VectorStore instance for retrieving relevant content
        """
        self.client = anthropic.Anthropic(api_key=api_key)
        self.vector_store = vector_store
        self.model = "claude-3-5-sonnet-20241022"

    def _create_context_from_sources(self, sources: List[Dict[str, any]]) -> str:
        """Create a context string from retrieved sources.

        Args:
            sources: List of retrieved documents

        Returns:
            Formatted context string
        """
        if not sources:
            return "No relevant information found."

        context_parts = []
        for i, source in enumerate(sources, 1):
            context_parts.append(
                f"[Source {i}]\n"
                f"Title: {source['metadata'].get('title', 'Unknown')}\n"
                f"URL: {source['metadata'].get('source', 'Unknown')}\n"
                f"Content: {source['text']}\n"
            )

        return "\n".join(context_parts)

    def _build_prompt(self, question: str, context: str) -> str:
        """Build the prompt for Claude with anti-hallucination instructions.

        Args:
            question: User's question
            context: Retrieved context from the website

        Returns:
            Formatted prompt
        """
        return f"""You are an AI assistant that answers questions based ONLY on the provided website content. Your role is to be accurate and truthful.

CRITICAL ANTI-HALLUCINATION RULES:
1. ONLY use information from the provided sources below
2. If the answer is not in the sources, say "I don't have enough information to answer this question based on the website content."
3. ALWAYS cite which source number you're using (e.g., "According to Source 1...")
4. Do NOT add information from your general knowledge
5. Do NOT make assumptions or inferences beyond what's explicitly stated
6. If you're uncertain, express that uncertainty
7. Quote directly from sources when possible

WEBSITE CONTENT:
{context}

USER QUESTION: {question}

Please provide an answer based ONLY on the sources above. Include citations to source numbers."""

    def answer_question(
        self,
        question: str,
        n_sources: int = 5,
        max_tokens: int = 1024
    ) -> Dict[str, any]:
        """Answer a question using RAG with anti-hallucination measures.

        Args:
            question: The user's question
            n_sources: Number of relevant sources to retrieve
            max_tokens: Maximum tokens for the response

        Returns:
            Dictionary containing the answer, sources, and metadata
        """
        # Retrieve relevant sources
        sources = self.vector_store.search(question, n_results=n_sources)

        if not sources:
            return {
                'answer': "I don't have any information to answer this question. The website content may not have been loaded yet.",
                'sources': [],
                'confidence': 'none'
            }

        # Create context from sources
        context = self._create_context_from_sources(sources)

        # Build prompt with anti-hallucination instructions
        prompt = self._build_prompt(question, context)

        try:
            # Call Claude API
            message = self.client.messages.create(
                model=self.model,
                max_tokens=max_tokens,
                messages=[
                    {"role": "user", "content": prompt}
                ]
            )

            answer = message.content[0].text

            # Determine confidence based on sources and answer
            confidence = self._assess_confidence(answer, sources)

            return {
                'answer': answer,
                'sources': [
                    {
                        'text': s['text'][:200] + "..." if len(s['text']) > 200 else s['text'],
                        'url': s['metadata'].get('source', 'Unknown'),
                        'title': s['metadata'].get('title', 'Unknown'),
                        'relevance_score': 1 - s['distance'] if s['distance'] is not None else None
                    }
                    for s in sources
                ],
                'confidence': confidence,
                'question': question
            }

        except Exception as e:
            logger.error(f"Error generating answer: {e}")
            return {
                'answer': f"An error occurred while generating the answer: {str(e)}",
                'sources': [],
                'confidence': 'error'
            }

    def _assess_confidence(self, answer: str, sources: List[Dict]) -> str:
        """Assess confidence level of the answer.

        Args:
            answer: Generated answer
            sources: Retrieved sources

        Returns:
            Confidence level: 'high', 'medium', 'low', or 'none'
        """
        # If answer indicates lack of information
        if "don't have enough information" in answer.lower() or "cannot answer" in answer.lower():
            return 'none'

        # If multiple sources with good relevance
        if len(sources) >= 3:
            avg_distance = sum(s.get('distance', 1) for s in sources) / len(sources)
            if avg_distance < 0.5:
                return 'high'
            elif avg_distance < 0.7:
                return 'medium'

        # If few sources or poor relevance
        if len(sources) < 2:
            return 'low'

        return 'medium'

    def answer_with_streaming(self, question: str, n_sources: int = 5):
        """Answer a question with streaming response.

        Args:
            question: The user's question
            n_sources: Number of relevant sources to retrieve

        Yields:
            Chunks of the answer as they're generated
        """
        sources = self.vector_store.search(question, n_results=n_sources)

        if not sources:
            yield {
                'type': 'answer',
                'content': "I don't have any information to answer this question."
            }
            return

        context = self._create_context_from_sources(sources)
        prompt = self._build_prompt(question, context)

        try:
            # First yield the sources
            yield {
                'type': 'sources',
                'content': [
                    {
                        'text': s['text'][:200] + "..." if len(s['text']) > 200 else s['text'],
                        'url': s['metadata'].get('source', 'Unknown'),
                        'title': s['metadata'].get('title', 'Unknown')
                    }
                    for s in sources
                ]
            }

            # Then stream the answer
            with self.client.messages.stream(
                model=self.model,
                max_tokens=1024,
                messages=[{"role": "user", "content": prompt}]
            ) as stream:
                for text in stream.text_stream:
                    yield {
                        'type': 'answer_chunk',
                        'content': text
                    }

        except Exception as e:
            logger.error(f"Error in streaming answer: {e}")
            yield {
                'type': 'error',
                'content': str(e)
            }
