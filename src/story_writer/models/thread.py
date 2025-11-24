"""Plot thread data models."""

from typing import Optional
from pydantic import BaseModel, Field


class PlotThread(BaseModel):
    """An ongoing plot thread (mystery, prophecy, promise, etc.)."""

    thread_id: str = Field(description="Unique identifier")
    name: str

    thread_type: str = Field(
        description="mystery, prophecy, promise, quest, danger, rivalry, romance, etc."
    )

    # Setup
    setup_chapter: str = Field(description="Chapter ID where thread began")
    setup_description: str = Field(description="How the thread was introduced")

    # Status
    status: str = Field(
        default="open",
        description="open, progressing, resolved, abandoned"
    )

    # Priority and timing
    importance: str = Field(
        default="medium",
        description="major, medium, minor"
    )
    expected_resolution: str = Field(
        default="medium_term",
        description="short_term (1-3 chapters), medium_term (4-10), long_term (10+)"
    )

    # Progression
    developments: list[dict] = Field(
        default_factory=list,
        description="List of {chapter_id, description} tracking progress"
    )

    # Resolution
    resolution_chapter: Optional[str] = None
    resolution_description: Optional[str] = None

    # Possible resolutions
    potential_resolutions: list[str] = Field(
        default_factory=list,
        description="Possible ways this thread could resolve"
    )

    # Connected entities
    characters_involved: list[str] = Field(
        default_factory=list,
        description="Character IDs involved in this thread"
    )
    locations_involved: list[str] = Field(
        default_factory=list,
        description="Location IDs involved"
    )

    # Narrative function
    themes: list[str] = Field(
        default_factory=list,
        description="Themes this thread explores"
    )

    # Notes
    notes: str = Field(default="")
    payoff_ideas: list[str] = Field(
        default_factory=list,
        description="Ideas for satisfying resolution"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "thread_id": "thread_001",
                "name": "What happened to Kael's homeland?",
                "thread_type": "mystery",
                "setup_chapter": "ch_001",
                "importance": "major",
                "expected_resolution": "long_term"
            }
        }
