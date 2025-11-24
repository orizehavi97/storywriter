# Oda-Style Manga Story Engine (OSSE)

### _Product Requirements Document (PRD)_

### Based on: “Planning an AI System to Emulate Eiichiro Oda’s Manga Writing Style.pdf”

---

# 1. Document Info

- **Project Name:** Oda-Style Manga Story Engine (OSSE)
- **Owner:** Ori (solo developer)
- **Tech Stack:** Python + LLMs + Vector Store/SQLite
- **Goal:** Generate infinite, coherent, Oda-style serialized manga storytelling

---

# 2. Vision & Background

Build a Python-powered system that:

- Writes **unlimited chapters** in an Oda-like serialized manga narrative style.
- Maintains deep **long-term continuity**, callbacks, and foreshadowing.
- Introduces new characters, factions, mysteries—just like Oda.
- Allows **optionally interactive story forks**.
- Stores and evolves an entire fictional world: locations, politics, history, lore.
- Is future-ready for **panel and animation generation**.

The final result is a continuously expanding, long-form epic—similar in spirit to One Piece, but original.

---

# 3. Goals & Non-Goals

## 3.1 Primary Goals

1. **Infinite Chapter Generation**
2. **Long-term Memory**
3. **Character-Driven Narrative**
4. **Deep World-Building**
5. **Thematic Consistency** (dreams, freedom, friendship, inherited will)
6. **Multi-stage Writing Pipeline** (brainstorm → outline → draft → revise → finalize)
7. **Optional Human Interactivity**
8. **Python-based Modular Architecture**
9. **Visual/Animation Readiness**

## 3.2 Non-Goals

- Full manga panel production (until later phases)
- Animated episodes
- Reproducing One Piece IP (NO copying)
- Autonomous multi-agent simulation (for future experimentation)

---

# 4. Users & Personas

### Primary:

- **You**, the author-engineer.

### Secondary (future):

- Readers
- Community voters/participants

---

# 5. High-Level Product Concept

The system consists of:

- **Story Memory** (structured/unstructured + embeddings)
- **Arc & Chapter Planner** (saga → arc → chapter)
- **Chapter Writer** (LLM-based)
- **Continuity & Style Checker**
- **Character/World Updater**
- **Optional Interactive Decision Interface**
- **Future Visual Pipelines**

Loops continuously: **Plan → Retrieve → Write → Edit → Update → Repeat**

---

# 6. Functional Requirements

---

## 6.1 Story Memory Module

### 6.1.1 Data Types

#### 1. Chapter Memory

- ID, arc ID, title
- Full text
- Summary
- Key events
- Cliffhanger type

#### 2. Arc Memory

- Arc ID, name
- Location/environment
- Villains, allies
- Themes
- Arc type (heist, rebellion, tournament, spy, etc.)
- Plot phase summaries
- Targeted thread resolutions

#### 3. Character Database

- Appearance, personality, quirks
- Dreams & ambitions
- Fears, flaws
- Fighting style / abilities
- Relationship graph
- Items held
- Status (alive, captured, injured…)
- Last seen, last chapter
- Current character arc status

#### 4. World State & Lore

- Locations: climate, culture, politics, history
- Factions/organizations
- Economies, myths, symbols
- Artifacts/items and ownership histories

#### 5. Open Plot Threads

- Setup scene
- Thread type (mystery, prophecy, item, promise)
- Expected payoff range
- Status
- Possible resolutions

#### 6. Meta Memory

- Arc type history
- Tone logs
- Theme distribution

---

### 6.1.2 Memory Operations

- **Create/Update**  
  After each chapter: update characters, world state, threads.

- **Retrieve**  
  Multi-layer retrieval: arc → chapter → character → items → threads.

- **Consolidation**  
  Compress old arcs into summaries.

- **Consistency Queries**  
  `is_alive(x)`, `has_item(x, item)`, `location_state(loc)`.

---

## 6.2 Plot Planning Module

### 6.2.1 Saga Planning

- Final overarching “destination” (Oda-style known ending)
- Saga milestones

### 6.2.2 Arc Planning

- Arc concept & setting
- Factions, villains, allies
- Themes
- Which threads will progress
- Arc type selection & variety balancing
- Arc structure:
  1. Arrival
  2. Conflict discovery
  3. Escalation
  4. Climax
  5. Resolution
  6. Departure

### 6.2.3 Chapter Planning

- Outline with scene-by-scene beats:
  - Location
  - Characters
  - Purpose of scene
  - Tone
  - Thematic moment
  - Foreshadowing
  - Required cliffhanger

