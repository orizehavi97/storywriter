"""Test chapter planner."""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))


def test_chapter_planner():
    """Test chapter planner with LLM."""
    print("Testing Chapter Planner")
    print("=" * 60)

    from story_writer.planner import ChapterPlanner
    from story_writer.memory import JSONMemoryStore
    from story_writer.models import Character, Arc
    from story_writer.utils import create_client

    try:
        # Create LLM client
        print("\n1. Creating LLM client...")
        client = create_client()
        print(f"[OK] Using {client.provider} - {client.model}")

        # Create planner
        print("\n2. Creating chapter planner...")
        planner = ChapterPlanner(client)
        print("[OK] Planner initialized")

        # Create a minimal story memory
        print("\n3. Creating test story memory...")
        store = JSONMemoryStore()
        memory = store.initialize_new_story(
            story_title="Sky Wanderers",
            world_name="The Shattered Isles",
            saga_goal="Unite the scattered sky islands"
        )

        # Add a protagonist
        protagonist = Character(
            character_id="char_001",
            name="Kael",
            age=17,
            personality="Optimistic, reckless, fiercely loyal",
            dream="Find his lost homeland",
            abilities=["Sky Affinity", "Natural navigator"],
            role="protagonist",
            status="active"
        )
        memory.characters[protagonist.character_id] = protagonist

        # Add a companion
        companion = Character(
            character_id="char_002",
            name="Finn",
            personality="Cautious, inventive, loyal",
            role="ally",
            status="active"
        )
        memory.characters[companion.character_id] = companion

        # Create a starting arc
        arc = Arc(
            arc_id="arc_001",
            arc_number=1,
            name="The Lost Trader",
            arc_type="mystery",
            summary="Mysterious disappearances plague Drift Port as traders vanish without a trace",
            primary_location="Drift Port",
            central_conflict="Missing traders and strange disappearances",
            themes=["mystery", "friendship"],
            current_phase="arrival",
            status="active"
        )
        memory.arcs[arc.arc_id] = arc
        memory.current_arc_id = arc.arc_id

        print("[OK] Story context created")
        print(f"    - Story: {memory.story_title}")
        print(f"    - Characters: {len(memory.characters)}")
        print(f"    - Arc: {arc.name}")

        # Plan first chapter
        print("\n4. Planning Chapter 1...")
        print("    (This will call the LLM API - may take 10-20 seconds)")
        outline = planner.plan_chapter(memory, arc)

        # Verify outline
        print("\n5. Verifying outline...")
        assert outline is not None, "Outline should not be None"
        assert outline.chapter_number == 1, "Should be chapter 1"
        assert outline.title, "Should have a title"
        assert len(outline.scenes) > 0, "Should have scenes"
        assert outline.cliffhanger, "Should have a cliffhanger"

        print("[OK] Outline structure verified")
        print(f"\n" + "=" * 60)
        print("GENERATED OUTLINE:")
        print("=" * 60)
        print(f"Title: {outline.title}")
        print(f"Summary: {outline.summary}")
        print(f"\nScenes: {len(outline.scenes)}")
        for i, scene in enumerate(outline.scenes, 1):
            print(f"  {i}. {scene.get('location', 'Unknown')} - {scene.get('purpose', 'No purpose')}")
        print(f"\nKey Events: {len(outline.key_events)}")
        for event in outline.key_events:
            print(f"  - {event}")
        print(f"\nCliffhanger ({outline.cliffhanger_type}): {outline.cliffhanger}")
        print("=" * 60)

        print("\n[PASS] Chapter planner test completed successfully!")

        return True

    except Exception as e:
        print(f"\n[FAIL] Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = test_chapter_planner()
    sys.exit(0 if success else 1)
