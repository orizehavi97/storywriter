# Storywriter

[![Python 3.12+](https://img.shields.io/badge/python-3.12+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

> An intelligent AI-powered story generation system for creating long-form, serialized narratives with consistent characters, evolving plot threads, and rich world-building inspired by Eiichiro Oda's narrative style.

## 🎯 Overview

Storywriter is a production-ready story generation engine that creates compelling, serialized narratives with:

- **Intelligent State Management** - Automatic tracking of characters, relationships, locations, and plot threads
- **Semantic Memory** - Vector-based retrieval for context-aware chapter planning
- **Quality Control** - Automated continuity checking and style assessment
- **Iterative Revision** - AI-driven refinement based on quality feedback
- **World Timeline** - Chronological event tracking with impact analysis
- **Relationship Dynamics** - Character relationship mapping with evolving types and strength

## ✨ Key Features

### 🧠 State Management
- **Character Tracking** - Automatic character extraction and deduplication
- **Relationship Evolution** - Dynamic mapping of character relationships (friend, rival, mentor, enemy, family)
- **Plot Thread Management** - Automatic introduction, progression, and resolution of narrative threads
- **World Timeline** - Chronological logging of major events (battles, discoveries, alliances, betrayals)
- **Fuzzy Matching** - Intelligent deduplication prevents "The Guard Captain" vs "Guard Captain" duplicates

### 📚 Semantic Memory
- **Vector Storage** - ChromaDB-powered semantic search for chapters, events, and plot threads
- **Smart Retrieval** - Context-aware selection of relevant past events for chapter planning
- **Historical Context** - Access to full story history for maintaining consistency

### ✅ Quality Assurance
- **Continuity Checking** - Automatic detection of character, location, and plot inconsistencies
- **Style Assessment** - Oda-style narrative quality evaluation (pacing, voice, structure)
- **Automated Revision** - Up to 2 revision cycles with targeted feedback
- **Multi-Criteria Scoring** - Overall quality, style adherence, voice consistency, pacing effectiveness

### 📝 Generation Pipeline
- **Chapter Planning** - LLM-powered outline generation with scene breakdown
- **Narrative Writing** - GPT-4o-based chapter composition (target 1500 words)
- **Quality Loop** - Iterative refinement until quality thresholds are met
- **State Extraction** - Automatic memory updates from generated content

## 📦 Installation

### Prerequisites

- Python 3.12 or higher
- OpenAI API key
- 2GB+ RAM (for embedding models)

### Setup

1. **Clone the repository**
   ```bash
   git clone https://github.com/yourusername/story_writer.git
   cd story_writer
   ```

2. **Install dependencies**
   ```bash
   pip install -e .
   ```

   This installs:
   - `openai` - LLM provider
   - `pydantic` - Data validation
   - `chromadb` - Vector database
   - `sentence-transformers` - Embedding models
   - `pyyaml` - Configuration parsing

3. **Configure API keys**

   Create a `.env` file in the project root:
   ```env
   OPENAI_API_KEY=your_api_key_here
   ```

4. **Set up world seed** (optional)

   Edit `config/world_seed.yaml` to customize your story world:
   ```yaml
   world_name: "The Shattered Isles"
   starting_location:
     name: "Drift Port"
     description: "A bustling harbor town"

   protagonist:
     name: "Kael"
     age: 17
     personality: "Optimistic, reckless, loyal"
     dream: "Find the lost homeland"
   ```

## 🚀 Quick Start

### Generate Your First Chapter

```bash
python main.py
```

The interactive CLI will guide you through:
1. Story initialization (from world seed)
2. Chapter generation
3. Automatic quality control
4. Memory state updates

### Basic Workflow

```
┌─────────────────┐
│  Initialize     │
│  Story Memory   │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  Plan Chapter   │ ◄─── Smart context retrieval
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  Write Chapter  │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  Quality Check  │ ◄─── Continuity & style assessment
└────────┬────────┘
         │
    ┌────┴────┐
    │  Pass?  │
    └────┬────┘
         │ No
         ▼
┌─────────────────┐
│  Revise Chapter │ (max 2 iterations)
└────────┬────────┘
         │ Yes
         ▼
┌─────────────────┐
│  Update State   │ ◄─── Extract characters, threads, relationships
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  Save & Index   │
└─────────────────┘
```

## 📖 Usage Examples

### Programmatic Story Generation

```python
from story_writer.memory import JSONMemoryStore, VectorMemoryStore, SmartRetriever
from story_writer.planner import ChapterPlanner
from story_writer.writer import ChapterWriter
from story_writer.updater import StateUpdater
from story_writer.checker import ContinuityChecker, QualityChecker
from story_writer.utils import create_client

# Initialize components
client = create_client()
store = JSONMemoryStore()
vector_store = VectorMemoryStore()
retriever = SmartRetriever(vector_store)

planner = ChapterPlanner(client, retriever=retriever)
writer = ChapterWriter(client)
updater = StateUpdater(client, vector_store=vector_store)
continuity_checker = ContinuityChecker()
quality_checker = QualityChecker(client)

# Load or initialize story
memory = store.load() or store.initialize_new_story(
    story_title="My Epic Saga",
    world_name="Fantasy World",
    saga_goal="Save the realm"
)

# Generate chapter
arc = memory.get_current_arc()
outline = planner.plan_chapter(memory, arc)
chapter = writer.write_chapter(outline, memory)

# Quality control
violations = continuity_checker.check_chapter(chapter, memory)
quality_report = quality_checker.check_chapter(chapter, chapter.content, memory)

# Update state
memory = updater.update_from_chapter(chapter, memory)
store.save(memory, backup=True)
```

### Accessing Story Data

```python
# Load story memory
store = JSONMemoryStore()
memory = store.load()

# Query characters
for char in memory.characters.values():
    print(f"{char.name} ({char.role}): {char.personality}")

# Check relationships
for rel_id, rel in memory.relationships.items():
    char_a = memory.characters[rel.character_a].name
    char_b = memory.characters[rel.character_b].name
    print(f"{char_a} ↔ {char_b}: {rel.relationship_type} (strength: {rel.strength})")

# View timeline
for event in memory.world_timeline:
    print(f"Ch{event.chapter_number}: [{event.event_type}] {event.description}")

# Analyze plot threads
open_threads = [t for t in memory.plot_threads.values() if t.status == "open"]
print(f"{len(open_threads)} open plot threads")
```

## 🗂️ Project Structure

```
story_writer/
├── config/
│   └── world_seed.yaml          # Story world configuration
├── data/
│   ├── chapters/                # Generated chapter markdown files
│   ├── memory/                  # JSON story state + backups
│   │   ├── backups/            # Timestamped backups
│   │   └── vectors/            # ChromaDB vector storage
│   └── models/                  # Cached embedding models (auto-downloaded)
├── src/story_writer/
│   ├── checker/                 # Quality control
│   │   ├── continuity_checker.py  # Detect inconsistencies
│   │   └── quality_checker.py     # Oda-style assessment
│   ├── memory/                  # Memory systems
│   │   ├── json_store.py         # JSON persistence
│   │   ├── vector_store.py       # ChromaDB integration
│   │   └── smart_retriever.py    # Context-aware retrieval
│   ├── models/                  # Data models
│   │   ├── memory.py             # StoryMemory, Arc, Chapter
│   │   ├── character.py          # Character model
│   │   ├── thread.py             # PlotThread model
│   │   └── tracker.py            # Relationship, WorldEvent
│   ├── planner/                 # Chapter planning
│   │   └── chapter_planner.py
│   ├── updater/                 # State extraction
│   │   └── state_updater.py      # LLM-based state extraction
│   ├── writer/                  # Chapter writing
│   │   ├── chapter_writer.py
│   │   └── chapter_reviser.py    # Revision with feedback
│   └── utils/
│       └── llm_client.py         # OpenAI integration
├── tests/                       # Unit tests
├── main.py                      # CLI entry point
├── pyproject.toml               # Package configuration
└── README.md                    # This file
```

## 🏗️ System Architecture

### Core Components

#### 1. Memory Layer
- **JSON Store** - Primary persistence for story state
- **Vector Store** - Semantic search with ChromaDB
- **Smart Retriever** - Context-aware information retrieval

#### 2. Generation Layer
- **Chapter Planner** - Creates outlines with scene breakdowns
- **Chapter Writer** - Generates narrative content
- **State Updater** - Extracts entities from generated text

#### 3. Quality Layer
- **Continuity Checker** - Rule-based consistency validation
- **Quality Checker** - LLM-based style assessment
- **Chapter Reviser** - Iterative refinement with feedback

#### 4. Data Models
- **StoryMemory** - Central state container
- **Character** - Entity tracking with relationships
- **PlotThread** - Narrative arc management
- **Chapter** - Generated content with metadata
- **Arc** - Story structure organization
- **Relationship** - Character dynamics
- **WorldEvent** - Timeline tracking

### Data Flow

```
User Input → Chapter Planning → Content Generation → Quality Check
                 ↓                     ↓                    ↓
         Context Retrieval      State Extraction    Pass/Revise
                 ↓                     ↓                    ↓
           Vector Search        Entity Detection     Feedback Loop
                 ↓                     ↓                    ↓
         Historical Data       Memory Updates      Final Chapter
                                      ↓
                              JSON + Vector Storage
```

## 🔧 Configuration

### World Seed (`config/world_seed.yaml`)

Define your story's foundation:

```yaml
world_name: "The Shattered Isles"
starting_location:
  name: "Drift Port"
  description: "A bustling harbor town"

protagonist:
  name: "Kael"
  age: 17
  personality: "Optimistic, reckless, loyal"
  dream: "Find the lost homeland"
  abilities:
    - "Wind current navigation"
    - "Natural leadership"

initial_crew:
  - name: "Finn"
    personality: "Cautious, inventive"
    role: "Mechanic and pilot"

central_conflict: |
  The Sky Empire controls ancient technology.
  A prophecy speaks of the Wind Walker.

initial_threads:
  - thread: "Protagonist's destroyed homeland - what happened?"
    type: "mystery"
  - thread: "Ancient ruins contain forbidden technology"
    type: "mystery"

themes:
  - adventure
  - friendship
  - freedom vs control
```

### Environment Variables

```env
# Required
OPENAI_API_KEY=sk-...

# Optional
OPENAI_MODEL=gpt-4o              # Default: gpt-4o
EMBEDDING_MODEL=all-MiniLM-L6-v2  # Default: all-MiniLM-L6-v2
CHAPTER_TARGET_WORDS=1500         # Default: 1500
MAX_REVISIONS=2                   # Default: 2
```

## 📊 Data Models

### StoryMemory
```python
story_title: str
world_name: str
characters: dict[str, Character]
plot_threads: dict[str, PlotThread]
chapters: dict[str, Chapter]
arcs: dict[str, Arc]
relationships: dict[str, Relationship]
world_timeline: list[WorldEvent]
```

### Character
```python
character_id: str
name: str
personality: str
dream: str | None
abilities: list[str]
status: str  # active, injured, captured, dead
current_location: str
items: list[str]
```

### Relationship
```python
character_a: str  # character_id
character_b: str  # character_id
relationship_type: str  # friend, rival, enemy, mentor, family
strength: int  # 0-100
established_chapter: str
last_updated: str
notes: str
```

### WorldEvent
```python
event_id: str
chapter_id: str
description: str
event_type: str  # battle, discovery, death, alliance, betrayal
impact: str  # minor, moderate, major, critical
timestamp: datetime
```

## 🎨 Oda-Style Quality Metrics

The system evaluates chapters on:

- **Overall Score** (0-100)
  - Oda Style adherence
  - Voice consistency
  - Pacing effectiveness

- **Story Elements**
  - Cliffhanger presence
  - Foreshadowing
  - Callbacks to past events

- **Strengths & Weaknesses**
  - AI-identified positive aspects
  - Constructive improvement suggestions

**Quality Thresholds:**
- ≥85: Excellent, publish-ready
- 70-84: Good, minor revisions
- <70: Needs significant revision

## 🔍 Advanced Features

### Smart Context Retrieval

The system uses semantic search to find relevant context:

```python
# Retrieve similar past events
similar_events = vector_store.search_events(
    query="character betrayal",
    n_results=5
)

# Find related plot threads
related_threads = vector_store.search_threads(
    query="ancient prophecy",
    n_results=3
)
```

### Character Deduplication

Intelligent name normalization prevents duplicates:

```
"The Mysterious Stranger" → "mysterious stranger"
"Unnamed Guard Leader"    → "guard leader"
"A wandering merchant"    → "wandering merchant"
```

### Relationship Evolution

Track how character dynamics change:

```python
# Initial meeting (Ch 1)
relationship.relationship_type = "stranger"
relationship.strength = 10

# After shared adventure (Ch 5)
relationship.relationship_type = "ally"
relationship.strength = 60

# After betrayal (Ch 8)
relationship.relationship_type = "enemy"
relationship.strength = -80
```

### Thread Deduplication

Fuzzy matching prevents duplicate plot threads:

```
"Wind Walker Prophecy"     → normalized to "wind walker prophecy"
"The Wind Walker prophecy" → normalized to "wind walker prophecy"
"wind walker prophecy"     → normalized to "wind walker prophecy"
→ Only one thread created
```

## 📈 Performance & Scaling

- **Memory Usage:** ~500MB-2GB (depends on embedding model)
- **Generation Speed:** ~30-60s per chapter (GPT-4o)
- **Storage:** ~50KB per chapter (JSON + markdown)
- **Vector DB:** Scales to 10,000+ chapters efficiently

### Optimization Tips

1. **Use smaller embedding models** for faster indexing:
   ```python
   vector_store = VectorMemoryStore(model_name="all-MiniLM-L6-v2")
   ```

2. **Batch chapter generation** to reduce API overhead

3. **Adjust quality thresholds** for faster iteration:
   ```python
   quality_checker.min_score = 75  # Default: 80
   ```

## 🧪 Testing

Run the test suite:

```bash
# Test LLM connection
python tests/test_llm_connection.py

# Test memory store
python tests/test_memory_store.py

# Test thread deduplication
python tests/test_thread_deduplication.py

# Run all tests
pytest tests/
```

## 🤝 Contributing

Contributions welcome! Areas of interest:

- **New LLM providers** (Anthropic, Cohere, local models)
- **Alternative storage backends** (PostgreSQL, MongoDB)
- **Enhanced quality metrics** (plot coherence, theme consistency)
- **Web interface** (Flask/FastAPI dashboard)
- **Export formats** (EPUB, PDF, HTML)

### Development Setup

```bash
# Install dev dependencies
pip install -e ".[dev]"

# Run linting
black src/ tests/
pylint src/

# Type checking
mypy src/
```

## 📝 License

MIT License - see [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- **Eiichiro Oda** - Inspiration for narrative style and structure
- **OpenAI** - GPT-4o API for generation
- **ChromaDB** - Vector storage and retrieval
- **Sentence Transformers** - Embedding models

## 📮 Contact & Support

- **Issues:** [GitHub Issues](https://github.com/yourusername/story_writer/issues)
- **Discussions:** [GitHub Discussions](https://github.com/yourusername/story_writer/discussions)

---

**Built with ❤️ for storytellers and AI enthusiasts**
