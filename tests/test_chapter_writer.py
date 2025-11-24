"""Test chapter writer."""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))


def test_chapter_writer():
    """Test chapter writer with planner."""
    print("Testing Chapter Writer")
    print("=" * 60)

    from story_writer.planner import ChapterPlanner
    from story_writer.writer import ChapterWriter
    from story_writer.memory import JSONMemoryStore
    from story_writer.models import Character, Arc
    from story_writer.utils import create_client

    try:
        # Create LLM client
        print("\n1. Creating LLM client...")
        client = create_client()
        print(f"[OK] Using {client.provider} - {client.model}")

        # Create planner and writer
        print("\n2. Creating planner and writer...")
        planner = ChapterPlanner(client)
        writer = ChapterWriter(client)
        print("[OK] Components initialized")

        # Create test story
        print("\n3. Creating test story...")
        store = JSONMemoryStore()
        memory = store.initialize_new_story(
            story_title="Sky Wanderers",
            world_name="The Shattered Isles",
            saga_goal="Unite the scattered sky islands"
        )

        # Add protagonist
        kael = Character(
            character_id="char_001",
            name="Kael",
            age=17,
            personality="Optimistic, reckless, fiercely loyal, curious",
            speech_pattern="Enthusiastic, asks lots of questions",
            quirks=["Always looking up at the sky", "Collects island maps"],
            dream="Find his lost homeland",
            abilities=["Sky Affinity", "Natural navigator"],
            role="protagonist",
            status="active"
        )
        memory.characters[kael.character_id] = kael

        # Add companion
        finn = Character(
            character_id="char_002",
            name="Finn",
            personality="Cautious, inventive, loyal",
            speech_pattern="Technical jargon, worries a lot",
            quirks=["Constantly tinkering with gadgets"],
            role="ally",
            status="active"
        )
        memory.characters[finn.character_id] = finn

        # Create arc
        arc = Arc(
            arc_id="arc_001",
            arc_number=1,
            name="The Lost Trader",
            arc_type="mystery",
            summary="Mysterious disappearances plague Drift Port",
            primary_location="Drift Port",
            central_conflict="Missing traders and strange disappearances",
            themes=["mystery", "friendship"],
            current_phase="arrival",
            status="active"
        )
        memory.arcs[arc.arc_id] = arc
        memory.current_arc_id = arc.arc_id

        print("[OK] Story context created")

        # Plan chapter
        print("\n4. Planning chapter...")
        print("    (Calling LLM API...)")
        outline = planner.plan_chapter(memory, arc)

        # Write chapter
        print("\n5. Writing full chapter...")
        print("    (Calling LLM API... may take 20-40 seconds)")
        chapter = writer.write_chapter(outline, memory)

        # Verify chapter
        print("\n6. Verifying chapter...")
        assert chapter is not None, "Chapter should not be None"
        assert chapter.chapter_number == 1, "Should be chapter 1"
        assert chapter.title, "Should have a title"
        assert chapter.content, "Should have content"
        assert chapter.word_count > 500, f"Should have substantial content (got {chapter.word_count} words)"

        print("[OK] Chapter structure verified")
        print(f"\n" + "=" * 60)
        print("GENERATED CHAPTER:")
        print("=" * 60)
        print(f"Chapter {chapter.chapter_number}: {chapter.title}")
        print(f"Word Count: {chapter.word_count}")
        print(f"Arc: {chapter.arc_id}")
        print(f"\n{'-' * 60}")
        print(f"{chapter.content[:500]}...")
        print(f"\n[... {chapter.word_count - 500} more words ...]")
        print(f"{'-' * 60}")
        print(f"\nEnds with ({chapter.cliffhanger_type}): {chapter.cliffhanger}")
        print("=" * 60)

        print("\n[PASS] Chapter writer test completed successfully!")

        return True

    except Exception as e:
        print(f"\n[FAIL] Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = test_chapter_writer()
    sys.exit(0 if success else 1)
