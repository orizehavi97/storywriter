"""Chapter data models."""

from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field


class ChapterOutline(BaseModel):
    """Structured outline for a chapter before writing."""

    chapter_number: int
    arc_id: str
    title: Optional[str] = None
    summary: str = Field(description="High-level chapter summary")

    scenes: list[dict] = Field(
        description="List of scenes with structure: location, characters, purpose, tone"
    )

    key_events: list[str] = Field(
        default_factory=list,
        description="Major events that occur"
    )

    character_moments: dict[str, str] = Field(
        default_factory=dict,
        description="Character name -> key moment/development"
    )

    cliffhanger: str = Field(description="How the chapter ends")
    cliffhanger_type: str = Field(
        description="Type: revelation, danger, mystery, character_arrival, emotional_peak, twist"
    )

    themes_present: list[str] = Field(
        default_factory=list,
        description="Themes featured in this chapter"
    )

    foreshadowing: list[str] = Field(
        default_factory=list,
        description="Elements that hint at future events"
    )

    expected_word_count: int = Field(default=1500)


class Chapter(BaseModel):
    """Complete chapter with metadata and content."""

    chapter_id: str = Field(description="Unique identifier (e.g., 'ch_001')")
    chapter_number: int
    arc_id: str

    title: str
    content: str = Field(description="Full chapter text")
    word_count: int

    summary: str = Field(description="Brief summary for memory")
    key_events: list[str] = Field(
        default_factory=list,
        description="Important events that occurred"
    )

    characters_present: list[str] = Field(
        default_factory=list,
        description="Character names that appeared"
    )

    locations: list[str] = Field(
        default_factory=list,
        description="Locations featured"
    )

    cliffhanger: str
    cliffhanger_type: str

    themes: list[str] = Field(default_factory=list)
    tone: str = Field(default="balanced")

    outline: Optional[ChapterOutline] = None

    created_at: datetime = Field(default_factory=datetime.now)

    # State changes caused by this chapter
    state_changes: dict = Field(
        default_factory=dict,
        description="Changes to world/character state"
    )

    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }
