"""State updater to extract changes from chapters and update memory."""

import json
from typing import Optional

from ..models import StoryMemory, Chapter
from ..utils import LLMClient


class StateUpdater:
    """Extracts state changes from chapters and updates memory."""

    def __init__(self, llm_client: LLMClient, vector_store=None):
        """
        Initialize state updater.

        Args:
            llm_client: LLM client for extraction
            vector_store: Optional VectorMemoryStore for Phase 2 indexing
        """
        self.client = llm_client
        self.vector_store = vector_store  # Phase 2 enhancement

    def update_from_chapter(self, chapter: Chapter, memory: StoryMemory) -> StoryMemory:
        """
        Update story memory based on a completed chapter.

        Args:
            chapter: The completed chapter
            memory: Current story memory

        Returns:
            Updated story memory
        """
        print(f"\n[UPDATER] Updating memory from Chapter {chapter.chapter_number}...")

        # Add chapter to memory
        memory.chapters[chapter.chapter_id] = chapter
        memory.current_chapter_number = chapter.chapter_number

        # Extract state changes using LLM
        print(f"[UPDATER] Extracting state changes...")
        changes = self._extract_state_changes(chapter)

        # Apply changes to memory
        self._apply_new_characters(changes.get("new_characters", []), memory, chapter)
        self._apply_character_updates(changes.get("character_updates", []), memory)
        self._apply_location_updates(changes.get("location_updates", []), memory)
        self._apply_thread_updates(changes.get("thread_updates", []), memory, chapter)

        # Update arc progress
        if memory.current_arc_id:
            arc = memory.arcs.get(memory.current_arc_id)
            if arc:
                arc.current_chapter += 1
                print(f"[UPDATER] Arc '{arc.name}' progress: {arc.current_chapter}/{arc.expected_chapters}")

        # Update theme counts
        for theme in chapter.themes:
            memory.theme_counts[theme] = memory.theme_counts.get(theme, 0) + 1

        # Phase 2: Index in vector store
        if self.vector_store:
            print(f"[UPDATER] Indexing chapter in vector store...")
            self.vector_store.add_chapter(chapter)

            # Index any new threads
            for thread_id, thread in memory.plot_threads.items():
                if thread.setup_chapter == chapter.chapter_id:
                    self.vector_store.add_thread(thread)

        print(f"[OK] Memory updated successfully")

        return memory

    def _extract_state_changes(self, chapter: Chapter) -> dict:
        """
        Use LLM to extract state changes from chapter content.

        Args:
            chapter: The chapter to analyze

        Returns:
            Dictionary of state changes
        """
        prompt = f"""Analyze this chapter and extract state changes.

CHAPTER: {chapter.title}
CONTENT:
{chapter.content}

Extract the following information in JSON format:

1. NEW CHARACTERS: Characters introduced or mentioned for the first time
   Format: [{{"name": "Name", "role": "protagonist/antagonist/ally/mentor/neutral", "personality": "brief description", "first_description": "how they were introduced"}}]

2. CHARACTER UPDATES: Changes to existing character states, locations, or possessions
   Format: [{{"character_name": "Name", "updates": {{"status": "injured/captured/etc", "location": "new location", "items_gained": ["item"], "items_lost": ["item"]}}}}]

3. LOCATION UPDATES: Changes to locations (destroyed, modified, discovered)
   Format: [{{"location_name": "Name", "change": "description of change", "status": "active/destroyed"}}]

4. THREAD UPDATES: Progress on existing plot threads or new threads introduced
   Format: [{{"action": "progress/resolve/introduce", "thread_name": "Name", "description": "what happened"}}]

Return ONLY valid JSON in this format:
{{
  "new_characters": [...],
  "character_updates": [...],
  "location_updates": [...],
  "thread_updates": [...]
}}

If no changes in a category, use empty array []."""

        system_prompt = """You are a story analysis expert. Extract factual state changes from narrative text.
Focus on concrete, verifiable changes like:
- New characters introduced (named characters who appear or speak)
- Character injuries, captures, or status changes
- Locations discovered, destroyed, or modified
- Plot threads introduced, advanced, or resolved

For new characters, only include those with names or significant roles (not unnamed "townspeople" or "guards").
Be conservative - only report changes explicitly stated or strongly implied in the text."""

        response = self.client.generate(
            prompt=prompt,
            system_prompt=system_prompt,
            temperature=0.3,  # Low temperature for factual extraction
            max_tokens=2000
        )

        # Parse JSON response
        response = response.strip()
        if response.startswith("```"):
            lines = response.split("\n")
            start_idx = 0
            end_idx = len(lines)
            for i, line in enumerate(lines):
                if line.strip().startswith("```"):
                    if start_idx == 0:
                        start_idx = i + 1
                    else:
                        end_idx = i
                        break
            response = "\n".join(lines[start_idx:end_idx])

        try:
            changes = json.loads(response)
        except json.JSONDecodeError as e:
            print(f"[WARN] Failed to parse state changes: {e}")
            print(f"         Using empty changes")
            changes = {
                "new_characters": [],
                "character_updates": [],
                "location_updates": [],
                "thread_updates": []
            }

        return changes

    def _apply_new_characters(
        self,
        new_chars: list[dict],
        memory: StoryMemory,
        chapter: Chapter
    ) -> None:
        """Add newly introduced characters to memory."""
        if not new_chars:
            return

        print(f"[UPDATER] Adding {len(new_chars)} new character(s)...")

        from ..models import Character

        for char_data in new_chars:
            char_name = char_data.get("name")

            # Check if character already exists
            exists = any(c.name == char_name for c in memory.characters.values())
            if exists:
                print(f"         - '{char_name}' already exists, skipping")
                continue

            # Generate character ID
            char_id = f"char_{len(memory.characters) + 1:03d}"

            # Create new character
            new_char = Character(
                character_id=char_id,
                name=char_name,
                personality=char_data.get("personality", ""),
                role=char_data.get("role", "neutral"),
                background=char_data.get("first_description", ""),
                status="active",
                current_location=""  # Will be updated as they appear
            )

            memory.characters[char_id] = new_char
            print(f"         - Added '{char_name}' ({new_char.role})")

    def _apply_character_updates(
        self,
        updates: list[dict],
        memory: StoryMemory
    ) -> None:
        """Apply character updates to memory."""
        if not updates:
            return

        print(f"[UPDATER] Applying {len(updates)} character update(s)...")

        for update_data in updates:
            char_name = update_data.get("character_name")
            updates_dict = update_data.get("updates", {})

            # Find character by name
            character = None
            for char in memory.characters.values():
                if char.name == char_name:
                    character = char
                    break

            if not character:
                print(f"         - Warning: Character '{char_name}' not found in memory")
                continue

            # Apply updates
            if "status" in updates_dict:
                old_status = character.status
                character.status = updates_dict["status"]
                print(f"         - {char_name}: status {old_status} -> {character.status}")

            if "location" in updates_dict:
                character.current_location = updates_dict["location"]
                print(f"         - {char_name}: location updated to {character.current_location}")

            if "items_gained" in updates_dict:
                for item in updates_dict["items_gained"]:
                    if item not in character.items:
                        character.items.append(item)
                        print(f"         - {char_name}: gained item '{item}'")

            if "items_lost" in updates_dict:
                for item in updates_dict["items_lost"]:
                    if item in character.items:
                        character.items.remove(item)
                        print(f"         - {char_name}: lost item '{item}'")

    def _apply_location_updates(
        self,
        updates: list[dict],
        memory: StoryMemory
    ) -> None:
        """Apply location updates to memory."""
        if not updates:
            return

        print(f"[UPDATER] Applying {len(updates)} location update(s)...")

        for update_data in updates:
            loc_name = update_data.get("location_name")
            change = update_data.get("change")
            status = update_data.get("status")

            # Find location by name
            location = None
            for loc in memory.locations.values():
                if loc.name == loc_name:
                    location = loc
                    break

            if location:
                if status:
                    location.status = status
                print(f"         - {loc_name}: {change}")
            else:
                print(f"         - New location mentioned: {loc_name} ({change})")

    def _apply_thread_updates(
        self,
        updates: list[dict],
        memory: StoryMemory,
        chapter: Chapter
    ) -> None:
        """Apply plot thread updates to memory."""
        if not updates:
            return

        print(f"[UPDATER] Applying {len(updates)} thread update(s)...")

        from ..models import PlotThread

        for update_data in updates:
            action = update_data.get("action")
            thread_name = update_data.get("thread_name")
            description = update_data.get("description", "")

            if action == "introduce":
                # Create new thread
                thread_id = f"thread_{len(memory.plot_threads) + 1:03d}"
                new_thread = PlotThread(
                    thread_id=thread_id,
                    name=thread_name,
                    thread_type="mystery",  # Default type
                    setup_chapter=chapter.chapter_id,
                    setup_description=description,
                    status="open"
                )
                memory.plot_threads[thread_id] = new_thread
                print(f"         - New thread: '{thread_name}'")

            elif action == "progress":
                # Find and update existing thread
                thread = None
                for t in memory.plot_threads.values():
                    if t.name == thread_name:
                        thread = t
                        break

                if thread:
                    thread.status = "progressing"
                    thread.developments.append({
                        "chapter_id": chapter.chapter_id,
                        "description": description
                    })
                    print(f"         - Progressed thread: '{thread_name}'")
                else:
                    print(f"         - Warning: Thread '{thread_name}' not found")

            elif action == "resolve":
                # Find and resolve thread
                thread = None
                for t in memory.plot_threads.values():
                    if t.name == thread_name:
                        thread = t
                        break

                if thread:
                    thread.status = "resolved"
                    thread.resolution_chapter = chapter.chapter_id
                    thread.resolution_description = description
                    print(f"         - Resolved thread: '{thread_name}'")
                else:
                    print(f"         - Warning: Thread '{thread_name}' not found")
