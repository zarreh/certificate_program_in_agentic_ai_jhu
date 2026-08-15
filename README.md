# Certificate Program in Agentic AI (JHU)

Course materials and notebooks for the JHU / Great Learning Agentic AI certificate program.

## Setup

### Prerequisites
- Python 3.12+ (managed via `.python-version`)
- [uv](https://docs.astral.sh/uv/) package manager

### Install

```bash
uv sync
```

This creates `.venv/` and installs every dependency used across the notebooks in this repo (LangChain/LangGraph, DSPy, smolagents, ChromaDB, MCP, DeepEval, spaCy, sentence-transformers, etc. — see `pyproject.toml`).

### Activate

```bash
source .venv/bin/activate
```

or

```bash
source activate.sh
```

### Configuration

Some notebooks read API credentials from `config.json`. Copy the example and fill in your own keys:

```bash
cp config.json.example config.json
```

```json
{
  "API_KEY": "your-openai-api-key-here",
  "OPENAI_API_BASE": "https://api.openai.com/v1",
  "TAVILY_API_KEY": "tvly-dev-xxxxxxxxxxxxxx"
}
```

`config.json` is gitignored — never commit real keys.

### Running notebooks

```bash
jupyter lab
```

A Jupyter kernel named **Python (agentic-ai-jhu)** is registered for this environment (`.venv/bin/python -m ipykernel install --user --name certificate-program-in-agentic-ai-jhu`) — select it when opening a notebook.

## Repository structure

```
program_overview/                          course logistics, policies, orientation
pre-work/                                   pre-work sessions
generative_ai_foundation/
  week_1/  AI-assisted Python coding
  week_2/  LLMs and prompt engineering
  week_3/  Retrieval-Augmented Generation (RAG)
  week_4/  Prompt optimization and evaluation
  week_5/  Project 1 — DualLens Analytics
introduction_to_agentic_ai_design/
  week_6/  Introduction to Agentic AI, agentic RAG
  week_7/  Core agent concepts, MCP
  week_8/  Ethics, safety, alignment, responsible AI
unstructured/                               downloads manifest tracking new/unsorted files
```

## Updating dependencies

```bash
uv add <package>       # add a new dependency
uv sync                # reinstall from the lockfile
```

`uv.lock` is committed so the environment is reproducible.

## Notes

- The notebooks themselves each `pip install` their own pinned versions in their first cell (they were authored for standalone Colab runs). Those in-notebook installs are harmless no-ops once the shared `.venv` already satisfies them, but the pins across notebooks aren't mutually consistent — `pyproject.toml` picks one resolvable, recent set of versions that covers everything each notebook actually imports rather than replicating every notebook's exact pin.
