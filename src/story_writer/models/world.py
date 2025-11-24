"""World and location data models."""

from typing import Optional
from pydantic import BaseModel, Field


class WorldLocation(BaseModel):
    """A location in the story world."""

    location_id: str = Field(description="Unique identifier")
    name: str

    # Description
    description: str
    geography: str = Field(default="")
    climate: str = Field(default="")

    # Culture and politics
    culture: str = Field(default="")
    government: str = Field(default="")
    ruler: Optional[str] = None
    population: Optional[str] = None

    # Economy
    economy: str = Field(default="")
    resources: list[str] = Field(default_factory=list)
    trade_goods: list[str] = Field(default_factory=list)

    # History and lore
    history: str = Field(default="")
    myths: list[str] = Field(default_factory=list)
    symbols: list[str] = Field(default_factory=list)

    # Status
    status: str = Field(
        default="active",
        description="active, destroyed, inaccessible, etc."
    )

    # Connections
    connected_to: list[str] = Field(
        default_factory=list,
        description="Connected location IDs"
    )

    # Factions present
    factions: list[str] = Field(default_factory=list)

    # Story relevance
    first_appearance: Optional[str] = None  # Chapter ID
    importance: str = Field(
        default="minor",
        description="major, minor, background"
    )

    # Notes
    notes: str = Field(default="")


class Faction(BaseModel):
    """An organization or group in the world."""

    faction_id: str
    name: str

    # Identity
    description: str
    alignment: str = Field(
        description="protagonist, antagonist, neutral, etc."
    )

    # Structure
    leader: Optional[str] = None  # Character ID
    members: list[str] = Field(
        default_factory=list,
        description="Known member character IDs"
    )
    size: str = Field(default="unknown")

    # Goals and ideology
    goals: list[str] = Field(default_factory=list)
    ideology: str = Field(default="")
    methods: str = Field(default="")

    # Power and influence
    power_level: str = Field(default="medium")
    territory: list[str] = Field(
        default_factory=list,
        description="Location IDs controlled"
    )
    resources: list[str] = Field(default_factory=list)

    # Relationships
    allies: list[str] = Field(
        default_factory=list,
        description="Allied faction IDs"
    )
    enemies: list[str] = Field(
        default_factory=list,
        description="Enemy faction IDs"
    )

    # Status
    status: str = Field(default="active")

    # Story tracking
    first_appearance: Optional[str] = None

    notes: str = Field(default="")


class Artifact(BaseModel):
    """A significant item in the world."""

    artifact_id: str
    name: str

    description: str
    appearance: str = Field(default="")

    # Properties
    powers: list[str] = Field(default_factory=list)
    limitations: list[str] = Field(default_factory=list)

    # History
    origin: str = Field(default="")
    history: str = Field(default="")

    # Status
    current_owner: Optional[str] = None  # Character ID
    location: Optional[str] = None  # Location ID or "unknown"
    status: str = Field(
        default="unknown",
        description="possessed, lost, destroyed, etc."
    )

    # Story tracking
    first_mentioned: Optional[str] = None  # Chapter ID
    importance: str = Field(default="minor")

    notes: str = Field(default="")
