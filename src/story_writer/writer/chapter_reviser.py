"""Chapter revision system for quality improvement."""

from typing import List
from ..models import Chapter, ContinuityViolation, QualityReport, RevisionResult
from ..utils import LLMClient, get_style_guide


class ChapterReviser:
    """
    Revises chapters based on continuity violations and quality feedback.

    Uses LLM to fix specific issues while preserving the core story.
    """

    def __init__(self, llm_client: LLMClient):
        """
        Initialize chapter reviser.

        Args:
            llm_client: LLM client for revision generation
        """
        self.client = llm_client
        self.style_guide = get_style_guide()

    def revise_chapter(
        self,
        chapter: Chapter,
        chapter_text: str,
        violations: List[ContinuityViolation],
        quality_report: QualityReport,
        attempt: int = 1
    ) -> RevisionResult:
        """
        Revise chapter based on feedback.

        Args:
            chapter: Chapter metadata
            chapter_text: Original chapter text
            violations: Continuity violations to fix
            quality_report: Quality assessment
            attempt: Revision attempt number (1 or 2)

        Returns:
            RevisionResult with revised text and notes
        """
        print(f"\n[REVISER] Revising chapter {chapter.chapter_number} (attempt {attempt})...")

        # Build revision context
        feedback = self._build_feedback_summary(violations, quality_report)

        # Generate revised chapter
        prompt = self._create_revision_prompt(chapter, chapter_text, feedback)
        system_prompt = self._create_system_prompt()

        print(f"[REVISER] Generating revised version...")
        revised_text = self.client.generate(
            prompt=prompt,
            system_prompt=system_prompt,
            temperature=0.75  # Slightly creative but focused
        )

        # Create revision notes
        notes = self._create_revision_notes(violations, quality_report, attempt)

        # Determine what was fixed
        violations_fixed = [
            v.description for v in violations
            if v.severity in ["critical", "major"]
        ]

        result = RevisionResult(
            revised_text=revised_text,
            revision_notes=notes,
            violations_fixed=violations_fixed,
            quality_improved=True  # Assume improvement; will be verified
        )

        print(f"[OK] Revision complete")
        print(f"    - Addressed: {len(violations_fixed)} violation(s)")
        print(f"    - Focus: {len(quality_report.suggestions)} quality improvement(s)")

        return result

    def _build_feedback_summary(
        self,
        violations: List[ContinuityViolation],
        quality_report: QualityReport
    ) -> dict:
        """Build structured feedback for revision."""
        feedback = {
            "continuity_issues": [],
            "quality_suggestions": quality_report.suggestions[:3],
            "preserve_strengths": quality_report.strengths[:2]
        }

        # Focus on critical and major violations
        for v in violations:
            if v.severity in ["critical", "major"]:
                feedback["continuity_issues"].append({
                    "type": v.type,
                    "issue": v.description,
                    "fix": v.suggested_fix
                })

        return feedback

    def _create_system_prompt(self) -> str:
        """Create system prompt for revision."""
        themes = ", ".join(self.style_guide["themes"])

        return f"""You are a skilled manga chapter editor specializing in Eiichiro Oda's style (One Piece).

Your role is to revise chapters while:
- Fixing continuity errors and inconsistencies
- Improving quality based on specific feedback
- PRESERVING the core story, characters, and plot progression
- MAINTAINING the Oda-style optimistic adventure tone
- KEEPING successful elements intact

Core themes: {themes}

Make targeted improvements, not wholesale rewrites.
Return the complete revised chapter text."""

    def _create_revision_prompt(
        self,
        chapter: Chapter,
        chapter_text: str,
        feedback: dict
    ) -> str:
        """Create the revision prompt."""
        prompt = f"""Revise this manga chapter based on specific feedback.

CHAPTER INFO:
Title: {chapter.title}
Number: {chapter.chapter_number}

ORIGINAL TEXT:
{chapter_text}

---

REVISION REQUIREMENTS:

"""

        # Add continuity issues if any
        if feedback["continuity_issues"]:
            prompt += "**CONTINUITY ISSUES TO FIX:**\n"
            for i, issue in enumerate(feedback["continuity_issues"], 1):
                prompt += f"{i}. {issue['issue']}\n"
                prompt += f"   Fix: {issue['fix']}\n\n"

        # Add quality suggestions
        if feedback["quality_suggestions"]:
            prompt += "**QUALITY IMPROVEMENTS:**\n"
            for i, suggestion in enumerate(feedback["quality_suggestions"], 1):
                prompt += f"{i}. {suggestion}\n"
            prompt += "\n"

        # Note strengths to preserve
        if feedback["preserve_strengths"]:
            prompt += "**PRESERVE THESE STRENGTHS:**\n"
            for strength in feedback["preserve_strengths"]:
                prompt += f"- {strength}\n"
            prompt += "\n"

        prompt += """**GUIDELINES:**
- Make TARGETED fixes, not a complete rewrite
- Keep the core plot, characters, and story progression
- Maintain Oda-style elements: optimism, mystery, adventure
- Ensure natural dialogue and authentic character voices
- Preserve the cliffhanger ending
- Keep the chapter length similar (1200-1800 words)

Return the complete revised chapter in the same markdown format as the original."""

        return prompt

    def _create_revision_notes(
        self,
        violations: List[ContinuityViolation],
        quality_report: QualityReport,
        attempt: int
    ) -> str:
        """Create human-readable revision notes."""
        notes = f"Revision Attempt {attempt}\n\n"

        if violations:
            notes += f"Continuity fixes ({len(violations)}):\n"
            for v in violations:
                if v.severity in ["critical", "major"]:
                    notes += f"  - [{v.severity.upper()}] {v.description}\n"
            notes += "\n"

        if quality_report.suggestions:
            notes += f"Quality improvements:\n"
            for suggestion in quality_report.suggestions[:3]:
                notes += f"  - {suggestion}\n"
            notes += "\n"

        notes += f"Original quality score: {quality_report.overall_score}/100\n"

        return notes
