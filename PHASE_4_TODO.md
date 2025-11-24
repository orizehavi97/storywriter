# Phase 4 Implementation TODO

**Status:** Foundation Complete - Implementation Pending
**Created:** 2025-11-24
**Estimated Time:** 2-3 hours

---

## What's Done ✅

1. **Data Models Created** (`src/story_writer/models/tracker.py`)
   - `CharacterAlias` - Track character alternate names
   - `Relationship` - Character relationship tracking
   - `WorldEvent` - Timeline event tracking

2. **Directory Structure**
   - `src/story_writer/tracker/` created
   - Models exported in `__init__.py`

3. **Committed to Git**
   - Commit: "feat: Add Phase 4 data models for enhanced state tracking"
   - Branch: master

---

## What Needs to Be Done 🚧

### 1. Update StoryMemory Model (30 min)

**File:** `src/story_writer/models/memory.py`

Add Phase 4 fields to `StoryMemory` class:

```python
# Phase 4: Enhanced tracking
character_aliases: dict[str, CharacterAlias] = Field(
    default_factory=dict,
    description="Character ID -> CharacterAlias"
)

relationships: dict[str, Relationship] = Field(
    default_factory=dict,
    description="Relationship ID -> Relationship"
)

world_timeline: list[WorldEvent] = Field(
    default_factory=list,
    description="Chronological list of major events"
)
```

### 2. Enhanced Character Deduplication (1 hour)

**File:** `src/story_writer/updater/state_updater.py`

**Update `_normalize_character_name()` method:**

```python
def _normalize_character_name(self, name: str) -> str:
    """Enhanced normalization with 'Unnamed X' handling."""
    if not name:
        return ""

    normalized = name.lower().strip()

    # Remove leading articles
    for article in ["the ", "a ", "an "]:
        if normalized.startswith(article):
            normalized = normalized[len(article):]

    # Remove "unnamed" prefix (NEW)
    if normalized.startswith("unnamed "):
        normalized = normalized[8:]  # Remove "unnamed "

    # Remove extra whitespace
    normalized = " ".join(normalized.split())

    return normalized
```

**Add alias tracking in `_apply_new_characters()`:**

```python
# After creating new character, check for aliases
# If character has multiple names mentioned, track them
if char_name != normalized_new_name:
    alias_id = f"alias_{char_id}"
    alias = CharacterAlias(
        character_id=char_id,
        primary_name=char_name,
        aliases=[]
    )
    memory.character_aliases[alias_id] = alias
```

### 3. Relationship Tracking (1 hour)

**File:** `src/story_writer/updater/state_updater.py`

**Add to extraction prompt:**

```python
5. RELATIONSHIPS: Character relationships mentioned or established
   Format: [{{"character_a": "Name", "character_b": "Name", "type": "ally/friend/rival/enemy/mentor", "description": "context"}}]
```

**Add method `_apply_relationships()`:**

```python
def _apply_relationships(
    self,
    relationships: list[dict],
    memory: StoryMemory,
    chapter: Chapter
) -> None:
    """Add or update character relationships."""
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
```

### 4. World Event Timeline (30 min)

**File:** `src/story_writer/updater/state_updater.py`

**Add to extraction prompt:**

```python
6. MAJOR EVENTS: Significant events worth tracking in timeline
   Format: [{{"description": "what happened", "type": "battle/discovery/death/alliance/betrayal", "impact": "minor/moderate/major/critical"}}]
```

**Add method `_apply_timeline_events()`:**

```python
def _apply_timeline_events(
    self,
    events: list[dict],
    memory: StoryMemory,
    chapter: Chapter
) -> None:
    """Add events to world timeline."""
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
```

### 5. Update `update_from_chapter()` Method

**File:** `src/story_writer/updater/state_updater.py`

Add Phase 4 applications:

```python
def update_from_chapter(self, chapter: Chapter, memory: StoryMemory) -> StoryMemory:
    # ... existing code ...

    # Apply changes to memory
    self._apply_new_characters(changes.get("new_characters", []), memory, chapter)
    self._apply_character_updates(changes.get("character_updates", []), memory)
    self._apply_location_updates(changes.get("location_updates", []), memory)
    self._apply_thread_updates(changes.get("thread_updates", []), memory, chapter)

    # Phase 4: Apply enhanced tracking
    self._apply_relationships(changes.get("relationships", []), memory, chapter)
    self._apply_timeline_events(changes.get("major_events", []), memory, chapter)

    # ... rest of existing code ...
```

### 6. Testing (30 min)

**Create:** `tests/test_phase4_integration.py`

```python
"""Test Phase 4 enhanced state tracking."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from story_writer.updater import StateUpdater
from story_writer.utils import create_client

def test_phase4_features():
    """Test Phase 4 tracking features."""

    print("\n" + "=" * 60)
    print("PHASE 4 INTEGRATION TEST")
    print("=" * 60)

    client = create_client()
    updater = StateUpdater(client)

    # Test 1: Enhanced name normalization
    print("\n[TEST 1] Enhanced name normalization...")
    test_cases = [
        ("Unnamed Guard Leader", "guard leader"),
        ("The Unnamed Captain", "captain"),
        ("Guard Leader", "guard leader"),
    ]

    for original, expected in test_cases:
        result = updater._normalize_character_name(original)
        status = "[OK]" if result == expected else "[FAIL]"
        print(f"  {status} '{original}' -> '{result}' (expected: '{expected}')")

    print("\n[OK] All Phase 4 tests passed!")

if __name__ == "__main__":
    test_phase4_features()
```

**Run:** `python tests/test_phase4_integration.py`

### 7. Final Integration Test

Delete existing chapters and regenerate with Phase 4:

```bash
# Backup current data
cp -r data data_backup

# Delete chapters
rm data/chapters/*.md

# Reset memory (or let it auto-update)
python main.py
# Select option 1 to generate chapter
```

Check output for Phase 4 messages:
```
[UPDATER] Tracking 2 relationship(s)...
         - New: Kael <-> Finn (ally)
[UPDATER] Adding 1 event(s) to timeline...
         - discovery: Ancient ruins discovered
```

---

## Success Criteria ✓

Phase 4 is complete when:

1. ✅ "Unnamed Guard Leader" = "Guard Leader" (deduplication works)
2. ✅ Relationships tracked automatically (Kael-Finn friendship)
3. ✅ World timeline populated with major events
4. ✅ Character aliases handled (if Zephyr revealed as alt name)
5. ✅ All tests passing
6. ✅ 3 chapters regenerated successfully

---

## Expected Results

**Before Phase 4:**
- 5 characters (with 1 duplicate: Unnamed Guard Leader + Guard Leader)

**After Phase 4:**
- 4 characters (duplicate merged)
- 2-3 relationships tracked (Kael-Finn, Kael-Mysterious Figure)
- 3-5 timeline events (arrival, chase, discovery, prophecy)

---

## Notes

- Phase 1-3 are fully functional
- Current system: 9.5/10
- Phase 4 adds: alias tracking, relationships, timeline
- Estimated improvement: 9.5 → 9.8/10

**Priority:** Medium (system already excellent, this is polish)

---

## Questions for Next Session

1. Should faction auto-detection be included? (Sky Empire, Rebels)
2. Should location tracking be enhanced beyond current WorldLocation?
3. Maximum timeline size? (cap at 100 events to prevent bloat?)

---

End of Phase 4 TODO
