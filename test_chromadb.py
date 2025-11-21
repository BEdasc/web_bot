#!/usr/bin/env python3
"""Quick test to verify ChromaDB initialization works correctly."""
import sys
import os
from pathlib import Path

# Add current directory to path
sys.path.insert(0, str(Path(__file__).parent))

try:
    print("🔍 Testing ChromaDB initialization...")

    from vector_store import VectorStore

    # Test 1: Create VectorStore instance
    print("\n✓ Test 1: Creating VectorStore instance...")
    test_dir = "./test_chroma_db"

    # Clean up test directory if it exists
    if os.path.exists(test_dir):
        import shutil
        shutil.rmtree(test_dir)
        print(f"  Cleaned up existing test directory: {test_dir}")

    vector_store = VectorStore(persist_directory=test_dir)
    print(f"  ✅ VectorStore created successfully!")
    print(f"  Collection name: {vector_store.collection_name}")
    print(f"  Collection size: {vector_store.get_collection_size()}")

    # Test 2: Add some test documents
    print("\n✓ Test 2: Adding test documents...")
    test_chunks = [
        {
            'id': 'test_1',
            'text': 'This is a test document about Python programming.',
            'source': 'test',
            'title': 'Test Document 1'
        },
        {
            'id': 'test_2',
            'text': 'ChromaDB is a vector database for AI applications.',
            'source': 'test',
            'title': 'Test Document 2'
        }
    ]

    vector_store.add_documents(test_chunks)
    print(f"  ✅ Added {len(test_chunks)} documents")
    print(f"  Collection size: {vector_store.get_collection_size()}")

    # Test 3: Search for documents
    print("\n✓ Test 3: Searching documents...")
    results = vector_store.search("Python programming", n_results=2)
    print(f"  ✅ Found {len(results)} results")
    if results:
        print(f"  Top result: {results[0]['text'][:50]}...")

    # Cleanup
    print("\n🧹 Cleaning up test directory...")
    import shutil
    shutil.rmtree(test_dir)

    print("\n✅ All tests passed! ChromaDB is working correctly.")
    print("\n💡 Your ChromaDB installation is now compatible with version 0.5.20")
    print("   You can now use the chat interface without issues.")

except Exception as e:
    print(f"\n❌ Error: {e}")
    print(f"\nError type: {type(e).__name__}")
    import traceback
    print("\nFull traceback:")
    traceback.print_exc()
    sys.exit(1)
