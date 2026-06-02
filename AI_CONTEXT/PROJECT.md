# Project Context

Project root: `/Users/cight/Desktop/chess-analyzer`

## Product Goal

Chess Analyzer is an interactive chess game analyzer and AI coach.

The app lets a user load Chess.com games or paste PGN, analyzes the game with Stockfish, classifies moves, shows a game review, and uses Gemini to explain positions and mistakes in human language. The UI is a custom dark Chess.com-inspired single-page app.

## Stack

- Backend: Python, FastAPI, Uvicorn.
- Chess engine: Stockfish via `python-chess`.
- AI coach: Google Gemini through `google-genai`, enabled by `GEMINI_API_KEY`.
- External chess data: Chess.com public API and Lichess Opening Explorer.
- Frontend: single `index.html` with HTML, CSS, and JavaScript.
- Frontend libraries loaded from CDNs include chessboard.js, chess.js, and Chart.js.

## Main Features

- PGN analysis with move classification, CPL, accuracy, and report counters.
- Brilliant move heuristic for tactical material sacrifices.
- Interactive board navigation and variation/sandbox support.
- Stockfish evaluation bar and evaluation chart.
- Gemini comments and coach summaries.
- Chess.com recent game loading by username.
- Opening explorer and opening study UI.
- Mini-games tab with Stockfish bot modes: Sparring, King of the Hill, and Blindfold, plus native Stockfish `Skill Level 0..20` difficulty.

## Important Files And Directories

```text
main.py - FastAPI backend, Stockfish analysis, Gemini integration, API routes
index.html - full frontend SPA: layout, styles, board logic, charts, API calls
README.md - project overview, install, and run instructions
requirements.txt - Python dependencies
run.sh - macOS/Linux quick start using local .venv and uvicorn
run_windows.bat - Windows quick start
start.command - Finder double-click launcher for macOS
stockfish/ - local Stockfish binary location; ignored except .gitkeep
test_run.py - small direct analyzer smoke script
test_legals_mate.pgn - sample PGN
debug*.py - local debugging scripts
AI_CONTEXT/ - shared memory and coordination for parallel Codex chats
```

## API Surface

Known routes in `main.py`:

```text
GET  / - serves index.html
GET  /get_latest_game/{username} - fetches latest Chess.com game
GET  /opening_explorer - queries Lichess Opening Explorer
POST /bot_move - returns a simple Stockfish bot reply for mini-games
POST /analyze - analyzes PGN
POST /analyze_position - analyzes current/variation position
POST /evaluate_idea - evaluates a user idea from a position
POST /commentator_summary - asks Gemini for a game summary/commentary
```

## Environment

Optional `.env` keys:

```text
GEMINI_API_KEY=...
LICHESS_TOKEN=...
STOCKFISH_PATH=/path/to/stockfish
```

If `STOCKFISH_PATH` is not set, `main.py` checks local `stockfish/`, common macOS Homebrew paths, common Linux paths, and `shutil.which("stockfish")`.

## Coding Conventions

- Keep changes scoped; this project currently has a compact architecture with most logic in `main.py` and `index.html`.
- Be extra careful when editing `index.html`: it is large and currently carries most frontend state, layout, and UI logic.
- Do not overwrite user changes. Check `git status` and relevant diffs before editing.
- Prefer adding focused helper functions over broad refactors unless the user explicitly requests restructuring.
- If frontend behavior changes, run the app and verify in a browser when possible.

## Non-Negotiables

- New Codex chats must read `AI_CONTEXT/START_HERE.md` before work.
- Coordinate parallel work through `AI_CONTEXT/TASKS.md` and `AI_CONTEXT/THREADS.md`.
- Do not let two chats edit the same area of `index.html` at the same time without explicit coordination.
- Keep `AI_CONTEXT/` updated when project facts, tasks, or decisions change.
