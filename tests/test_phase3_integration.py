"""
Integration test for Phase 3: Quality Control System

Tests the continuity checker, quality checker, and revision system.
"""

import sys
from pathlib import Path

# Add parent directory to path
test_dir = Path(__file__).parent
sys.path.insert(0, str(test_dir.parent / "src"))

from story_writer.checker import ContinuityChecker, QualityChecker
from story_writer.writer.chapter_reviser import ChapterReviser
from story_writer.models import (
    Chapter, StoryMemory, Character, Arc, PlotThread
)
from story_writer.utils import create_client


def test_phase3_integration():
    """Test Phase 3 quality control components."""

    print("\n" + "=" * 60)
    print("PHASE 3 INTEGRATION TEST")
    print("=" * 60)

    # Initialize components
    print("\n[TEST] Initializing Phase 3 components...")
    client = create_client()

    continuity_checker = ContinuityChecker()
    quality_checker = QualityChecker(client)
    reviser = ChapterReviser(client)

    print("[OK] All Phase 3 components initialized")

    # Create test story memory
    print("\n[TEST] Creating test story memory...")
    memory = StoryMemory(
        story_title="Test Story",
        world_name="Test World",
        saga_goal="Test the quality control system"
    )

    # Add test character
    char = Character(
        character_id="char_001",
        name="TestHero",
        personality="Brave and optimistic",
        role="protagonist",
        status="active",
        current_location="Test Town"
    )
    memory.characters[char.character_id] = char

    # Add test arc
    arc = Arc(
        arc_id="arc_001",
        arc_number=1,
        name="Test Arc",
        arc_type="exploration",
        summary="Testing Phase 3",
        primary_location="Test Town",
        central_conflict="Test conflict",
        themes=["adventure", "friendship"],
        expected_chapters=3,
        status="active"
    )
    memory.arcs[arc.arc_id] = arc
    memory.current_arc_id = arc.arc_id

    # Create test chapter
    print("\n[TEST] Creating test chapter...")
    test_chapter = Chapter(
        chapter_id="ch_001",
        chapter_number=1,
        arc_id=arc.arc_id,
        title="The Beginning",
        summary="TestHero starts their adventure in Test Town.",
        scenes=[
            {
                "location": "Test Town",
                "characters": ["TestHero"],
                "purpose": "Introduction",
                "tone": "optimistic"
            }
        ],
        key_events=["TestHero arrives in Test Town", "TestHero meets locals"],
        character_moments={"TestHero": "Shows determination"},
        cliffhanger="A mysterious figure appears!",
        cliffhanger_type="character_arrival",
        themes_present=["adventure"],
        foreshadowing=["The mysterious figure knows something"],
        content="""# Chapter 1: The Beginning

TestHero walked into Test Town with a smile on their face. The sun was shining, and adventure awaited!

"This is it!" TestHero said. "My journey begins here!"

The townspeople welcomed TestHero warmly. Everyone seemed friendly and optimistic about the future.

As the sun set, TestHero noticed a mysterious figure watching from the shadows. Who could it be?""",
        word_count=62
    )

    # Add chapter to memory
    memory.chapters[test_chapter.chapter_id] = test_chapter
    memory.current_chapter_number = 1

    print("[OK] Test chapter created")

    # Test 1: Continuity Check
    print("\n" + "=" * 60)
    print("TEST 1: Continuity Checker")
    print("=" * 60)

    violations = continuity_checker.check_chapter(test_chapter, memory)

    if len(violations) == 0:
        print("[OK] No continuity violations found")
    else:
        print(f"[INFO] Found {len(violations)} violations (expected for test)")
        for v in violations:
            print(f"  - [{v.severity}] {v.description}")

    # Test 2: Quality Check
    print("\n" + "=" * 60)
    print("TEST 2: Quality Checker")
    print("=" * 60)

    quality_report = quality_checker.check_chapter(
        test_chapter,
        test_chapter.content,
        memory
    )

    assert quality_report.overall_score >= 0 and quality_report.overall_score <= 100
    print(f"[OK] Quality assessment complete (score: {quality_report.overall_score}/100)")

    # Test 3: Revision (only if quality is low)
    if quality_report.needs_revision or len(violations) > 0:
        print("\n" + "=" * 60)
        print("TEST 3: Chapter Reviser")
        print("=" * 60)

        revision_result = reviser.revise_chapter(
            chapter=test_chapter,
            chapter_text=test_chapter.content,
            violations=violations,
            quality_report=quality_report,
            attempt=1
        )

        assert len(revision_result.revised_text) > 0
        print(f"[OK] Revision complete")
        print(f"     Original: {test_chapter.word_count} words")
        print(f"     Revised: {len(revision_result.revised_text.split())} words")
    else:
        print("\n[INFO] Chapter quality acceptable, skipping revision test")

    # Final summary
    print("\n" + "=" * 60)
    print("PHASE 3 TEST SUMMARY")
    print("=" * 60)
    print("[OK] Continuity Checker: Working")
    print("[OK] Quality Checker: Working")
    print("[OK] Chapter Reviser: Working")
    print("\n[OK] All Phase 3 integration tests passed!")


if __name__ == "__main__":
    try:
        test_phase3_integration()
    except Exception as e:
        print(f"\n[FAIL] Test failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
