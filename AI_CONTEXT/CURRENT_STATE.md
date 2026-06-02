# Current State

Last updated: 2026-06-02

## Project Location

The actual project is here:

```text
/Users/cight/Desktop/chess-analyzer
```

There are similarly named folders under `/Users/cight/Documents/`, but they are not the active project:

```text
/Users/cight/Documents/ChessAdapter 2
/Users/cight/Documents/ChessAdapter
```

## Git State At Creation

Branch:

```text
xxkurai...origin/xxkurai
```

Working tree at the time this context was created:

```text
M index.html
```

Important: `index.html` already had uncommitted changes before this shared context was added. Treat those as user/project changes and inspect before editing.

## How To Run

Recommended macOS/Linux quick start:

```bash
./run.sh
```

Manual run:

```bash
python3 -m venv .venv
.venv/bin/python -m pip install -r requirements.txt
.venv/bin/python -m uvicorn main:app --reload --host 127.0.0.1 --port 8000
```

Open:

```text
http://127.0.0.1:8000
```

Windows:

```bat
run_windows.bat
```

## Dependencies

Python dependencies from `requirements.txt`:

```text
fastapi
uvicorn
python-chess
pydantic
python-dotenv
google-genai
requests
```

Stockfish is required for full analysis. On macOS:

```bash
brew install stockfish
```

## What Is Known

- The app is a FastAPI backend serving a single-page frontend from `index.html`.
- `main.py` contains Stockfish analysis, move classification, Gemini comments, Chess.com API support, and Lichess opening explorer support.
- `index.html` contains the full UI, CSS, board interaction logic, charting, Chess.com recent-games UI, analysis flow, and openings UI.
- The project uses local `.venv`, `.env`, and local Stockfish binaries as developer-specific files.

## Known Risks

- `index.html` is large and is the most likely conflict point for parallel chats.
- Gemini requires `GEMINI_API_KEY`; without it, coach features may be disabled or degraded.
- Stockfish must be installed or available through `STOCKFISH_PATH`.
- Network calls to Chess.com, Lichess, and Gemini can fail independently of local app correctness.

## Recent Progress

- 2026-06-02: Created shared `AI_CONTEXT/` memory folder in the real project root.
- 2026-06-02: Added `AGENTS.md` root pointer for future Codex chats.
- 2026-06-02: Recorded stack, run commands, important files, API routes, current git state, and parallel chat protocol.

## Open Questions

- What are the top 3 immediate product tasks?
- Should `index.html` remain a single file, or should the frontend be split once the current feature push stabilizes?
- Should the parallel chats use separate git worktrees for safer simultaneous work?

