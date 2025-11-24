"""Test script to verify project setup."""

import sys
from pathlib import Path

# Add src to path (now we're in tests/, so go up one level)
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

# Simple ASCII checkmarks for Windows compatibility
OK = "[OK]"
FAIL = "[FAIL]"
WARN = "[WARN]"


def test_imports():
    """Test that all modules can be imported."""
    print("Testing imports...")

    try:
        from story_writer.models import (
            Chapter, ChapterOutline, Character, Arc,
            WorldLocation, Faction, Artifact, PlotThread, StoryMemory
        )
        print(f"{OK} Models imported successfully")
    except Exception as e:
        print(f"{FAIL} Failed to import models: {e}")
        return False

    try:
        from story_writer.utils import (
            get_settings, get_llm_config, get_style_guide, get_world_seed
        )
        print(f"{OK} Utils imported successfully")
    except Exception as e:
        print(f"{FAIL} Failed to import utils: {e}")
        return False

    return True


def test_config():
    """Test configuration loading."""
    print("\nTesting configuration...")

    try:
        from story_writer.utils import get_llm_config, get_style_guide, get_world_seed

        llm_config = get_llm_config()
        print(f"{OK} LLM config loaded - Provider: {llm_config.get('provider')}")

        style_guide = get_style_guide()
        print(f"{OK} Style guide loaded - Themes: {len(style_guide.get('themes', []))}")

        world_seed = get_world_seed()
        print(f"{OK} World seed loaded - World: {world_seed.get('world_name')}")

        return True
    except Exception as e:
        print(f"{FAIL} Failed to load config: {e}")
        return False


def test_models():
    """Test creating model instances."""
    print("\nTesting data models...")

    try:
        from story_writer.models import Character, PlotThread, StoryMemory

        # Test Character
        char = Character(
            character_id="test_char",
            name="Test Character",
            personality="Brave and clever",
            dream="Test the system"
        )
        print(f"{OK} Created Character: {char.name}")

        # Test PlotThread
        thread = PlotThread(
            thread_id="test_thread",
            name="Test Mystery",
            thread_type="mystery",
            setup_chapter="ch_001",
            setup_description="A test mystery appears"
        )
        print(f"{OK} Created PlotThread: {thread.name}")

        # Test StoryMemory
        memory = StoryMemory(
            story_title="Test Story",
            world_name="Test World"
        )
        memory.characters["test_char"] = char
        memory.plot_threads["test_thread"] = thread

        print(f"{OK} Created StoryMemory with {len(memory.characters)} character(s)")

        return True
    except Exception as e:
        print(f"{FAIL} Failed to create models: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_llm_client():
    """Test LLM client creation (without API call)."""
    print("\nTesting LLM client...")

    try:
        from story_writer.utils import create_client

        # This will fail if no API key is set, which is expected
        try:
            client = create_client()
            print(f"{OK} LLM client created - Provider: {client.provider}")
            print(f"{OK} Model: {client.model}")
            print("  (Note: Not testing actual API call)")
            return True
        except ValueError as e:
            if "API_KEY not found" in str(e):
                print(f"{WARN} LLM client creation requires API key (expected)")
                print("  Set ANTHROPIC_API_KEY or OPENAI_API_KEY in .env file")
                return True
            raise

    except Exception as e:
        print(f"{FAIL} Failed to test LLM client: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Run all tests."""
    print("=" * 60)
    print("Story Writer Setup Test")
    print("=" * 60)

    results = []

    results.append(("Imports", test_imports()))
    results.append(("Configuration", test_config()))
    results.append(("Data Models", test_models()))
    results.append(("LLM Client", test_llm_client()))

    print("\n" + "=" * 60)
    print("Test Results:")
    print("=" * 60)

    for name, passed in results:
        status = "[PASS]" if passed else "[FAIL]"
        print(f"{status} - {name}")

    all_passed = all(result[1] for result in results)

    print("=" * 60)
    if all_passed:
        print("[OK] All tests passed! Setup is complete.")
        print("\nNext steps:")
        print("1. Copy .env.template to .env")
        print("2. Add your API key to .env")
        print("3. Install dependencies: pip install -e .")
        print("4. Start building the story system!")
    else:
        print("[FAIL] Some tests failed. Please check the errors above.")

    return 0 if all_passed else 1


if __name__ == "__main__":
    sys.exit(main())
