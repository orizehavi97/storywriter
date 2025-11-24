# Story Writer - Setup Guide

## Project Structure Created

```
story_writer/
├── src/story_writer/          # Main source code
│   ├── models/                # Data models (Pydantic)
│   │   ├── chapter.py         # Chapter and ChapterOutline
│   │   ├── character.py       # Character model
│   │   ├── arc.py             # Arc model
│   │   ├── world.py           # WorldLocation, Faction, Artifact
│   │   ├── thread.py          # PlotThread model
│   │   └── memory.py          # StoryMemory (main state)
│   ├── memory/                # Storage layer (Phase 1-2)
│   ├── planner/               # Planning modules
│   ├── writer/                # Writing modules
│   ├── checker/               # Consistency validation (Phase 3)
│   ├── updater/               # State management
│   ├── interface/             # CLI (Phase 4)
│   └── utils/
│       ├── config.py          # Configuration management
│       └── llm_client.py      # LLM wrapper (Claude/GPT)
├── config/
│   ├── llm_config.yaml        # LLM settings
│   ├── style_guide.yaml       # Oda-style writing rules
│   └── world_seed.yaml        # Initial world configuration
├── data/
│   ├── chapters/              # Generated chapters
│   ├── memory/                # Memory JSON files
│   └── manual_prototype/      # Hand-written samples
├── tests/                     # Test suite
├── .env.template              # Environment variables template
├── pyproject.toml             # Dependencies and config
├── test_setup.py              # Setup verification script
└── README.md                  # Main project documentation
```

## Next Steps

### 1. Install Dependencies

First, install the project in development mode:

```bash
pip install -e .
```

This will install:
- `anthropic` - Claude API client
- `openai` - OpenAI API client
- `pydantic` - Data validation
- `pyyaml` - Configuration files
- `python-dotenv` - Environment variables

### 2. Set Up API Keys

Copy the environment template:

```bash
cp .env.template .env
```

Then edit `.env` and add your API key:

```env
# For Claude (recommended)
ANTHROPIC_API_KEY=your_anthropic_api_key_here

# OR for OpenAI
OPENAI_API_KEY=your_openai_api_key_here
```

Get API keys from:
- Anthropic Claude: https://console.anthropic.com/
- OpenAI: https://platform.openai.com/

### 3. Verify Setup

Run the test script:

```bash
python test_setup.py
```

All tests should pass!

### 4. Customize Your World

Edit [config/world_seed.yaml](config/world_seed.yaml) to customize:
- World name and setting
- Protagonist details
- Initial factions
- Starting location
- Power system rules

The default world is "The Shattered Isles" (sky islands), but you can create any setting you want!

## What's Been Built

### Core Data Models

All foundational data structures are ready:

- **Chapter** - Complete chapter with content and metadata
- **ChapterOutline** - Planning structure before writing
- **Character** - Full character profiles with personality, abilities, relationships
- **Arc** - Multi-chapter story arcs with phases
- **PlotThread** - Mystery/prophecy/quest tracking
- **WorldLocation** - Locations with culture, politics, history
- **Faction** - Organizations and groups
- **Artifact** - Special items
- **StoryMemory** - Top-level story state container

### Configuration System

Three YAML config files control the system:

1. **llm_config.yaml** - LLM provider and model settings
2. **style_guide.yaml** - Oda-style writing rules
3. **world_seed.yaml** - Your story's starting state

### LLM Client

Ready-to-use LLM wrapper supporting:
- Anthropic Claude
- OpenAI GPT-4
- Automatic retries
- Token estimation
- Easy provider switching

## What's Next (Phase 1)

Now that the foundation is ready, the next step is to build the core generation loop:

1. **Memory Store** - JSON-based storage (simple file I/O)
2. **Chapter Planner** - LLM-powered outline generation
3. **Chapter Writer** - LLM-powered chapter writing
4. **State Updater** - Extract changes and update memory
5. **Main Loop** - Orchestrate the full process

This will let you generate your first chapters!

## Testing Your Setup

The `test_setup.py` script verifies:
- ✓ All modules import correctly
- ✓ Configuration files load
- ✓ Data models can be created
- ✓ LLM client initializes (with API key)

## Configuration Files

### World Seed ([config/world_seed.yaml](config/world_seed.yaml))

Defines your story's starting state:
- World name: "The Shattered Isles"
- Setting: Sky islands in an endless sky
- Protagonist: Kael, 17-year-old orphan
- Power system: Sky Affinity
- Initial factions and conflicts

Feel free to completely change this to your own original world!

### Style Guide ([config/style_guide.yaml](config/style_guide.yaml))

Oda-inspired writing rules:
- Core themes (dreams, friendship, freedom)
- Chapter structure (1500 words, 3-5 scenes, mandatory cliffhanger)
- Tone management (optimistic with stakes)
- Character voice requirements

### LLM Config ([config/llm_config.yaml](config/llm_config.yaml))

Technical settings:
- Provider: anthropic (Claude) or openai (GPT)
- Model selection
- Temperature settings
- Token limits

## Development Workflow

1. **Phase 0 (Current)**: Foundation complete ✓
2. **Phase 1 (Next)**: Build minimal generation system
3. **Phase 2**: Add intelligent memory and retrieval
4. **Phase 3**: Add continuity checking
5. **Phase 4**: Add interactive CLI
6. **Phase 5+**: Visual extensions

## Need Help?

- Check main [README.md](README.md) for the full PRD
- Run `python test_setup.py` to diagnose issues
- Verify API keys are set in `.env`
- Check that all dependencies installed: `pip list`

---

**Status**: Foundation complete! Ready to build Phase 1 components.
