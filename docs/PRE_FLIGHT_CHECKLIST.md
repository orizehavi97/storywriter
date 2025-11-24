# Pre-Flight Checklist

Run through this checklist before starting Phase 1 development.

## ✅ Setup Verification

### 1. Dependencies Installed

```bash
pip install -e .
```

Verify packages are installed:
```bash
pip list | grep -E "(anthropic|openai|pydantic|pyyaml)"
```

Expected output:
```
anthropic      >=0.39.0
openai         >=1.54.0
pydantic       >=2.9.0
pyyaml         >=6.0
python-dotenv  >=1.0.0
```

✅ **Status**: Dependencies already installed

---

### 2. API Key Configuration

Create your `.env` file:

```bash
cp .env.template .env
```

Edit `.env` and add your API key:

```env
# For Claude (Recommended for creative writing)
ANTHROPIC_API_KEY=sk-ant-api03-...

# OR for OpenAI
OPENAI_API_KEY=sk-...
```

**Get API keys:**
- Anthropic Claude: https://console.anthropic.com/settings/keys
- OpenAI: https://platform.openai.com/api-keys

**Cost estimates (approximate):**
- Claude Sonnet: ~$3 per million input tokens, ~$15 per million output tokens
- GPT-4 Turbo: ~$10 per million input tokens, ~$30 per million output tokens
- Per chapter (~2000 tokens): ~$0.03-0.10 depending on context

⚠️ **Status**: `.env` file needs to be created

---

### 3. Run Tests

**Basic setup test:**
```bash
python tests/test_setup.py
```

Expected: All tests pass ✓

**LLM connection test** (after setting API key):
```bash
python tests/test_llm_connection.py
```

Expected: Successful API call with sample response

---

### 4. Customize Your World (Optional)

Edit `config/world_seed.yaml` to customize:
- World name and setting
- Protagonist details
- Factions and conflicts
- Power system rules

Default world: "The Shattered Isles" (sky islands setting)

---

### 5. Verify Git Repository

```bash
git status
```

Expected: Clean working tree

```bash
git log --oneline
```

Expected: At least 3 commits (initial setup, settings, test script)

---

## 🚀 Ready for Phase 1?

Once all items above are complete, you're ready to build:

### Phase 1 Components
1. **memory/json_store.py** - Save/load story state
2. **planner/chapter_planner.py** - Generate chapter outlines
3. **writer/chapter_writer.py** - Write full chapters
4. **updater/state_updater.py** - Update memory

### Expected Outcome
Generate 5-10 consecutive chapters with basic continuity

---

## Quick Commands Reference

```bash
# Run basic tests
python tests/test_setup.py

# Test LLM connection (requires API key)
python tests/test_llm_connection.py

# Run the main application (Phase 1+)
python main.py

# Check git status
git status

# View recent commits
git log --oneline -5
```

---

## Troubleshooting

### "API_KEY not found"
- Ensure `.env` file exists in project root
- Check that the key is correctly formatted (no quotes needed)
- Verify the key is valid on the provider's dashboard

### "ModuleNotFoundError"
- Run `pip install -e .` to install the package
- Verify you're in the correct directory

### Tests failing
- Run `python tests/test_setup.py` to diagnose
- Check Python version: `python --version` (needs 3.13+)
- Verify all config files exist in `config/` directory

### Import errors
- Ensure you're running from the project root
- Check that all `__init__.py` files exist
- Try: `pip install -e . --force-reinstall`

---

## Current Status

- ✅ Project structure complete
- ✅ Data models implemented
- ✅ Configuration files ready
- ✅ LLM client wrapper built
- ✅ Tests created
- ✅ Git repository initialized
- ⚠️ `.env` file needs to be created
- ⚠️ LLM connection needs to be tested

**Next**: Create `.env` file, test LLM connection, then proceed to Phase 1!
