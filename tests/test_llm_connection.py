"""Test LLM connection with actual API call."""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))


def test_llm_connection():
    """Test actual LLM API connection."""
    print("Testing LLM connection...")
    print("=" * 60)

    try:
        from story_writer.utils import create_client

        # Create client
        print("Creating LLM client...")
        client = create_client()
        print(f"[OK] Using provider: {client.provider}")
        print(f"[OK] Using model: {client.model}")
        print()

        # Test simple generation
        print("Testing API call with simple prompt...")
        response = client.generate(
            prompt="Write a single sentence describing a brave sky pirate.",
            temperature=0.7,
            max_tokens=100
        )

        print("[OK] API call successful!")
        print()
        print("Response:")
        print("-" * 60)
        print(response)
        print("-" * 60)
        print()
        print("[PASS] LLM connection test PASSED")
        return True

    except ValueError as e:
        if "API_KEY not found" in str(e):
            print("[ERROR] API key not set!")
            print()
            print("Please:")
            print("1. Copy .env.template to .env")
            print("2. Add your ANTHROPIC_API_KEY or OPENAI_API_KEY")
            print("3. Run this test again")
            return False
        raise

    except Exception as e:
        print(f"[ERROR] Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = test_llm_connection()
    sys.exit(0 if success else 1)
