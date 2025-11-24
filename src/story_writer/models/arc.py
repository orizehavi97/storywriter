"""Story arc data models."""

from typing import Optional
from pydantic import BaseModel, Field


class Arc(BaseModel):
    """Story arc spanning multiple chapters."""

    arc_id: str = Field(description="Unique identifier (e.g., 'arc_001')")
    arc_number: int
    name: str

    # Arc metadata
    arc_type: str = Field(
        description="heist, rebellion, tournament, rescue, mystery, exploration, etc."
    )
    status: str = Field(
        default="planned",
        description="planned, active, completed"
    )

    # Setting
    primary_location: str
    environment_description: str = Field(default="")

    # Characters
    main_characters: list[str] = Field(
        default_factory=list,
        description="Character IDs of main players"
    )
    antagonists: list[str] = Field(default_factory=list)
    allies: list[str] = Field(default_factory=list)
    new_characters: list[str] = Field(
        default_factory=list,
        description="Characters introduced in this arc"
    )

    # Narrative
    summary: str = Field(description="Arc summary")
    central_conflict: str
    themes: list[str] = Field(default_factory=list)

    # Structure
    expected_chapters: int = Field(default=10)
    current_chapter: int = Field(default=0)

    phases: dict[str, str] = Field(
        default_factory=lambda: {
            "arrival": "Protagonists arrive, setup begins",
            "discovery": "Conflict and stakes are revealed",
            "escalation": "Tension builds, complications arise",
            "climax": "Major confrontation or revelation",
            "resolution": "Arc concludes, threads resolve",
            "departure": "Setup for next arc"
        }
    )
    current_phase: str = Field(default="arrival")

    # Plot threads
    threads_introduced: list[str] = Field(
        default_factory=list,
        description="Plot thread IDs introduced"
    )
    threads_resolved: list[str] = Field(
        default_factory=list,
        description="Plot thread IDs resolved"
    )
    threads_advanced: list[str] = Field(
        default_factory=list,
        description="Plot thread IDs that progress"
    )

    # Factions
    factions_involved: list[str] = Field(default_factory=list)

    # Outcomes
    major_revelations: list[str] = Field(default_factory=list)
    character_growth: dict[str, str] = Field(
        default_factory=dict,
        description="Character ID -> growth description"
    )
    world_changes: list[str] = Field(
        default_factory=list,
        description="Permanent changes to world state"
    )

    # Meta
    notes: str = Field(default="")

    class Config:
        json_schema_extra = {
            "example": {
                "arc_id": "arc_001",
                "arc_number": 1,
                "name": "The Sky Trader's Gambit",
                "arc_type": "mystery",
                "primary_location": "Drift Port",
                "central_conflict": "Uncover the conspiracy behind missing traders",
                "expected_chapters": 8
            }
        }
