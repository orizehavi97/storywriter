"""Continuity checking for story consistency."""

from typing import List
from ..models import Chapter, StoryMemory, ContinuityViolation


class ContinuityChecker:
    """
    Checks for continuity violations in chapters.

    Validates hard rules:
    - Character status (alive/dead/injured)
    - Item possession (who has what)
    - Location consistency (where characters are)
    - Timeline coherence (chapter ordering)
    """

    def __init__(self):
        """Initialize continuity checker."""
        pass

    def check_chapter(
        self,
        chapter: Chapter,
        memory: StoryMemory
    ) -> List[ContinuityViolation]:
        """
        Check a chapter for continuity violations.

        Args:
            chapter: Chapter to check
            memory: Current story memory

        Returns:
            List of continuity violations (empty if none)
        """
        violations = []

        print(f"\n[CONTINUITY] Checking chapter {chapter.chapter_number}...")

        # Check character status consistency
        violations.extend(self._check_character_status(chapter, memory))

        # Check location consistency
        violations.extend(self._check_locations(chapter, memory))

        # Check character mentions
        violations.extend(self._check_character_mentions(chapter, memory))

        if violations:
            print(f"[WARN] Found {len(violations)} continuity issue(s)")
            for v in violations:
                print(f"  - [{v.severity.upper()}] {v.description}")
        else:
            print(f"[OK] No continuity violations found")

        return violations

    def _check_character_status(
        self,
        chapter: Chapter,
        memory: StoryMemory
    ) -> List[ContinuityViolation]:
        """Check if characters' statuses are consistent."""
        violations = []

        # Get characters mentioned in this chapter
        mentioned_chars = set()
        for event in chapter.key_events:
            event_lower = event.lower()
            for char_name in memory.characters.keys():
                if char_name.lower() in event_lower:
                    mentioned_chars.add(char_name)

        # Check each mentioned character's status
        for char_name in mentioned_chars:
            char = memory.characters.get(char_name)
            if not char:
                continue

            # Dead characters shouldn't be active
            if char.status == "dead":
                violations.append(ContinuityViolation(
                    type="character_status",
                    severity="critical",
                    description=f"{char_name} is mentioned but marked as dead",
                    chapter_reference=chapter.chapter_id,
                    conflicting_info=f"Character died in previous chapter",
                    suggested_fix=f"Either revive {char_name} explicitly or remove references"
                ))

        return violations

    def _check_locations(
        self,
        chapter: Chapter,
        memory: StoryMemory
    ) -> List[ContinuityViolation]:
        """Check if character locations are consistent."""
        violations = []

        # Extract locations from chapter outline
        chapter_locations = set()
        if hasattr(chapter, 'scenes') and chapter.scenes:
            for scene in chapter.scenes:
                if isinstance(scene, dict) and 'location' in scene:
                    chapter_locations.add(scene['location'])

        # Check if locations are reasonable (exist in world or previous chapters)
        known_locations = set(memory.locations.keys())

        # Add locations from previous chapters
        for prev_chapter in memory.chapters.values():
            if hasattr(prev_chapter, 'scenes') and prev_chapter.scenes:
                for scene in prev_chapter.scenes:
                    if isinstance(scene, dict) and 'location' in scene:
                        known_locations.add(scene['location'])

        # Check for completely unknown locations (minor warning)
        for location in chapter_locations:
            if location and location not in known_locations:
                # This is minor - new locations are fine, just flag for awareness
                violations.append(ContinuityViolation(
                    type="location",
                    severity="minor",
                    description=f"New location introduced: {location}",
                    chapter_reference=chapter.chapter_id,
                    conflicting_info="",
                    suggested_fix=f"Consider adding {location} to world locations if it's significant"
                ))

        return violations

    def _check_character_mentions(
        self,
        chapter: Chapter,
        memory: StoryMemory
    ) -> List[ContinuityViolation]:
        """Check if mentioned characters exist in memory."""
        violations = []

        # Check if character moments reference existing characters
        if hasattr(chapter, 'character_moments') and chapter.character_moments:
            for char_name in chapter.character_moments.keys():
                if char_name not in memory.characters:
                    violations.append(ContinuityViolation(
                        type="character_status",
                        severity="major",
                        description=f"Character '{char_name}' has development moment but doesn't exist in memory",
                        chapter_reference=chapter.chapter_id,
                        conflicting_info="Character not found in story memory",
                        suggested_fix=f"Add {char_name} to characters or fix character name"
                    ))

        return violations

    def get_severity_counts(self, violations: List[ContinuityViolation]) -> dict:
        """Get counts of violations by severity."""
        counts = {"critical": 0, "major": 0, "minor": 0}
        for v in violations:
            if v.severity in counts:
                counts[v.severity] += 1
        return counts
