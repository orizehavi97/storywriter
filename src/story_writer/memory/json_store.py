"""JSON-based memory storage for story state."""

import json
from datetime import datetime
from pathlib import Path
from typing import Optional

from ..models import StoryMemory


class JSONMemoryStore:
    """Simple JSON file-based storage for story memory."""

    def __init__(self, data_dir: Path = Path("data/memory")):
        """
        Initialize the memory store.

        Args:
            data_dir: Directory for storing memory files
        """
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(parents=True, exist_ok=True)

        self.memory_file = self.data_dir / "story_memory.json"
        self.backup_dir = self.data_dir / "backups"
        self.backup_dir.mkdir(exist_ok=True)

    def save(self, memory: StoryMemory, backup: bool = True) -> None:
        """
        Save story memory to JSON file.

        Args:
            memory: StoryMemory object to save
            backup: Whether to create a backup of existing file
        """
        # Update timestamp
        memory.last_updated = datetime.now()

        # Create backup if file exists
        if backup and self.memory_file.exists():
            self._create_backup()

        # Convert to dict and save
        memory_dict = memory.model_dump(mode='json')

        with open(self.memory_file, 'w', encoding='utf-8') as f:
            json.dump(memory_dict, f, indent=2, ensure_ascii=False)

        print(f"[OK] Saved story memory to {self.memory_file}")

    def load(self) -> Optional[StoryMemory]:
        """
        Load story memory from JSON file.

        Returns:
            StoryMemory object, or None if file doesn't exist
        """
        if not self.memory_file.exists():
            print(f"[INFO] No existing memory file found at {self.memory_file}")
            return None

        with open(self.memory_file, 'r', encoding='utf-8') as f:
            memory_dict = json.load(f)

        memory = StoryMemory.model_validate(memory_dict)
        print(f"[OK] Loaded story memory from {self.memory_file}")
        print(f"    - Story: {memory.story_title}")
        print(f"    - World: {memory.world_name}")
        print(f"    - Chapters: {len(memory.chapters)}")
        print(f"    - Characters: {len(memory.characters)}")
        print(f"    - Current chapter: {memory.current_chapter_number}")

        return memory

    def _create_backup(self) -> None:
        """Create a timestamped backup of the current memory file."""
        if not self.memory_file.exists():
            return

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_file = self.backup_dir / f"story_memory_{timestamp}.json"

        with open(self.memory_file, 'r', encoding='utf-8') as f:
            content = f.read()

        with open(backup_file, 'w', encoding='utf-8') as f:
            f.write(content)

        print(f"[OK] Created backup: {backup_file.name}")

    def exists(self) -> bool:
        """Check if a memory file exists."""
        return self.memory_file.exists()

    def initialize_new_story(
        self,
        story_title: str,
        world_name: str,
        saga_goal: str = ""
    ) -> StoryMemory:
        """
        Initialize a new story memory.

        Args:
            story_title: Title of the story
            world_name: Name of the world
            saga_goal: Ultimate goal of the saga

        Returns:
            New StoryMemory object
        """
        memory = StoryMemory(
            story_title=story_title,
            world_name=world_name,
            saga_goal=saga_goal
        )

        print(f"[OK] Initialized new story: {story_title}")
        print(f"    - World: {world_name}")

        return memory

    def save_chapter_text(self, chapter_id: str, content: str) -> None:
        """
        Save chapter text to a separate markdown file.

        Args:
            chapter_id: Chapter identifier (e.g., 'ch_001')
            content: Chapter content
        """
        chapters_dir = Path("data/chapters")
        chapters_dir.mkdir(parents=True, exist_ok=True)

        chapter_file = chapters_dir / f"{chapter_id}.md"

        with open(chapter_file, 'w', encoding='utf-8') as f:
            f.write(content)

        print(f"[OK] Saved chapter text to {chapter_file}")

    def load_chapter_text(self, chapter_id: str) -> Optional[str]:
        """
        Load chapter text from markdown file.

        Args:
            chapter_id: Chapter identifier

        Returns:
            Chapter content, or None if not found
        """
        chapter_file = Path("data/chapters") / f"{chapter_id}.md"

        if not chapter_file.exists():
            return None

        with open(chapter_file, 'r', encoding='utf-8') as f:
            return f.read()

    def list_backups(self) -> list[str]:
        """List all available backup files."""
        backups = sorted(self.backup_dir.glob("story_memory_*.json"), reverse=True)
        return [b.name for b in backups]

    def restore_backup(self, backup_name: str) -> StoryMemory:
        """
        Restore memory from a backup file.

        Args:
            backup_name: Name of the backup file

        Returns:
            Restored StoryMemory object
        """
        backup_file = self.backup_dir / backup_name

        if not backup_file.exists():
            raise FileNotFoundError(f"Backup not found: {backup_name}")

        with open(backup_file, 'r', encoding='utf-8') as f:
            memory_dict = json.load(f)

        memory = StoryMemory.model_validate(memory_dict)
        print(f"[OK] Restored from backup: {backup_name}")

        return memory
