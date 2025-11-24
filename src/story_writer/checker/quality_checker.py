"""Quality checking for Oda-style storytelling."""

import json
from typing import Optional
from ..models import Chapter, StoryMemory, QualityReport
from ..utils import LLMClient, get_style_guide


class QualityChecker:
    """
    Checks chapter quality against Oda-style standards.

    Validates soft rules:
    - Oda-style elements (optimism, adventure, mystery)
    - Character voice consistency
    - Pacing and scene structure
    - Cliffhanger quality
    - Foreshadowing and callbacks
    """

    def __init__(self, llm_client: LLMClient):
        """
        Initialize quality checker.

        Args:
            llm_client: LLM client for quality assessment
        """
        self.client = llm_client
        self.style_guide = get_style_guide()

    def check_chapter(
        self,
        chapter: Chapter,
        chapter_text: str,
        memory: StoryMemory
    ) -> QualityReport:
        """
        Assess chapter quality using LLM.

        Args:
            chapter: Chapter metadata
            chapter_text: Full chapter text
            memory: Story memory for context

        Returns:
            QualityReport with scores and suggestions
        """
        print(f"\n[QUALITY] Assessing chapter {chapter.chapter_number}...")

        # Build assessment context
        context = self._build_assessment_context(chapter, memory)

        # Generate quality assessment
        prompt = self._create_assessment_prompt(chapter, chapter_text, context)
        system_prompt = self._create_system_prompt()

        print(f"[QUALITY] Analyzing with LLM...")
        response = self.client.generate(
            prompt=prompt,
            system_prompt=system_prompt,
            temperature=0.3  # Lower temperature for consistent assessment
        )

        # Parse response into QualityReport
        report = self._parse_quality_response(response)

        # Display results
        self._display_report(report)

        return report

    def _build_assessment_context(
        self,
        chapter: Chapter,
        memory: StoryMemory
    ) -> dict:
        """Build context for quality assessment."""
        context = {
            "story_title": memory.story_title,
            "chapter_number": chapter.chapter_number,
            "total_chapters": len(memory.chapters),
        }

        # Get recent chapters for voice consistency check
        recent = memory.get_recent_chapters(n=2)
        if recent:
            context["recent_chapters"] = [
                {
                    "num": ch.chapter_number,
                    "title": ch.title,
                    "cliffhanger_type": ch.cliffhanger_type
                }
                for ch in recent
            ]

        return context

    def _create_system_prompt(self) -> str:
        """Create system prompt for quality assessment."""
        themes = ", ".join(self.style_guide["themes"])

        return f"""You are a manga story quality assessor specializing in Eiichiro Oda's style (One Piece).

Your role is to objectively evaluate chapters against Oda-style standards:
- Optimistic adventure tone with real stakes
- Character-driven storytelling
- Mystery layering and foreshadowing
- Compelling cliffhangers
- World-building through action
- Humor mixed with drama

Core themes: {themes}

Provide detailed, constructive feedback with specific examples.
Return assessment in JSON format."""

    def _create_assessment_prompt(
        self,
        chapter: Chapter,
        chapter_text: str,
        context: dict
    ) -> str:
        """Create the quality assessment prompt."""
        prompt = f"""Assess the quality of this manga chapter against Oda-style standards.

CHAPTER INFO:
Title: {chapter.title}
Number: {chapter.chapter_number} (of {context['total_chapters']} total)
Story: {context['story_title']}

CHAPTER TEXT:
{chapter_text}

---

Evaluate the chapter on these criteria (0-100 scale):

1. **Oda Style Elements** (0-100):
   - Optimistic adventure tone with real stakes?
   - Mystery layering and world intrigue?
   - Balance of action, emotion, humor?
   - Character-driven rather than plot-driven?

2. **Voice Consistency** (0-100):
   - Do characters sound consistent?
   - Is dialogue age-appropriate and authentic?
   - Does narrative voice match the story tone?

3. **Pacing & Structure** (0-100):
   - Do scenes flow naturally?
   - Is there variety in scene length/intensity?
   - Does it build to a satisfying moment?

4. **Story Elements**:
   - Cliffhanger: Present and compelling? (yes/no)
   - Foreshadowing: Any hints at future events? (yes/no)
   - Callbacks: References to past events? (yes/no)

5. **Overall Assessment**:
   - Strengths (2-3 specific examples)
   - Suggestions for improvement (2-3 specific points)
   - Needs revision? (yes if overall < 70)

Return ONLY valid JSON in this format:
{{
  "overall_score": 85,
  "oda_style_score": 90,
  "voice_consistency_score": 85,
  "pacing_score": 80,
  "has_cliffhanger": true,
  "has_foreshadowing": true,
  "has_callbacks": true,
  "strengths": [
    "Specific strength 1 with example",
    "Specific strength 2 with example"
  ],
  "suggestions": [
    "Specific suggestion 1",
    "Specific suggestion 2"
  ],
  "needs_revision": false
}}"""

        return prompt

    def _parse_quality_response(self, response: str) -> QualityReport:
        """Parse LLM response into QualityReport."""
        # Extract JSON from response
        response = response.strip()

        # Remove markdown code blocks if present
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

        # Parse JSON
        try:
            data = json.loads(response)
        except json.JSONDecodeError as e:
            print(f"[ERROR] Failed to parse quality response: {e}")
            print(f"Response was: {response[:500]}...")
            # Return default "needs review" report
            return QualityReport(
                overall_score=50,
                oda_style_score=50,
                voice_consistency_score=50,
                pacing_score=50,
                has_cliffhanger=False,
                has_foreshadowing=False,
                has_callbacks=False,
                strengths=["Could not assess - parsing error"],
                suggestions=["Manual review required"],
                needs_revision=True
            )

        # Create QualityReport
        report = QualityReport(
            overall_score=data.get("overall_score", 50),
            oda_style_score=data.get("oda_style_score", 50),
            voice_consistency_score=data.get("voice_consistency_score", 50),
            pacing_score=data.get("pacing_score", 50),
            has_cliffhanger=data.get("has_cliffhanger", False),
            has_foreshadowing=data.get("has_foreshadowing", False),
            has_callbacks=data.get("has_callbacks", False),
            strengths=data.get("strengths", []),
            suggestions=data.get("suggestions", []),
            needs_revision=data.get("needs_revision", False)
        )

        return report

    def _display_report(self, report: QualityReport):
        """Display quality report to console."""
        print(f"\n[QUALITY] Assessment Results:")
        print(f"    Overall Score: {report.overall_score}/100")
        print(f"    - Oda Style: {report.oda_style_score}/100")
        print(f"    - Voice: {report.voice_consistency_score}/100")
        print(f"    - Pacing: {report.pacing_score}/100")
        print(f"    Story Elements:")
        print(f"      - Cliffhanger: {'Yes' if report.has_cliffhanger else 'No'}")
        print(f"      - Foreshadowing: {'Yes' if report.has_foreshadowing else 'No'}")
        print(f"      - Callbacks: {'Yes' if report.has_callbacks else 'No'}")

        if report.strengths:
            print(f"    Strengths:")
            for strength in report.strengths[:3]:
                print(f"      + {strength}")

        if report.suggestions:
            print(f"    Suggestions:")
            for suggestion in report.suggestions[:3]:
                print(f"      - {suggestion}")

        if report.needs_revision:
            print(f"[WARN] Chapter may benefit from revision (score < 70)")
        else:
            print(f"[OK] Quality assessment passed")
