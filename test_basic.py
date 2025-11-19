"""Basic tests for the AI Web Reader components."""
import os
import sys
from unittest.mock import Mock, patch


def test_imports():
    """Test that all modules can be imported."""
    print("Testing imports...")

    try:
        import config
        import scraper
        import vector_store
        import qa_engine
        import updater
        import api
        print("✓ All modules imported successfully")
        return True
    except ImportError as e:
        print(f"✗ Import error: {e}")
        return False


def test_scraper():
    """Test web scraper functionality."""
    print("\nTesting scraper...")

    from scraper import WebScraper

    scraper = WebScraper("https://example.com")

    # Test HTML extraction
    html = """
    <html>
        <head><title>Test Page</title></head>
        <body>
            <h1>Main Title</h1>
            <p>This is a test paragraph with enough content to be extracted.</p>
            <p>Another paragraph with sufficient length for testing.</p>
        </body>
    </html>
    """

    chunks = scraper.extract_text_chunks(html, chunk_size=100)

    if chunks and len(chunks) > 0:
        print(f"✓ Extracted {len(chunks)} chunks")
        print(f"  Sample chunk: {chunks[0]['text'][:50]}...")
        return True
    else:
        print("✗ Failed to extract chunks")
        return False


def test_vector_store():
    """Test vector store functionality."""
    print("\nTesting vector store...")

    from vector_store import VectorStore
    import tempfile
    import shutil

    # Create temporary directory
    temp_dir = tempfile.mkdtemp()

    try:
        store = VectorStore(persist_directory=temp_dir)

        # Test adding documents
        chunks = [
            {
                'id': 'test_1',
                'text': 'This is a test document about machine learning and AI.',
                'source': 'https://test.com',
                'title': 'Test Document'
            },
            {
                'id': 'test_2',
                'text': 'Another document discussing natural language processing.',
                'source': 'https://test.com',
                'title': 'Test Document 2'
            }
        ]

        store.add_documents(chunks)
        size = store.get_collection_size()

        if size == 2:
            print(f"✓ Successfully stored {size} documents")

            # Test search
            results = store.search("machine learning", n_results=1)
            if results and len(results) > 0:
                print(f"✓ Search returned {len(results)} results")
                return True
            else:
                print("✗ Search failed")
                return False
        else:
            print(f"✗ Expected 2 documents, got {size}")
            return False

    finally:
        # Cleanup
        shutil.rmtree(temp_dir)


def test_hash_detection():
    """Test content change detection."""
    print("\nTesting content change detection...")

    from scraper import WebScraper

    scraper = WebScraper("https://test.com")

    html1 = "<html><body>Content version 1</body></html>"
    html2 = "<html><body>Content version 2</body></html>"

    # First check - should be true (no previous hash)
    changed1 = scraper.has_content_changed(html1)

    # Same content - should be false
    changed2 = scraper.has_content_changed(html1)

    # Different content - should be true
    changed3 = scraper.has_content_changed(html2)

    if changed1 and not changed2 and changed3:
        print("✓ Content change detection working correctly")
        return True
    else:
        print(f"✗ Change detection failed: {changed1}, {changed2}, {changed3}")
        return False


def run_all_tests():
    """Run all tests."""
    print("=" * 80)
    print("RUNNING BASIC TESTS FOR AI WEB READER")
    print("=" * 80)

    tests = [
        test_imports,
        test_scraper,
        test_hash_detection,
        test_vector_store,
    ]

    results = []

    for test in tests:
        try:
            result = test()
            results.append(result)
        except Exception as e:
            print(f"\n✗ Test failed with exception: {e}")
            results.append(False)

    print("\n" + "=" * 80)
    print(f"RESULTS: {sum(results)}/{len(results)} tests passed")
    print("=" * 80)

    if all(results):
        print("\n✓ All tests passed!")
        return 0
    else:
        print("\n✗ Some tests failed")
        return 1


if __name__ == "__main__":
    # Set environment variables for testing
    os.environ['ANTHROPIC_API_KEY'] = 'test_key'
    os.environ['TARGET_URL'] = 'https://example.com'

    sys.exit(run_all_tests())
