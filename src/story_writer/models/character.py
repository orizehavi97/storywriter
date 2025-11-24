"""Character data models."""

from typing import Optional
from pydantic import BaseModel, Field


class Character(BaseModel):
    """Complete character profile."""

    character_id: str = Field(description="Unique identifier")
    name: str

    # Appearance and identity
    age: Optional[int] = None
    appearance: str = Field(default="", description="Physical description")

    # Personality and voice
    personality: str = Field(description="Core personality traits")
    speech_pattern: Optional[str] = None
    quirks: list[str] = Field(default_factory=list)
    running_gags: list[str] = Field(default_factory=list)

    # Motivations
    dream: Optional[str] = None
    ambitions: list[str] = Field(default_factory=list)
    fears: list[str] = Field(default_factory=list)
    flaws: list[str] = Field(default_factory=list)

    # Background
    background: str = Field(default="")
    history: str = Field(default="")

    # Abilities
    abilities: list[str] = Field(default_factory=list)
    fighting_style: Optional[str] = None
    power_level: str = Field(default="unknown")

    # Relationships
    relationships: dict[str, str] = Field(
        default_factory=dict,
        description="Character ID -> relationship description"
    )

    # Status
    status: str = Field(
        default="active",
        description="active, injured, captured, dead, etc."
    )
    current_location: Optional[str] = None

    # Items and possessions
    items: list[str] = Field(default_factory=list)

    # Story tracking
    first_appearance: Optional[str] = None  # Chapter ID
    last_appearance: Optional[str] = None   # Chapter ID
    arc_status: str = Field(
        default="",
        description="Current character arc progress"
    )

    # Role
    role: str = Field(
        default="supporting",
        description="protagonist, antagonist, ally, supporting, etc."
    )
    faction: Optional[str] = None

    # Notes
    notes: str = Field(default="")

    class Config:
        json_schema_extra = {
            "example": {
                "character_id": "char_kael",
                "name": "Kael",
                "age": 17,
                "personality": "Optimistic, reckless, fiercely loyal",
                "dream": "Find his lost homeland",
                "abilities": ["Sky Affinity", "Natural navigator"],
                "status": "active",
                "role": "protagonist"
            }
        }
