# Decision Log

Record durable decisions here so future chats do not re-litigate the same choices.

Use this format:

```text
## YYYY-MM-DD - Decision Title

Decision:
Reason:
Alternatives considered:
Impact:
```

## 2026-06-02 - Use `AI_CONTEXT/` As Shared Project Memory

Decision: Create a visible `AI_CONTEXT/` folder inside the project root.

Reason: Multiple Codex chats may work on the same project in parallel, and each chat needs a reliable source of shared context without requiring the user to re-explain the project.

Alternatives considered: relying on chat memory; a single root-level context file; hidden `.codex/` folder.

Impact: New chats should read `AI_CONTEXT/START_HERE.md` first and keep the context files updated as work progresses.

## 2026-06-02 - Treat `/Users/cight/Desktop/chess-analyzer` As The Active Project

Decision: The real project root is `/Users/cight/Desktop/chess-analyzer`.

Reason: The user clarified that the project is on the Desktop. This folder contains the git repository, README, backend, frontend, and run scripts.

Alternatives considered: `/Users/cight/Documents/ChessAdapter 2` and `/Users/cight/Documents/ChessAdapter`; those folders do not contain the active codebase.

Impact: Future chats should work in `/Users/cight/Desktop/chess-analyzer`, not the similarly named Documents folders.

