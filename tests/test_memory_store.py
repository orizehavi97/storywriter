"""Test JSON memory store."""

import sys
from pathlib import Path
import shutil

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))


def test_memory_store():
    """Test memory store save/load operations."""
    print("Testing JSON Memory Store")
    print("=" * 60)

    from story_writer.memory import JSONMemoryStore
    from story_writer.models import StoryMemory, Character, PlotThread

    # Use a test directory
    test_dir = Path("data/memory_test")
    if test_dir.exists():
        shutil.rmtree(test_dir)

    try:
        # Initialize store
        print("\n1. Initializing memory store...")
        store = JSONMemoryStore(data_dir=test_dir)
        print(f"[OK] Store initialized at {test_dir}")

        # Create new story
        print("\n2. Creating new story...")
        memory = store.initialize_new_story(
            story_title="Test Adventure",
            world_name="Test World",
            saga_goal="Test the memory system"
        )

        # Add a character
        print("\n3. Adding test character...")
        char = Character(
            character_id="char_test",
            name="Test Hero",
            personality="Brave and clever",
            dream="Pass all tests"
        )
        memory.characters[char.character_id] = char
        print(f"[OK] Added character: {char.name}")

        # Add a plot thread
        print("\n4. Adding test plot thread...")
        thread = PlotThread(
            thread_id="thread_test",
            name="Can we save and load?",
            thread_type="mystery",
            setup_chapter="ch_001",
            setup_description="Testing memory persistence"
        )
        memory.plot_threads[thread.thread_id] = thread
        print(f"[OK] Added plot thread: {thread.name}")

        # Save memory
        print("\n5. Saving memory...")
        store.save(memory, backup=False)

        # Load memory
        print("\n6. Loading memory...")
        loaded_memory = store.load()

        # Verify data
        print("\n7. Verifying loaded data...")
        assert loaded_memory is not None, "Memory should not be None"
        assert loaded_memory.story_title == "Test Adventure", "Title mismatch"
        assert loaded_memory.world_name == "Test World", "World name mismatch"
        assert len(loaded_memory.characters) == 1, "Character count mismatch"
        assert len(loaded_memory.plot_threads) == 1, "Thread count mismatch"

        loaded_char = loaded_memory.characters["char_test"]
        assert loaded_char.name == "Test Hero", "Character name mismatch"

        loaded_thread = loaded_memory.plot_threads["thread_test"]
        assert loaded_thread.name == "Can we save and load?", "Thread name mismatch"

        print("[OK] All data verified correctly!")

        # Test backup
        print("\n8. Testing backup...")
        store.save(memory, backup=True)
        backups = store.list_backups()
        print(f"[OK] Created {len(backups)} backup(s)")

        print("\n" + "=" * 60)
        print("[PASS] Memory store test completed successfully!")
        print("=" * 60)

        return True

    except Exception as e:
        print(f"\n[FAIL] Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

    finally:
        # Cleanup
        if test_dir.exists():
            shutil.rmtree(test_dir)
            print(f"\n[OK] Cleaned up test directory")


if __name__ == "__main__":
    success = test_memory_store()
    sys.exit(0 if success else 1)
