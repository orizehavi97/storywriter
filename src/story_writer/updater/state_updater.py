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

        # Phase 4: Apply enhanced tracking
        self._apply_relationships(changes.get("relationships", []), memory, chapter)
        self._apply_timeline_events(changes.get("major_events", []), memory, chapter)

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

5. RELATIONSHIPS: Character relationships mentioned or established
   Format: [{{"character_a": "Name", "character_b": "Name", "type": "ally/friend/rival/enemy/mentor/family", "description": "context"}}]

6. MAJOR EVENTS: Significant events worth tracking in timeline
   Format: [{{"description": "what happened", "type": "battle/discovery/death/alliance/betrayal/revelation", "impact": "minor/moderate/major/critical"}}]

Return ONLY valid JSON in this format:
{{
  "new_characters": [...],
  "character_updates": [...],
  "location_updates": [...],
  "thread_updates": [...],
  "relationships": [...],
  "major_events": [...]
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
                "thread_updates": [],
                "relationships": [],
                "major_events": []
            }

        return changes

    def _apply_new_characters(
        self,
        new_chars: list[dict],
        memory: StoryMemory,
        chapter: Chapter
    ) -> None:
        """Add newly introduced characters to memory with smart deduplication."""
        if not new_chars:
            return

        print(f"[UPDATER] Adding {len(new_chars)} new character(s)...")

        from ..models import Character

        for char_data in new_chars:
            char_name = char_data.get("name")

            # Smart deduplication: normalize name and check for similar matches
            normalized_new_name = self._normalize_character_name(char_name)

            # Check for existing character with similar name
            existing_char = None
            for char in memory.characters.values():
                normalized_existing = self._normalize_character_name(char.name)
                if normalized_existing == normalized_new_name:
                    existing_char = char
                    break

            if existing_char:
                print(f"         - '{char_name}' matches existing '{existing_char.name}', skipping")

                # Update existing character if new info is more detailed
                if char_data.get("personality") and not existing_char.personality:
                    existing_char.personality = char_data.get("personality")
                    print(f"           Updated personality for '{existing_char.name}'")

                if char_data.get("role") and existing_char.role == "neutral":
                    existing_char.role = char_data.get("role")
                    print(f"           Updated role to '{existing_char.role}'")

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

    def _normalize_character_name(self, name: str) -> str:
        """
        Normalize character name for deduplication.

        Examples:
        - "The Mysterious Informant" -> "mysterious informant"
        - "Unnamed Guard Leader" -> "guard leader"
        - "Zephyr" -> "zephyr"
        - "Sky Captain" -> "sky captain"
        """
        if not name:
            return ""

        # Remove common articles and convert to lowercase
        normalized = name.lower().strip()

        # Remove leading articles
        for article in ["the ", "a ", "an "]:
            if normalized.startswith(article):
                normalized = normalized[len(article):]

        # Phase 4: Remove "unnamed" prefix
        if normalized.startswith("unnamed "):
            normalized = normalized[8:]  # Remove "unnamed "

        # Remove extra whitespace
        normalized = " ".join(normalized.split())

        return normalized

    def _normalize_thread_name(self, name: str) -> str:
        """
        Normalize plot thread name for deduplication.

        Examples:
        - "Wind Walker Prophecy" -> "wind walker prophecy"
        - "The Wind Walker prophecy" -> "wind walker prophecy"
        - "Wind Walker prophecy" -> "wind walker prophecy"
        """
        if not name:
            return ""

        # Remove common articles and convert to lowercase
        normalized = name.lower().strip()

        # Remove leading articles
        for article in ["the ", "a ", "an "]:
            if normalized.startswith(article):
                normalized = normalized[len(article):]

        # Remove extra whitespace
        normalized = " ".join(normalized.split())

        return normalized

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
                # Check if thread already exists (fuzzy match to avoid duplicates)
                normalized_new = self._normalize_thread_name(thread_name)
                existing_thread = None

                for thread in memory.plot_threads.values():
                    normalized_existing = self._normalize_thread_name(thread.name)
                    if normalized_existing == normalized_new:
                        existing_thread = thread
                        break

                if existing_thread:
                    # Thread already exists, just update it
                    print(f"         - Thread '{thread_name}' already exists as '{existing_thread.name}', skipping")
                    if description and not existing_thread.setup_description:
                        existing_thread.setup_description = description
                else:
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

    def _apply_relationships(
        self,
        relationships: list[dict],
        memory: StoryMemory,
        chapter: Chapter
    ) -> None:
        """Track character relationships (Phase 4)."""
        if not relationships:
            return

        print(f"[UPDATER] Tracking {len(relationships)} relationship(s)...")

        from ..models import Relationship

        for rel_data in relationships:
            char_a_name = rel_data.get("character_a")
            char_b_name = rel_data.get("character_b")

            # Find character IDs by name
            char_a_id = None
            char_b_id = None
            for char in memory.characters.values():
                if char.name == char_a_name:
                    char_a_id = char.character_id
                if char.name == char_b_name:
                    char_b_id = char.character_id

            if not char_a_id or not char_b_id:
                print(f"         - Warning: Could not find characters for relationship")
                continue

            # Create relationship ID (sorted to avoid duplicates)
            rel_key = tuple(sorted([char_a_id, char_b_id]))
            rel_id = f"rel_{rel_key[0]}_{rel_key[1]}"

            # Check if relationship exists
            if rel_id in memory.relationships:
                # Update existing
                memory.relationships[rel_id].last_updated = chapter.chapter_id
                print(f"         - Updated: {char_a_name} <-> {char_b_name}")
            else:
                # Create new
                new_rel = Relationship(
                    character_a=char_a_id,
                    character_b=char_b_id,
                    relationship_type=rel_data.get("type", "neutral"),
                    established_chapter=chapter.chapter_id,
                    last_updated=chapter.chapter_id,
                    notes=rel_data.get("description", "")
                )
                memory.relationships[rel_id] = new_rel
                print(f"         - New: {char_a_name} <-> {char_b_name} ({new_rel.relationship_type})")

    def _apply_timeline_events(
        self,
        events: list[dict],
        memory: StoryMemory,
        chapter: Chapter
    ) -> None:
        """Add events to world timeline (Phase 4)."""
        if not events:
            return

        print(f"[UPDATER] Adding {len(events)} event(s) to timeline...")

        from ..models import WorldEvent

        for event_data in events:
            event_id = f"event_{chapter.chapter_id}_{len(memory.world_timeline) + 1}"

            event = WorldEvent(
                event_id=event_id,
                chapter_id=chapter.chapter_id,
                chapter_number=chapter.chapter_number,
                description=event_data.get("description", ""),
                event_type=event_data.get("type", "discovery"),
                impact=event_data.get("impact", "minor")
            )

            memory.world_timeline.append(event)
            print(f"         - {event.event_type}: {event.description[:50]}...")
