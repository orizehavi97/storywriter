"""
Main entry point for the Story Writer system.

Orchestrates all components to generate chapters.
"""

import sys
from pathlib import Path

# Add src to path for development
sys.path.insert(0, str(Path(__file__).parent / "src"))

from story_writer.memory import JSONMemoryStore
from story_writer.planner import ChapterPlanner
from story_writer.writer import ChapterWriter
from story_writer.updater import StateUpdater
from story_writer.models import Character, Arc, PlotThread
from story_writer.utils import create_client, get_world_seed


def initialize_new_story(store: JSONMemoryStore) -> None:
    """Initialize a new story from world seed."""
    print("\n" + "=" * 60)
    print("INITIALIZING NEW STORY")
    print("=" * 60)

    world_seed = get_world_seed()

    # Create story memory
    memory = store.initialize_new_story(
        story_title=f"Chronicles of {world_seed['world_name']}",
        world_name=world_seed['world_name'],
        saga_goal=world_seed['central_conflict']
    )

    # Add protagonist
    protag_data = world_seed['protagonist']
    protagonist = Character(
        character_id="char_001",
        name=protag_data['name'],
        age=protag_data.get('age'),
        personality=protag_data['personality'],
        dream=protag_data['dream'],
        quirks=protag_data.get('quirks', '').split(', '),
        abilities=protag_data.get('abilities', '').split(', ') if isinstance(protag_data.get('abilities'), str) else protag_data.get('abilities', []),
        background=protag_data.get('background', ''),
        role="protagonist",
        status="active",
        current_location=world_seed['starting_location']['name']
    )
    memory.characters[protagonist.character_id] = protagonist
    print(f"[OK] Added protagonist: {protagonist.name}")

    # Add initial crew
    for i, crew_data in enumerate(world_seed.get('initial_crew', []), start=2):
        crew_member = Character(
            character_id=f"char_{i:03d}",
            name=crew_data['name'],
            personality=crew_data['personality'],
            role=crew_data.get('role', 'ally'),
            background=crew_data.get('background', ''),
            status="active",
            current_location=world_seed['starting_location']['name']
        )
        memory.characters[crew_member.character_id] = crew_member
        print(f"[OK] Added crew member: {crew_member.name}")

    # Add initial plot threads
    for i, thread_data in enumerate(world_seed.get('initial_threads', []), start=1):
        thread = PlotThread(
            thread_id=f"thread_{i:03d}",
            name=thread_data['thread'],
            thread_type=thread_data['type'],
            setup_chapter="ch_000",
            setup_description=thread_data['thread'],
            status="open",
            importance="major"
        )
        memory.plot_threads[thread.thread_id] = thread
        print(f"[OK] Added plot thread: {thread.name}")

    # Create first arc
    arc = Arc(
        arc_id="arc_001",
        arc_number=1,
        name="Arrival",
        arc_type="exploration",
        summary=f"The adventure begins at {world_seed['starting_location']['name']}",
        primary_location=world_seed['starting_location']['name'],
        central_conflict=world_seed['central_conflict'],
        themes=world_seed.get('themes', ['adventure', 'friendship']),
        expected_chapters=5,
        status="active"
    )
    memory.arcs[arc.arc_id] = arc
    memory.current_arc_id = arc.arc_id
    print(f"[OK] Created first arc: {arc.name}")

    # Save initial state
    store.save(memory, backup=False)
    print("\n[OK] Story initialized and saved!")


def generate_chapter(
    planner: ChapterPlanner,
    writer: ChapterWriter,
    updater: StateUpdater,
    store: JSONMemoryStore,
    memory
) -> None:
    """Generate a single chapter."""
    print("\n" + "=" * 60)
    print(f"GENERATING CHAPTER {memory.current_chapter_number + 1}")
    print("=" * 60)

    # Get current arc
    arc = memory.get_current_arc()

    # Plan chapter
    outline = planner.plan_chapter(memory, arc)

    # Write chapter
    chapter = writer.write_chapter(outline, memory)

    # Save chapter text
    store.save_chapter_text(chapter.chapter_id, chapter.content)

    # Update memory
    memory = updater.update_from_chapter(chapter, memory)

    # Save updated memory
    store.save(memory, backup=True)

    print(f"\n[OK] Chapter {chapter.chapter_number} complete!")
    print(f"     Title: {chapter.title}")
    print(f"     Words: {chapter.word_count}")
    print(f"     File: data/chapters/{chapter.chapter_id}.md")


def main():
    """Main entry point."""
    print("=" * 60)
    print("ODA-STYLE MANGA STORY ENGINE (OSSE)")
    print("Phase 1 - Minimal System")
    print("=" * 60)

    try:
        # Initialize components
        print("\nInitializing components...")
        client = create_client()
        print(f"[OK] LLM Client: {client.provider} - {client.model}")

        planner = ChapterPlanner(client)
        writer = ChapterWriter(client)
        updater = StateUpdater(client)
        store = JSONMemoryStore()
        print("[OK] All components initialized")

        # Check if story exists
        if not store.exists():
            print("\n[INFO] No existing story found")
            response = input("Initialize new story? (y/n): ")

            if response.lower() == 'y':
                initialize_new_story(store)
            else:
                print("Exiting...")
                return

        # Load story
        memory = store.load()

        # Main loop
        print("\n" + "=" * 60)
        print("STORY GENERATION LOOP")
        print("=" * 60)
        print(f"\nStory: {memory.story_title}")
        print(f"Current chapter: {memory.current_chapter_number}")
        print(f"Characters: {len(memory.characters)}")
        print(f"Open threads: {len(memory.open_threads)}")

        while True:
            print(f"\nOptions:")
            print(f"  1. Generate next chapter (Ch {memory.current_chapter_number + 1})")
            print(f"  2. View story stats")
            print(f"  3. Exit")

            choice = input("\nChoice: ").strip()

            if choice == '1':
                generate_chapter(planner, writer, updater, store, memory)

            elif choice == '2':
                print(f"\n" + "=" * 60)
                print("STORY STATISTICS")
                print("=" * 60)
                print(f"Title: {memory.story_title}")
                print(f"World: {memory.world_name}")
                print(f"Chapters written: {len(memory.chapters)}")
                print(f"Characters: {len(memory.characters)}")
                print(f"  - Active: {sum(1 for c in memory.characters.values() if c.status == 'active')}")
                print(f"Arcs: {len(memory.arcs)}")
                print(f"Plot threads:")
                print(f"  - Open: {len(memory.open_threads)}")
                print(f"  - Resolved: {sum(1 for t in memory.plot_threads.values() if t.status == 'resolved')}")
                print(f"Themes used: {dict(memory.theme_counts)}")

            elif choice == '3':
                print("\nExiting Story Writer...")
                break

            else:
                print("Invalid choice")

    except KeyboardInterrupt:
        print("\n\nInterrupted by user. Exiting...")
    except Exception as e:
        print(f"\n[ERROR] {e}")
        import traceback
        traceback.print_exc()
        return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())
