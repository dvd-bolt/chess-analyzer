# Start Here For Any Codex Chat

This folder is the shared project memory for parallel Codex chats.

Every new chat should start by reading these files, in this order:

1. `AI_CONTEXT/START_HERE.md`
2. `AI_CONTEXT/PROJECT.md`
3. `AI_CONTEXT/CURRENT_STATE.md`
4. `AI_CONTEXT/TASKS.md`
5. `AI_CONTEXT/THREADS.md`
6. `AI_CONTEXT/DECISIONS.md`

Goal: avoid re-explaining the project in every new thread.

## Quick Prompt For New Chats

Paste this at the start of any new Codex chat:

```text
Read AI_CONTEXT/START_HERE.md first, then follow the project memory protocol.
Use AI_CONTEXT as the source of shared context for this project.
Before changing code, check AI_CONTEXT/TASKS.md and AI_CONTEXT/THREADS.md, then update your task ownership.
```

## Working Protocol

Before starting a task:

1. Read the files listed above.
2. Check `AI_CONTEXT/TASKS.md`.
3. Register or update your chat in `AI_CONTEXT/THREADS.md`.
4. Add your chat/thread name to the task you are working on.
5. If the task is not listed, add it under `Backlog` or `In Progress`.

During work:

1. Keep changes scoped.
2. Do not overwrite unrelated user changes.
3. If you discover important project facts, add them to `PROJECT.md` or `CURRENT_STATE.md`.
4. If you make an architectural or product decision, add it to `DECISIONS.md`.

Before ending a task:

1. Update `TASKS.md` with status and next steps.
2. Add a short handoff note using `HANDOFF_TEMPLATE.md`.
3. Mention any tests/checks that passed or could not be run.

## Folder Rules

- `PROJECT.md` is for durable context: product goal, architecture, stack, important files.
- `CURRENT_STATE.md` is for current state: what works, what is broken, how to run, recent progress.
- `TASKS.md` is for parallel coordination across chats.
- `THREADS.md` is for active chat/thread ownership and conflict prevention.
- `DECISIONS.md` is for decisions and why they were made.
- `HANDOFF_TEMPLATE.md` is copied into task notes when a chat stops or finishes work.