Outputs:

- Beat outline
- Expected outcomes
- State changes

---

## 6.3 Chapter Writing Agent

### 6.3.1 Inputs

- Chapter outline
- Retrieved memory
- Style rules

### 6.3.2 Outputs

- ~1,000–2,000 word chapter
- Rich descriptive scenes
- Character-consistent dialogue
- Strong final hook

### 6.3.3 Constraints

- No lore contradictions
- Personality-consistent actions
- Visual-friendly descriptions
- Respect power system logic

---

## 6.4 Continuity & Consistency Checker

### 6.4.1 Hard Rules

- Dead characters stay dead
- Missing limbs stay missing
- Items must be possessed to be used
- Characters cannot teleport
- Destroyed places remain destroyed unless rebuilt

### 6.4.2 Soft Checks

- Voice consistency
- Emotional consistency
- Thematic consistency
- No excessive darkness without relief

### 6.4.3 Structural Checks

- Proper pacing
- Cliffhanger present
- Non-repetitive arc patterns

### 6.4.4 Actions

- Suggest revisions
- Auto-fix small issues
- Re-prompt chapter writer for major issues
- Ask human for key choices (optional)

---

## 6.5 Character & World Updating Module

### Inputs:

- Final chapter
- Outline outcomes
- Extracted changes (LLM)

### Responsibilities:

- Update character states
- Update world states
- Manage open threads
- Generate summaries
- Embed summaries into vector store
- Persist all data to disk/DB

---

## 6.6 Interactive Decision Interface (Optional)

### Use Cases:

- Choosing new arcs
- Approving chapter outlines
- Selecting which unresolved thread to pay off
- Selecting new crewmates or major reveals

### Requirements:

- CLI or simple GUI
- Options:
  - Fully automatic
  - Semi-automatic (pause on big decisions)

---

## 6.7 Style & Creativity Requirements

### Core Themes:

- Dreams & ambition
- Friendship & loyalty
- Freedom vs oppression
- Inherited will
- Humor & adventure

### Tone Management:

- Tragedy followed by relief
- Rare character deaths
- Strong emotional balance

### Character Quirks:

- Unique speech patterns
- Running gags

### Creative Spice Input:

- Mythology, bizarre animals, weird cultures
- External creative prompt list

### Battle Rules:

- Consistent power logic
- Creative abuse of abilities
- Character development during fights

### Cliffhangers:

**Mandatory for every chapter**

---

# 7. Non-Functional Requirements

- **High Coherence** across 100+ chapters
- **Performance:** slow is acceptable
- **Recovery:** persistent storage
- **Cost Management:** local vs API models
- **Extensibility:** new arcs, modules, power systems

---

# 8. Technical Design & Stack

## 8.1 LLM & Embeddings

- Generation: GPT-4+, Claude, or local LLaMA models
- Embeddings: sentence transformers
- Large context windows recommended

## 8.2 Storage

- SQLite for structured data
- JSON/YAML for configs
- FAISS for vector embeddings

## 8.3 Orchestration

Python modules for:

- `planner`
- `memory`
- `writer`
- `checker`
- `updater`
- `interface`
- `vector_store`
- `db`

## 8.4 Planning DSL

- Structured outline: scenes, tone, themes, beats, cliffhangers

## 8.5 Testing

- Unit tests for continuity rules
- Integration tests for mini-arcs
- Metrics: thread resolution rate, arc-type diversity, theme frequency

---

# 9. Roadmap

### **Phase 0 – Manual Prototype**

- Write 2–3 chapters manually with notes
- Learn the shape of the system

### **Phase 1 – Minimal System**

- JSON-based memory
- Simple planner & writer
- Manual continuity check

### **Phase 2 – Full Memory + RAG**

- World DB, characters, locations
- Embeddings + retrieval
- Advanced chapter planner

### **Phase 3 – Continuity Checker**

- Hard + soft rules
- Automated revision loop

### **Phase 4 – Interactivity**

- CLI menu for decisions

### **Phase 5 – Visual Extensions**

- Character images
- Cover illustrations per chapter

### **Phase 6 – Multi-Agent Simulation (Experimental)**

---

# 10. Risks & Open Questions

1. **LLM Drift**
2. **Memory Bloat**
3. **Complexity vs Solo Dev**
4. **Legal Safety** (original world only)
5. **Visual Consistency** (later challenge)

---

# 11. Appendix

- Source used:  
  **Planning an AI System to Emulate Eiichiro Oda’s Manga Writing Style.pdf**
