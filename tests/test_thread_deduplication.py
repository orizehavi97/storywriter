"""
Test thread deduplication in Phase 4.
"""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from story_writer.updater import StateUpdater
from story_writer.models import StoryMemory, Chapter, PlotThread
from story_writer.utils import create_client


def test_thread_normalization():
    """Test that thread names are normalized correctly."""
    client = create_client()
    updater = StateUpdater(client)

    # Test cases
    test_cases = [
        ("Wind Walker Prophecy", "wind walker prophecy"),
        ("The Wind Walker prophecy", "wind walker prophecy"),
        ("wind walker prophecy", "wind walker prophecy"),
        ("A mysterious map", "mysterious map"),
        ("The Ancient Ruins", "ancient ruins"),
    ]

    print("\n" + "=" * 60)
    print("TEST: Thread Name Normalization")
    print("=" * 60)

    all_passed = True
    for input_name, expected in test_cases:
        result = updater._normalize_thread_name(input_name)
        passed = result == expected
        status = "[PASS]" if passed else "[FAIL]"
        print(f"{status}: '{input_name}' -> '{result}' (expected: '{expected}')")
        if not passed:
            all_passed = False

    return all_passed


def test_thread_deduplication():
    """Test that duplicate threads are not created."""
    client = create_client()
    updater = StateUpdater(client)

    # Create test memory with existing thread
    memory = StoryMemory(
        story_title="Test Story",
        world_name="Test World",
        saga_goal="Test goal"
    )

    # Add initial thread
    thread1 = PlotThread(
        thread_id="thread_001",
        name="Wind Walker Prophecy",
        thread_type="mystery",
        setup_chapter="ch_001",
        setup_description="A prophecy about the Wind Walker",
        status="open"
    )
    memory.plot_threads["thread_001"] = thread1

    print("\n" + "=" * 60)
    print("TEST: Thread Deduplication")
    print("=" * 60)
    print(f"Initial threads: {len(memory.plot_threads)}")
    print(f"  - {thread1.name}")

    # Create test chapter
    chapter = Chapter(
        chapter_id="ch_002",
        chapter_number=2,
        arc_id="arc_001",
        title="Test Chapter",
        content="Test content",
        word_count=100,
        summary="Test summary",
        cliffhanger="Test cliffhanger",
        cliffhanger_type="danger"
    )

    # Try to add duplicate threads with slight variations
    duplicate_threads = [
        {"action": "introduce", "thread_name": "The Wind Walker prophecy", "description": "Another mention"},
        {"action": "introduce", "thread_name": "wind walker prophecy", "description": "Yet another"},
        {"action": "introduce", "thread_name": "Wind Walker Prophecy", "description": "Exact duplicate"},
    ]

    print("\nAttempting to add 3 duplicate threads...")
    updater._apply_thread_updates(duplicate_threads, memory, chapter)

    print(f"\nFinal threads: {len(memory.plot_threads)}")
    for thread in memory.plot_threads.values():
        print(f"  - {thread.name} ({thread.thread_id})")

    # Should still have only 1 thread
    passed = len(memory.plot_threads) == 1
    status = "[PASS]" if passed else "[FAIL]"
    print(f"\n{status}: Expected 1 thread, got {len(memory.plot_threads)}")

    return passed


def main():
    """Run all tests."""
    print("\n" + "=" * 60)
    print("PHASE 4: THREAD DEDUPLICATION TESTS")
    print("=" * 60)

    test1_passed = test_thread_normalization()
    test2_passed = test_thread_deduplication()

    print("\n" + "=" * 60)
    print("TEST RESULTS")
    print("=" * 60)
    print(f"Thread Normalization: {'[PASS]' if test1_passed else '[FAIL]'}")
    print(f"Thread Deduplication: {'[PASS]' if test2_passed else '[FAIL]'}")

    if test1_passed and test2_passed:
        print("\n[SUCCESS] ALL TESTS PASSED!")
        return 0
    else:
        print("\n[ERROR] SOME TESTS FAILED")
        return 1


if __name__ == "__main__":
    sys.exit(main())
