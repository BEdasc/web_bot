#!/usr/bin/env python3
"""Quick test to verify Anthropic client initialization."""
import sys
import os

try:
    print("🔍 Testing Anthropic client initialization...")

    import anthropic
    print(f"✓ Anthropic version: {anthropic.__version__}")

    # Test client initialization with a dummy API key
    print("\n✓ Testing client initialization...")
    client = anthropic.Anthropic(api_key="test_key_dummy")
    print("  ✅ Client initialized successfully!")
    print(f"  Client type: {type(client)}")

    # Check what parameters are accepted
    import inspect
    sig = inspect.signature(anthropic.Anthropic.__init__)
    print(f"\n✓ Accepted parameters for Anthropic():")
    for param_name, param in sig.parameters.items():
        if param_name != 'self':
            print(f"  - {param_name}")

    print("\n✅ All tests passed! Anthropic client is working correctly.")

except Exception as e:
    print(f"\n❌ Error: {e}")
    print(f"\nError type: {type(e).__name__}")
    import traceback
    print("\nFull traceback:")
    traceback.print_exc()
    sys.exit(1)
