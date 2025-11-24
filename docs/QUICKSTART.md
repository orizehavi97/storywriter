# Quick Start Guide

## Installation (5 minutes)

```bash
# 1. Install dependencies
pip install -e .

# 2. Set up API key
cp .env.template .env
# Edit .env and add your ANTHROPIC_API_KEY or OPENAI_API_KEY

# 3. Verify setup
python test_setup.py
```

## File Overview

### Configuration Files (customize these!)

- **[config/world_seed.yaml](config/world_seed.yaml)** - Your story world (protagonist, setting, factions)
- **[config/style_guide.yaml](config/style_guide.yaml)** - Writing style rules (themes, tone, structure)
- **[config/llm_config.yaml](config/llm_config.yaml)** - LLM settings (provider, model, temperature)

### Core Data Models

All in [src/story_writer/models/](src/story_writer/models/):

```python
from story_writer.models import (
    Character,      # Character profiles
    Chapter,        # Complete chapters
    Arc,           # Multi-chapter arcs
    PlotThread,    # Mysteries, quests, etc.
    StoryMemory,   # Top-level state
)
```

### LLM Client

```python
from story_writer.utils import create_client

# Create client (reads from config)
client = create_client()

# Generate text
response = client.generate(
    prompt="Write a dramatic scene...",
    system_prompt="You are a manga writer...",
    temperature=0.9
)
```

## Project Structure

```
src/story_writer/
├── models/        ✓ Data schemas (DONE)
├── utils/         ✓ LLM client, config (DONE)
├── memory/        ⏳ Storage layer (NEXT)
├── planner/       ⏳ Chapter planning (NEXT)
├── writer/        ⏳ Chapter writing (NEXT)
├── updater/       ⏳ State updates (NEXT)
├── checker/       ⏳ Continuity (Phase 3)
└── interface/     ⏳ CLI (Phase 4)
```

## Development Phases

### Phase 0: Foundation ✓ COMPLETE
- Project structure
- Data models
- Configuration system
- LLM client wrapper

### Phase 1: Minimal System (NEXT)
Build these 4 modules:
1. **memory/json_store.py** - Save/load story state
2. **planner/chapter_planner.py** - Generate chapter outlines
3. **writer/chapter_writer.py** - Write full chapters
4. **updater/state_updater.py** - Extract and update state

Goal: Generate 5-10 consecutive chapters

### Phase 2: Intelligent Memory
- SQLite database
- Vector embeddings
- Smart retrieval
- Arc planning

Goal: Generate 20-50 chapters with callbacks

### Phase 3: Quality Control
- Continuity checker
- Hard rules (character states)
- Soft rules (tone, voice)
- Revision loop

### Phase 4: Interactivity
- CLI interface
- Decision points
- Manual overrides

## Quick Examples

### Create a Character

```python
from story_writer.models import Character

char = Character(
    character_id="char_001",
    name="Kael",
    age=17,
    personality="Optimistic, reckless, fiercely loyal",
    dream="Find his lost homeland",
    abilities=["Sky Affinity", "Natural navigator"],
    status="active"
)
```

### Create a Plot Thread

```python
from story_writer.models import PlotThread

thread = PlotThread(
    thread_id="thread_001",
    name="What happened to Kael's homeland?",
    thread_type="mystery",
    setup_chapter="ch_001",
    setup_description="Kael mentions his destroyed island",
    importance="major",
    expected_resolution="long_term"
)
```

### Initialize Story Memory

```python
from story_writer.models import StoryMemory

memory = StoryMemory(
    story_title="Sky Wanderers",
    world_name="The Shattered Isles",
    saga_goal="Unite the scattered islands and uncover the truth"
)

# Add entities
memory.characters[char.character_id] = char
memory.plot_threads[thread.thread_id] = thread
```

## Customizing Your World

Edit [config/world_seed.yaml](config/world_seed.yaml):

```yaml
world_name: "Your World Name"

setting:
  description: "Your setting description..."
  geography: "Your geography..."

protagonist:
  name: "Your Protagonist"
  dream: "Their ultimate goal..."
  personality: "Their traits..."

# Add factions, locations, power systems, etc.
```

## Key Design Principles

1. **Long-term Continuity** - Track everything, reference the past
2. **Character-Driven** - Characters are the heart of the story
3. **Thematic Consistency** - Themes appear regularly
4. **Structured but Creative** - Planning + creative generation
5. **Modular Architecture** - Each component is independent

## Getting Help

- Run `python test_setup.py` to diagnose issues
- Check [SETUP.md](SETUP.md) for detailed setup instructions
- Review [README.md](README.md) for the full PRD
- Check configuration files for customization options

## Next Steps

After setup, you'll build Phase 1 components:

1. **Memory Store** - Load/save story state to JSON
2. **Chapter Planner** - LLM creates structured outlines
3. **Chapter Writer** - LLM writes full chapters
4. **State Updater** - Extract changes, update memory

Then you can run the full generation loop!

---

**Ready to build?** Start with the memory store in `src/story_writer/memory/json_store.py`
