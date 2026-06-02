# Parallel Chat Registry

Use this file when running multiple Codex chats in the same project.

Important: all chats share the same physical folder unless the user creates separate git worktrees or project copies. Before editing code, each chat should claim a task and list the files or areas it expects to touch.

## Chat Slots

### Chat 1

Status: Paused
Current task: Completed mini-game drag jitter fix; click-to-move dots and `Skill Level 0..20` slider are also done.
Likely files/areas: `index.html`, `main.py`, `historic_games.json`
Last update: 2026-06-02

### Chat 2

Status: Paused
Current task: Completed Sparring mini-game arrow removal on branch `xxkurai`; no active task.
Likely files/areas:
Last update: 2026-06-02

### Chat 3

Status: Free
Current task:
Likely files/areas:
Last update:

## Conflict Rules

- Do not edit files already claimed by another active chat unless the user explicitly coordinates it.
- Before starting, read `TASKS.md` and this file.
- Before editing `index.html`, inspect current diff and check whether another chat has claimed frontend work.
- Before finishing, update your slot with result and next steps.
- If a chat becomes inactive, mark its status as `Paused` and leave a handoff note.
- For large independent tasks, prefer separate git worktrees or separate project copies so chats do not share one working tree.

## Suggested Chat Names

- `Chat 1 - Backend/API`
- `Chat 2 - Frontend/UI`
- `Chat 3 - QA/Tests/Docs`

These names are only suggestions. The important part is that each chat writes down what it owns.
