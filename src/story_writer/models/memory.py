"""Main story memory model."""

from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field

from .chapter import Chapter
from .arc import Arc
from .character import Character
from .world import WorldLocation, Faction, Artifact
from .thread import PlotThread


class StoryMemory(BaseModel):
    """Complete story state and memory."""

    # Meta
    story_title: str
    world_name: str
    created_at: datetime = Field(default_factory=datetime.now)
    last_updated: datetime = Field(default_factory=datetime.now)

    # Current state
    current_chapter_number: int = Field(default=0)
    current_arc_id: Optional[str] = None

    # Entities
    characters: dict[str, Character] = Field(
        default_factory=dict,
        description="Character ID -> Character"
    )

    locations: dict[str, WorldLocation] = Field(
        default_factory=dict,
        description="Location ID -> WorldLocation"
    )

    factions: dict[str, Faction] = Field(
        default_factory=dict,
        description="Faction ID -> Faction"
    )

    artifacts: dict[str, Artifact] = Field(
        default_factory=dict,
        description="Artifact ID -> Artifact"
    )

    # Story structure
    arcs: dict[str, Arc] = Field(
        default_factory=dict,
        description="Arc ID -> Arc"
    )

    chapters: dict[str, Chapter] = Field(
        default_factory=dict,
        description="Chapter ID -> Chapter"
    )

    plot_threads: dict[str, PlotThread] = Field(
        default_factory=dict,
        description="Thread ID -> PlotThread"
    )

    # Open threads by status
    @property
    def open_threads(self) -> list[PlotThread]:
        """Get all open plot threads."""
        return [
            thread for thread in self.plot_threads.values()
            if thread.status in ["open", "progressing"]
        ]

    @property
    def major_open_threads(self) -> list[PlotThread]:
        """Get major open plot threads."""
        return [
            thread for thread in self.open_threads
            if thread.importance == "major"
        ]

    # Saga-level info
    saga_goal: str = Field(
        default="",
        description="Ultimate destination of the story"
    )
    saga_milestones: list[str] = Field(
        default_factory=list,
        description="Major milestones toward the saga goal"
    )

    # Meta tracking
    arc_type_history: list[str] = Field(
        default_factory=list,
        description="History of arc types for variety"
    )
    theme_counts: dict[str, int] = Field(
        default_factory=dict,
        description="Theme -> count for balance"
    )

    # World state
    world_history_log: list[dict] = Field(
        default_factory=list,
        description="Major world events: {chapter_id, event}"
    )

    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }

    def get_character(self, char_id: str) -> Optional[Character]:
        """Get character by ID."""
        return self.characters.get(char_id)

    def get_location(self, loc_id: str) -> Optional[WorldLocation]:
        """Get location by ID."""
        return self.locations.get(loc_id)

    def get_current_arc(self) -> Optional[Arc]:
        """Get the current arc."""
        if self.current_arc_id:
            return self.arcs.get(self.current_arc_id)
        return None

    def get_recent_chapters(self, n: int = 3) -> list[Chapter]:
        """Get the N most recent chapters."""
        sorted_chapters = sorted(
            self.chapters.values(),
            key=lambda ch: ch.chapter_number,
            reverse=True
        )
        return sorted_chapters[:n]
