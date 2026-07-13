# Velora AI — Local Multi-Agent AI Web App

Hierarchical multi-agent research pipeline powered by **LangGraph 1.x** and **Ollama** — fully local, no paid APIs / web search.

Includes an Apple-style **AI Lab** landing page under `ai-lab-landing/`.

## Architecture (Phase-1)

```
START → Supervisor → Researcher → Supervisor → FINISH
              │                        ▲
              └────────────────────────┘
```

| Agent        | Role                                              | Status   |
|--------------|---------------------------------------------------|----------|
| Supervisor   | Sole decision-maker; sets `next_agent` / `status` | ✅ Phase-1 |
| Researcher   | Wikipedia + Arxiv tools → research brief          | ✅ Phase-1 |
| Writer       | Markdown report from findings                     | ⏳ Phase-2 |
| Critic       | Quality / accuracy review                         | ⏳ Phase-2 |

## Prerequisites

1. **Python 3.11+**
2. **Ollama** running at `http://localhost:11434`
3. Pull the model:

```bash
ollama pull qwen2.5:7b
```

## Setup

```bash
cd localmultiagent
python -m venv .venv

# Windows
.venv\Scripts\activate

# Linux / macOS
# source .venv/bin/activate

pip install -r requirements.txt
```

Optional env vars (see `src/config.py`):

```env
OLLAMA_MODEL=qwen2.5:7b
OLLAMA_BASE_URL=http://localhost:11434
```

## Run Phase-1 test

```bash
python test_phase1.py
python test_phase1.py "Retrieval Augmented Generation"
```

Expected path: Supervisor decides `researcher` → Researcher gathers notes → Supervisor finishes (Writer not wired yet).

## Project layout

```
src/
  state.py              # AgentState TypedDict
  config.py             # Settings
  llm.py                # ChatOllama factory
  graph.py              # StateGraph build + compile
  agents/
    supervisor.py       # supervisor_node + route_supervisor
    researcher.py       # researcher_node (tool loop)
  tools/
    research_tools.py   # WikipediaQueryRun + ArxivQueryRun
  prompts/
    prompts.py          # System prompts
test_phase1.py
requirements.txt
```

## State schema

- `messages` — conversation history (`add_messages` reducer)
- `current_task` — user topic
- `research_findings` — Researcher output
- `draft_report` / `critic_feedback` / `final_report` — Phase-2 fields
- `status` — `research` | `write` | `critic` | `done`
- `next_agent` — `researcher` | `writer` | `critic` | `FINISH`
