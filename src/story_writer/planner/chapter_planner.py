"""Chapter planning using LLM."""

import json
from typing import Optional

from ..models import StoryMemory, ChapterOutline, Arc
from ..utils import LLMClient, get_style_guide


class ChapterPlanner:
    """Plans chapter outlines using LLM."""

    def __init__(self, llm_client: LLMClient):
        """
        Initialize chapter planner.

        Args:
            llm_client: LLM client for generation
        """
        self.client = llm_client
        self.style_guide = get_style_guide()

    def plan_chapter(
        self,
        memory: StoryMemory,
        arc: Optional[Arc] = None
    ) -> ChapterOutline:
        """
        Plan the next chapter.

        Args:
            memory: Current story memory
            arc: Current arc (optional)

        Returns:
            ChapterOutline with structured plan
        """
        next_chapter_num = memory.current_chapter_number + 1

        print(f"\n[PLANNER] Planning Chapter {next_chapter_num}...")

        # Build context
        context = self._build_planning_context(memory, arc)

        # Generate outline
        prompt = self._create_planning_prompt(context, next_chapter_num)
        system_prompt = self._create_system_prompt()

        print(f"[PLANNER] Generating outline with LLM...")
        response = self.client.generate(
            prompt=prompt,
            system_prompt=system_prompt,
            temperature=0.7  # Slightly structured for planning
        )

        # Parse response into ChapterOutline
        outline = self._parse_outline_response(response, next_chapter_num, arc)

        print(f"[OK] Chapter outline created")
        print(f"    - Title: {outline.title}")
        print(f"    - Scenes: {len(outline.scenes)}")
        print(f"    - Cliffhanger: {outline.cliffhanger_type}")

        return outline

    def _build_planning_context(
        self,
        memory: StoryMemory,
        arc: Optional[Arc]
    ) -> dict:
        """Build context for planning prompt."""
        context = {
            "story_title": memory.story_title,
            "world_name": memory.world_name,
            "current_chapter": memory.current_chapter_number,
            "saga_goal": memory.saga_goal,
        }

        # Recent chapters summary
        recent_chapters = memory.get_recent_chapters(n=3)
        if recent_chapters:
            context["recent_chapters"] = [
                {
                    "num": ch.chapter_number,
                    "title": ch.title,
                    "summary": ch.summary,
                    "cliffhanger": ch.cliffhanger
                }
                for ch in recent_chapters
            ]

        # Current arc info
        if arc:
            context["arc"] = {
                "name": arc.name,
                "type": arc.arc_type,
                "phase": arc.current_phase,
                "conflict": arc.central_conflict,
                "location": arc.primary_location
            }

        # Active characters
        active_chars = [
            {"name": char.name, "role": char.role, "status": char.status}
            for char in memory.characters.values()
            if char.status == "active"
        ]
        context["active_characters"] = active_chars[:10]  # Limit context

        # Open plot threads (major ones)
        major_threads = memory.major_open_threads
        if major_threads:
            context["open_threads"] = [
                {"name": t.name, "type": t.thread_type}
                for t in major_threads[:5]
            ]

        return context

    def _create_system_prompt(self) -> str:
        """Create system prompt for chapter planning."""
        themes = ", ".join(self.style_guide["themes"])

        return f"""You are a master manga story planner in the style of Eiichiro Oda (One Piece).

Your role is to create detailed chapter outlines that:
- Advance the plot while maintaining excitement
- Develop characters through actions and dialogue
- Balance action, emotion, and mystery
- Include foreshadowing and callbacks
- End with a compelling cliffhanger

Core themes to weave in: {themes}

Tone: Optimistic adventure with real stakes, humor mixed with drama.

Generate a structured chapter outline in JSON format."""

    def _create_planning_prompt(self, context: dict, chapter_num: int) -> str:
        """Create the planning prompt."""
        prompt = f"""Plan Chapter {chapter_num} of "{context['story_title']}"

STORY CONTEXT:
World: {context['world_name']}
Current Chapter: {context['current_chapter']}
Saga Goal: {context.get('saga_goal', 'Ongoing adventure')}

"""

        # Add recent chapters
        if "recent_chapters" in context:
            prompt += "RECENT CHAPTERS:\n"
            for ch in context["recent_chapters"]:
                prompt += f"- Ch {ch['num']}: {ch['title']}\n  {ch['summary']}\n  Ended with: {ch['cliffhanger']}\n"
            prompt += "\n"

        # Add arc info
        if "arc" in context:
            arc = context["arc"]
            prompt += f"""CURRENT ARC: {arc['name']} ({arc['type']})
Phase: {arc['phase']}
Conflict: {arc['conflict']}
Location: {arc['location']}

"""

        # Add characters
        if context.get("active_characters"):
            prompt += "ACTIVE CHARACTERS:\n"
            for char in context["active_characters"][:5]:
                prompt += f"- {char['name']} ({char['role']})\n"
            prompt += "\n"

        # Add threads
        if context.get("open_threads"):
            prompt += "OPEN PLOT THREADS:\n"
            for thread in context["open_threads"]:
                prompt += f"- {thread['name']} ({thread['type']})\n"
            prompt += "\n"

        # Instructions
        prompt += """Create a chapter outline with:
1. A compelling title
2. 3-5 scenes with: location, characters present, purpose, tone
3. Key events that occur
4. Character development moments
5. Thematic elements
6. Foreshadowing elements
7. A MANDATORY cliffhanger ending

Return ONLY valid JSON in this exact format:
{
  "title": "Chapter Title",
  "summary": "Brief chapter summary",
  "scenes": [
    {
      "location": "Location name",
      "characters": ["Character names"],
      "purpose": "What this scene accomplishes",
      "tone": "emotional tone"
    }
  ],
  "key_events": ["Event 1", "Event 2"],
  "character_moments": {
    "Character Name": "Development moment"
  },
  "cliffhanger": "How it ends",
  "cliffhanger_type": "revelation/danger/mystery/character_arrival/emotional_peak/twist",
  "themes_present": ["theme1", "theme2"],
  "foreshadowing": ["Hint at future event"]
}"""

        return prompt

    def _parse_outline_response(
        self,
        response: str,
        chapter_num: int,
        arc: Optional[Arc]
    ) -> ChapterOutline:
        """Parse LLM response into ChapterOutline."""
        # Extract JSON from response (might have markdown code blocks)
        response = response.strip()

        # Remove markdown code blocks if present
        if response.startswith("```"):
            lines = response.split("\n")
            # Find first and last ``` and extract content between
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

        # Parse JSON
        try:
            data = json.loads(response)
        except json.JSONDecodeError as e:
            print(f"[ERROR] Failed to parse JSON response: {e}")
            print(f"Response was: {response[:500]}...")
            raise

        # Create ChapterOutline
        arc_id = arc.arc_id if arc else "default_arc"

        outline = ChapterOutline(
            chapter_number=chapter_num,
            arc_id=arc_id,
            title=data.get("title", f"Chapter {chapter_num}"),
            summary=data.get("summary", ""),
            scenes=data.get("scenes", []),
            key_events=data.get("key_events", []),
            character_moments=data.get("character_moments", {}),
            cliffhanger=data.get("cliffhanger", "To be continued..."),
            cliffhanger_type=data.get("cliffhanger_type", "mystery"),
            themes_present=data.get("themes_present", []),
            foreshadowing=data.get("foreshadowing", []),
            expected_word_count=1500
        )

        return outline
