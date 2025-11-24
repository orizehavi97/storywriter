"""Data models for Phase 4 state tracking."""

from typing import List, Optional
from datetime import datetime
from pydantic import BaseModel, Field


class CharacterAlias(BaseModel):
    """Character alias tracking for deduplication."""

    character_id: str = Field(description="Primary character ID")
    primary_name: str = Field(description="Primary character name")
    aliases: List[str] = Field(
        default_factory=list,
        description="Alternative names/titles (e.g., ['Mysterious Figure', 'Zephyr'])"
    )


class Relationship(BaseModel):
    """Character relationship tracking."""

    character_a: str = Field(description="First character ID")
    character_b: str = Field(description="Second character ID")
    relationship_type: str = Field(
        description="ally, friend, rival, enemy, mentor, family, romantic, neutral"
    )
    strength: int = Field(
        ge=0,
        le=100,
        default=50,
        description="Relationship strength/depth (0-100)"
    )
    established_chapter: str = Field(
        description="Chapter where relationship was established"
    )
    last_updated: str = Field(
        description="Chapter where relationship was last updated"
    )
    notes: str = Field(
        default="",
        description="Additional context about the relationship"
    )


class WorldEvent(BaseModel):
    """Major world event tracking for timeline."""

    event_id: str
    chapter_id: str = Field(description="Chapter where event occurred")
    chapter_number: int
    description: str = Field(description="What happened")
    event_type: str = Field(
        description="battle, discovery, death, alliance, betrayal, revelation, destruction"
    )
    characters_involved: List[str] = Field(
        default_factory=list,
        description="Character IDs involved"
    )
    locations_involved: List[str] = Field(
        default_factory=list,
        description="Location names involved"
    )
    factions_involved: List[str] = Field(
        default_factory=list,
        description="Faction IDs involved"
    )
    timestamp: datetime = Field(default_factory=datetime.now)
    impact: str = Field(
        default="minor",
        description="minor, moderate, major, critical"
    )
