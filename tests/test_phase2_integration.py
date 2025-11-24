"""Test Phase 2 integration."""

import sys
from pathlib import Path
import shutil

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))


def test_phase2_integration():
    """Test Phase 2 vector store and retrieval integration."""
    print("Testing Phase 2 Integration")
    print("=" * 60)

    from story_writer.memory import JSONMemoryStore, VectorMemoryStore, SmartRetriever
    from story_writer.models import Chapter, PlotThread
    from story_writer.utils import create_client

    # Use test directories
    test_json_dir = Path("data/memory_test_phase2")
    test_vector_dir = test_json_dir / "vectors"

    if test_json_dir.exists():
        shutil.rmtree(test_json_dir)

    try:
        # 1. Initialize stores
        print("\n1. Initializing stores...")
        json_store = JSONMemoryStore(data_dir=test_json_dir)
        vector_store = VectorMemoryStore(data_dir=test_json_dir)
        retriever = SmartRetriever(vector_store)
        print("[OK] Stores initialized")

        # 2. Create test story
        print("\n2. Creating test story...")
        memory = json_store.initialize_new_story(
            story_title="Phase 2 Test",
            world_name="Test World"
        )

        # 3. Add sample chapters
        print("\n3. Adding sample chapters...")
        for i in range(1, 4):
            chapter = Chapter(
                chapter_id=f"ch_{i:03d}",
                chapter_number=i,
                arc_id="arc_001",
                title=f"Test Chapter {i}",
                content=f"This is test chapter {i} content...",
                word_count=100,
                summary=f"Chapter {i} introduces key plot point {i}",
                key_events=[
                    f"Character meets ally {i}",
                    f"Mystery deepens about artifact {i}",
                    f"Villain plans revealed stage {i}"
                ],
                cliffhanger=f"Chapter {i} ends with suspense",
                cliffhanger_type="mystery"
            )

            memory.chapters[chapter.chapter_id] = chapter
            memory.current_chapter_number = i

            # Index in vector store
            vector_store.add_chapter(chapter)
            print(f"   Added and indexed Chapter {i}")

        # 4. Test vector search
        print("\n4. Testing semantic search...")

        # Search for chapters
        results = vector_store.search_chapters(
            query="artifact mystery",
            n_results=2
        )

        print(f"[OK] Found {len(results)} relevant chapters")
        for r in results:
            print(f"   - {r['id']}: {r['metadata']['title']}")

        # Search for events
        event_results = vector_store.search_events(
            query="villain plans",
            n_results=3
        )

        print(f"[OK] Found {len(event_results)} relevant events")
        for r in event_results:
            print(f"   - Ch {r['metadata']['chapter_number']}: {r['document'][:50]}...")

        # 5. Test smart retrieval
        print("\n5. Testing smart retrieval...")
        retrieved = retriever.retrieve_for_planning(
            memory=memory,
            n_recent=2,
            n_relevant=2,
            n_surprise=1
        )

        assert len(retrieved["recent_chapters"]) > 0, "Should have recent chapters"
        print(f"[OK] Retrieved {len(retrieved['recent_chapters'])} recent chapters")

        if len(retrieved["relevant_chapters"]) > 0:
            print(f"[OK] Retrieved {len(retrieved['relevant_chapters'])} relevant chapters")

        # 6. Verify stats
        print("\n6. Checking vector store stats...")
        stats = vector_store.get_stats()
        assert stats['chapters'] == 3, f"Should have 3 chapters, got {stats['chapters']}"
        assert stats['events'] == 9, f"Should have 9 events (3 per chapter), got {stats['events']}"
        print(f"[OK] Stats correct:")
        print(f"   - Chapters: {stats['chapters']}")
        print(f"   - Events: {stats['events']}")
        print(f"   - Threads: {stats['threads']}")

        print("\n" + "=" * 60)
        print("[PASS] Phase 2 integration test completed successfully!")
        print("=" * 60)

        return True

    except Exception as e:
        print(f"\n[FAIL] Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

    finally:
        # Cleanup
        if test_json_dir.exists():
            shutil.rmtree(test_json_dir)
            print(f"\n[OK] Cleaned up test directory")


if __name__ == "__main__":
    success = test_phase2_integration()
    sys.exit(0 if success else 1)
