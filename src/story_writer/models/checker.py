"""Data models for quality control and continuity checking."""

from typing import List
from pydantic import BaseModel, Field


class ContinuityViolation(BaseModel):
    """Represents a continuity error in the story."""

    type: str = Field(
        description="Type of violation: character_status, possession, location, timeline"
    )
    severity: str = Field(
        description="Severity: critical, major, minor"
    )
    description: str = Field(
        description="Human-readable description of the violation"
    )
    chapter_reference: str = Field(
        description="Which chapter this relates to"
    )
    conflicting_info: str = Field(
        default="",
        description="What contradicts this"
    )
    suggested_fix: str = Field(
        description="How to fix this violation"
    )


class QualityReport(BaseModel):
    """Quality assessment report for a chapter."""

    overall_score: int = Field(
        ge=0,
        le=100,
        description="Overall quality score 0-100"
    )
    oda_style_score: int = Field(
        ge=0,
        le=100,
        description="How well it matches Oda's style"
    )
    voice_consistency_score: int = Field(
        ge=0,
        le=100,
        description="Character voice consistency"
    )
    pacing_score: int = Field(
        ge=0,
        le=100,
        description="Pacing and scene structure"
    )
    has_cliffhanger: bool = Field(
        description="Does it end with a cliffhanger?"
    )
    has_foreshadowing: bool = Field(
        description="Contains foreshadowing elements?"
    )
    has_callbacks: bool = Field(
        description="References past events?"
    )
    strengths: List[str] = Field(
        default_factory=list,
        description="What's working well"
    )
    suggestions: List[str] = Field(
        default_factory=list,
        description="Areas for improvement"
    )
    needs_revision: bool = Field(
        description="Should this be revised?"
    )


class RevisionResult(BaseModel):
    """Result of a chapter revision attempt."""

    revised_text: str = Field(
        description="The revised chapter text"
    )
    revision_notes: str = Field(
        description="What was changed and why"
    )
    violations_fixed: List[str] = Field(
        default_factory=list,
        description="Which violations were addressed"
    )
    quality_improved: bool = Field(
        description="Did quality score improve?"
    )
