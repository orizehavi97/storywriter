"""Chapter writing using LLM."""

from datetime import datetime

from ..models import StoryMemory, ChapterOutline, Chapter
from ..utils import LLMClient, get_style_guide


class ChapterWriter:
    """Writes full chapters from outlines using LLM."""

    def __init__(self, llm_client: LLMClient):
        """
        Initialize chapter writer.

        Args:
            llm_client: LLM client for generation
        """
        self.client = llm_client
        self.style_guide = get_style_guide()

    def write_chapter(
        self,
        outline: ChapterOutline,
        memory: StoryMemory
    ) -> Chapter:
        """
        Write a full chapter from an outline.

        Args:
            outline: Chapter outline to expand
            memory: Current story memory for context

        Returns:
            Complete Chapter with full text
        """
        print(f"\n[WRITER] Writing Chapter {outline.chapter_number}: {outline.title}")

        # Build context
        context = self._build_writing_context(memory, outline)

        # Generate chapter text
        prompt = self._create_writing_prompt(outline, context)
        system_prompt = self._create_system_prompt()

        print(f"[WRITER] Generating chapter text with LLM...")
        print(f"         (Target: {outline.expected_word_count} words)")

        content = self.client.generate(
            prompt=prompt,
            system_prompt=system_prompt,
            temperature=0.9,  # More creative for writing
            max_tokens=4096
        )

        # Count words
        word_count = len(content.split())

        print(f"[OK] Chapter written - {word_count} words")

        # Create Chapter object
        chapter_id = f"ch_{outline.chapter_number:03d}"

        chapter = Chapter(
            chapter_id=chapter_id,
            chapter_number=outline.chapter_number,
            arc_id=outline.arc_id,
            title=outline.title,
            content=content,
            word_count=word_count,
            summary=outline.summary,
            key_events=outline.key_events,
            characters_present=self._extract_characters_from_scenes(outline.scenes),
            locations=self._extract_locations_from_scenes(outline.scenes),
            cliffhanger=outline.cliffhanger,
            cliffhanger_type=outline.cliffhanger_type,
            themes=outline.themes_present,
            tone="balanced",
            outline=outline,
            created_at=datetime.now(),
            state_changes={}  # Will be populated by state updater
        )

        return chapter

    def _build_writing_context(
        self,
        memory: StoryMemory,
        outline: ChapterOutline
    ) -> dict:
        """Build context for writing prompt."""
        context = {
            "story_title": memory.story_title,
            "world_name": memory.world_name,
        }

        # Get character details for characters in this chapter
        character_names = set()
        for scene in outline.scenes:
            character_names.update(scene.get("characters", []))

        character_details = []
        for name in character_names:
            # Find character by name
            for char in memory.characters.values():
                if char.name == name:
                    character_details.append({
                        "name": char.name,
                        "personality": char.personality,
                        "speech_pattern": char.speech_pattern,
                        "quirks": char.quirks
                    })
                    break

        context["characters"] = character_details

        # Recent chapter for continuity
        recent_chapters = memory.get_recent_chapters(n=1)
        if recent_chapters and recent_chapters[0].chapter_number < outline.chapter_number:
            last_ch = recent_chapters[0]
            context["previous_chapter"] = {
                "title": last_ch.title,
                "summary": last_ch.summary,
                "ended_with": last_ch.cliffhanger
            }

        return context

    def _create_system_prompt(self) -> str:
        """Create system prompt for chapter writing."""
        chapter_structure = self.style_guide["chapter"]

        return f"""You are a master manga storyteller in the style of Eiichiro Oda (One Piece).

Your writing style:
- Vivid, cinematic descriptions that feel like manga panels
- Character-driven dialogue that reveals personality
- Balance action, emotion, and humor
- Build tension and release it strategically
- Rich sensory details (sights, sounds, smells)
- Creative metaphors and imagery
- Pacing: Mix of fast action and slower character moments

Target length: ~{chapter_structure['target_word_count']} words

Write in present tense, third person.
Make every scene visual and emotionally engaging.
End with the specified cliffhanger."""

    def _create_writing_prompt(self, outline: ChapterOutline, context: dict) -> str:
        """Create the writing prompt."""
        prompt = f"""Write Chapter {outline.chapter_number}: {outline.title}

STORY: {context['story_title']} - {context['world_name']}

CHAPTER SUMMARY:
{outline.summary}

"""

        # Previous chapter context
        if "previous_chapter" in context:
            prev = context["previous_chapter"]
            prompt += f"""PREVIOUS CHAPTER:
"{prev['title']}" ended with: {prev['ended_with']}
Continue naturally from this point.

"""

        # Character details
        if context.get("characters"):
            prompt += "CHARACTER DETAILS:\n"
            for char in context["characters"]:
                prompt += f"- {char['name']}: {char['personality']}\n"
                if char.get("speech_pattern"):
                    prompt += f"  Speech: {char['speech_pattern']}\n"
                if char.get("quirks"):
                    prompt += f"  Quirks: {', '.join(char['quirks'])}\n"
            prompt += "\n"

        # Scene breakdown
        prompt += "SCENE STRUCTURE:\n"
        for i, scene in enumerate(outline.scenes, 1):
            prompt += f"\nScene {i}: {scene.get('location', 'Unknown')}\n"
            prompt += f"Purpose: {scene.get('purpose', 'Advance plot')}\n"
            prompt += f"Tone: {scene.get('tone', 'balanced')}\n"
            if scene.get("characters"):
                prompt += f"Characters: {', '.join(scene['characters'])}\n"
        prompt += "\n"

        # Key events to include
        prompt += "KEY EVENTS TO INCLUDE:\n"
        for event in outline.key_events:
            prompt += f"- {event}\n"
        prompt += "\n"

        # Character moments
        if outline.character_moments:
            prompt += "CHARACTER DEVELOPMENT MOMENTS:\n"
            for char, moment in outline.character_moments.items():
                prompt += f"- {char}: {moment}\n"
            prompt += "\n"

        # Themes
        if outline.themes_present:
            prompt += f"THEMES TO WEAVE IN: {', '.join(outline.themes_present)}\n\n"

        # Foreshadowing
        if outline.foreshadowing:
            prompt += "FORESHADOWING (subtle hints):\n"
            for hint in outline.foreshadowing:
                prompt += f"- {hint}\n"
            prompt += "\n"

        # Cliffhanger
        prompt += f"""ENDING:
Must end with this cliffhanger ({outline.cliffhanger_type}):
{outline.cliffhanger}

---

Now write the full chapter. Make it vivid, emotional, and engaging.
Show don't tell. Use dialogue to reveal character.
Create visual moments that would work as manga panels.

Begin the chapter now:"""

        return prompt

    def _extract_characters_from_scenes(self, scenes: list[dict]) -> list[str]:
        """Extract unique character names from scenes."""
        characters = set()
        for scene in scenes:
            characters.update(scene.get("characters", []))
        return list(characters)

    def _extract_locations_from_scenes(self, scenes: list[dict]) -> list[str]:
        """Extract unique locations from scenes."""
        locations = set()
        for scene in scenes:
            loc = scene.get("location")
            if loc:
                locations.add(loc)
        return list(locations)
