# Shared Task Board

Use this file to coordinate parallel Codex chats.

When a chat starts work, mark the task owner like this:

```text
Owner: Chat 1 / Chat 2 / Chat 3 / username / thread title
Status: In Progress
Files/areas:
```

## In Progress

## Backlog

### Define Parallel Work Split

Owner: Unassigned
Status: Backlog
Files/areas: `AI_CONTEXT/TASKS.md`, `AI_CONTEXT/THREADS.md`

Decide how to split work between 3 chats. Suggested split:

- Chat 1: Backend/API/Stockfish/Gemini in `main.py`
- Chat 2: Frontend/UI/interaction in `index.html`
- Chat 3: QA/tests/docs/run verification

### Inspect Existing `index.html` Changes

Owner: Unassigned
Status: Backlog
Files/areas: `index.html`

`index.html` was already modified when shared context was created. Inspect `git diff -- index.html` before any frontend edits.

### Verify Local Run

Owner: Unassigned
Status: Backlog
Files/areas: `run.sh`, `requirements.txt`, `main.py`

Run the app locally, confirm Stockfish availability, and record the result in `CURRENT_STATE.md`.

### Fill Product Priorities

Owner: Unassigned
Status: Backlog
Files/areas: `AI_CONTEXT/PROJECT.md`, `AI_CONTEXT/TASKS.md`

Ask/record the user's current top-priority features and bugs.

## Done

### Fix Mini-Game Drag Jitter

Owner: Chat 1 - Mini-games UI/API (`xxkurai`)
Status: Done
Date: 2026-06-02
Files/areas: `index.html`, `AI_CONTEXT/TASKS.md`, `AI_CONTEXT/THREADS.md`

Removed early pointer/mouse-down click handling from the mini-game board so dragging a piece no longer conflicts with click-to-move hints.

## Handoff - 2026-06-02 - Fix Mini-Game Drag Jitter

Owner: Chat 1 - Mini-games UI/API (`xxkurai`)
Status: Done

What changed:

- Removed `pointerdown` and `mousedown` mini-board click handlers that were mutating board DOM at the exact grab moment.
- Kept click-to-move working through safer post-grab events plus `onDragStart`.
- Added a short same-square guard so selecting a piece does not immediately clear its legal-move dots.

Files touched:

- `index.html`
- `AI_CONTEXT/TASKS.md`
- `AI_CONTEXT/THREADS.md`

Checks run:

- `python3 -m py_compile main.py`
- `git diff --check`
- Browser check on `http://127.0.0.1:8000`: click `e2`, dots appear on `e3/e4`, click `e4`, Stockfish replies.
- Browser check: drag `e2 -> e4` still plays a move and receives a Stockfish reply.
- Browser console check: no fresh warnings/errors.

Known issues:

- None for this fix.

Next steps:

- If visual shake remains on the user's machine, inspect whether it is the default chessboard.js centered drag ghost rather than event-handler jitter.

### Remove Sparring Mini-Game Arrows

Owner: Chat 2 - Frontend/UI (`xxkurai`)
Status: Done
Date: 2026-06-02
Files/areas: `index.html`, `AI_CONTEXT/TASKS.md`, `AI_CONTEXT/THREADS.md`

Removed last-move arrows from the Sparring mini-game while leaving the mini-game canvas clearing behavior intact.

## Handoff - 2026-06-02 - Remove Sparring Mini-Game Arrows

Owner: Chat 2 - Frontend/UI (`xxkurai`)
Status: Done

What changed:

- Updated `drawMiniArrow()` to clear the mini-game canvas and return immediately when `miniMode === 'classic'`.
- Kept non-Sparring mini-game arrow behavior unchanged.

Files touched:

- `index.html`
- `AI_CONTEXT/TASKS.md`
- `AI_CONTEXT/THREADS.md`

Checks run:

- `git diff --check`
- Local server on `PORT=8130 ./run.sh`
- Headless Chrome/CDP check: forced a last move in `classic`; `duelCanvas` alpha stayed `0`.
- Headless Chrome/CDP check: forced the same last move in `king_hill`; `duelCanvas` alpha was nonzero, confirming the change is scoped.

Known issues:

- Unrelated mini-games changes in `AI_CONTEXT/PROJECT.md`, `main.py`, `historic_games.json`, and `assets/` were already present and not touched here.

Next steps:

- None for Sparring arrows.

### Add Click-To-Move Dots To Mini-Games

Owner: Chat 1 - Mini-games UI/API (`xxkurai`)
Status: Done
Date: 2026-06-02
Files/areas: `index.html`, `AI_CONTEXT/TASKS.md`, `AI_CONTEXT/THREADS.md`

Replaced the mini-game board's ugly yellow move hinting with gray legal-move dots and added click-to-move.

## Handoff - 2026-06-02 - Add Click-To-Move Dots To Mini-Games

Owner: Chat 1 - Mini-games UI/API (`xxkurai`)
Status: Done

What changed:

- Suppressed chessboard.js yellow highlight classes inside `#duelBoard`.
- Added gray centered dots for quiet legal moves and subtle gray rings for captures.
- Added selected-square state for the mini-game board.
- Added click-to-move: click a white piece to show legal destinations, then click a destination square to play the move.
- Kept drag-and-drop working; dropping the same source/target no longer clears click hints.

Files touched:

- `index.html`
- `AI_CONTEXT/TASKS.md`
- `AI_CONTEXT/THREADS.md`

Checks run:

- `python3 -m py_compile main.py`
- `git diff --check`
- Browser check on `http://127.0.0.1:8000`: clicking `e2` shows 2 dots on `e3/e4`; clicking `e4` plays `1. e4` and receives a Stockfish reply.
- Browser check: drag `e2 -> e4` still plays the move and receives a Stockfish reply.
- Browser console check: no fresh warnings/errors during click or drag scenarios.

Known issues:

- None for this interaction change.

Next steps:

- Tune dot/ring opacity after visual review on the user's screen if desired.

### Center Analysis Board

Owner: Chat 2 - Frontend/UI (`xxkurai`)
Status: Done
Date: 2026-06-02
Files/areas: `index.html`, `AI_CONTEXT/TASKS.md`, `AI_CONTEXT/THREADS.md`

Centered the larger Analysis board visually in the viewport while keeping the eval slider beside it and preserving side panels.

## Handoff - 2026-06-02 - Center Analysis Board

Owner: Chat 2 - Frontend/UI (`xxkurai`)
Status: Done

What changed:

- Changed the Analysis grid to use symmetrical side columns around the board column.
- Made the board itself, not the board plus eval slider, define the visual center.
- Positioned the eval slider absolutely to the right of the board so it no longer offsets the board center.
- Added `min-height` to the board stage to prevent controls jumping while chessboard.js finishes rendering.

Files touched:

- `index.html`
- `AI_CONTEXT/TASKS.md`
- `AI_CONTEXT/THREADS.md`

Checks run:

- `git diff --check`
- Local server on `PORT=8130 ./run.sh`
- Headless Chrome screenshot at `2048x797`.
- CDP/DOM checks at `2048x797`, `1440x900`, `1280x720`, and `1024x500`: board center delta `0`, no horizontal page scroll.

Known issues:

- `AI_CONTEXT/PROJECT.md`, `main.py`, and `historic_games.json` already had unrelated mini-games changes and were not touched here.

Next steps:

- None for centering.

### Add Stockfish Skill Level Slider To Mini-Games

Owner: Chat 1 - Mini-games UI/API (`xxkurai`)
Status: Done
Date: 2026-06-02
Files/areas: `index.html`, `main.py`, `AI_CONTEXT/TASKS.md`, `AI_CONTEXT/THREADS.md`

Replaced the mini-games bot strength select with a Stockfish-native `Skill Level` slider.

## Handoff - 2026-06-02 - Add Stockfish Skill Level Slider To Mini-Games

Owner: Chat 1 - Mini-games UI/API (`xxkurai`)
Status: Done

What changed:

- Verified local Stockfish 18 UCI options: `Skill Level type spin default 20 min 0 max 20`.
- Replaced the old 4-option strength dropdown with a `0..20` range slider.
- Added a live `N/20` badge and `L<N>` bot label.
- Changed `/bot_move` to pass the selected value directly into `engine.configure({"Skill Level": skill})`.
- Removed the previous `1..10 -> *2` mapping.

Files touched:

- `index.html`
- `main.py`
- `AI_CONTEXT/TASKS.md`
- `AI_CONTEXT/THREADS.md`

Checks run:

- `printf 'uci\nquit\n' | /opt/homebrew/bin/stockfish`
- `python3 -m py_compile main.py`
- `git diff --check`
- `curl -X POST http://127.0.0.1:8000/bot_move ...` with `skill: 0` and `skill: 20`
- Browser check on `http://127.0.0.1:8000`: slider renders as `type=range`, min `0`, max `20`, default `10`, badge `10/20`; setting it to `20` updates badge to `20/20`, bot label to `L20`, and slider fill to `100%`.

Known issues:

- The in-app browser typing helper hit its virtual clipboard limitation when trying to type a move into the input field; backend and slider UI were still verified.

Next steps:

- If the user wants rating-like difficulty later, consider adding a separate Elo mode through Stockfish `UCI_LimitStrength` and `UCI_Elo` (`1320..3190` in local Stockfish 18).

### Increase Analysis Board Size

Owner: Chat 2 - Frontend/UI (`xxkurai`)
Status: Done
Date: 2026-06-02
Files/areas: `index.html`, `AI_CONTEXT/TASKS.md`, `AI_CONTEXT/THREADS.md`

Increased the main Analysis board size while keeping the evaluation bar, controls, and right analysis panel usable across desktop sizes.

## Handoff - 2026-06-02 - Increase Analysis Board Size

Owner: Chat 2 - Frontend/UI (`xxkurai`)
Status: Done

What changed:

- Added height-aware Analysis board sizing variables and expanded the analysis container width.
- Increased the board, eval slider, move navigation, variation panel, best-line panel, effect toggles, and evaluation chart to share the larger board width.
- Adjusted the desktop grid so the center board column can grow without squeezing the right analysis panel too hard.
- Added a `max-width: 1180px` single-column Analysis breakpoint to remove horizontal overflow on narrower desktop/tablet widths.
- Added a compact low-height desktop board formula for short screens.

Files touched:

- `index.html`
- `AI_CONTEXT/TASKS.md`
- `AI_CONTEXT/THREADS.md`

Checks run:

- `git diff --check`
- Local server on `PORT=8130 ./run.sh`
- Browser layout checks at `2048x797`, `1440x900`, `1280x720`, and `1024x500`.
- Confirmed larger Analysis board, no horizontal page scroll, and board navigation remains visible.

Known issues:

- `main.py` and `historic_games.json` already had unrelated changes from the mini-games task and were not touched here.

Next steps:

- Review after running a real analysis with the chart visible; if needed, the lower control stack can be made denser.

### Replace Attraction Tab With Stockfish Mini-Games

Owner: Chat 1 - Mini-games UI/API (`xxkurai`)
Status: Done
Date: 2026-06-02
Files/areas: `index.html`, `main.py`, `historic_games.json`, `AI_CONTEXT/TASKS.md`, `AI_CONTEXT/THREADS.md`

Replaced the old Attraction/Guess The Move tab with three playable mini-games against a simple Stockfish bot: Sparring, King of the Hill, and Blindfold.

## Handoff - 2026-06-02 - Replace Attraction Tab With Stockfish Mini-Games

Owner: Chat 1 - Mini-games UI/API (`xxkurai`)
Status: Done

What changed:

- Renamed the old Attraction nav tab to `Мини-игры`.
- Removed the old historical-duel UI from the tab and replaced it with three mini-game cards.
- Added a shared mini-game board, move input, new/flip/show controls, score/status panel, and move history.
- Added King of the Hill rules inspired by Lichess: a legal king move to d4/e4/d5/e5 wins.
- Added Blindfold mode by hiding pieces and allowing a short peek with `Показать`.
- Added `/bot_move` in `main.py` so Stockfish can reply to the user's moves.
- Deleted the old `historic_games.json` data file and removed its compatibility endpoint.

Files touched:

- `index.html`
- `main.py`
- `historic_games.json`
- `AI_CONTEXT/TASKS.md`
- `AI_CONTEXT/THREADS.md`

Checks run:

- `python3 -m py_compile main.py`
- `git diff --check`
- `curl http://127.0.0.1:8000/`
- `curl -X POST http://127.0.0.1:8000/bot_move ...` for classic and King of the Hill modes
- Browser check on `http://127.0.0.1:8000`: tab opens, 3 mode cards render, board has 64 squares, `e4` receives a Stockfish reply, console has no fresh warnings/errors.
- Browser check for King of the Hill and Blindfold: mode switching works, Blindfold hides pieces, `Показать` temporarily reveals them.

Known issues:

- The project working tree already contains unrelated uncommitted changes from parallel chats.

Next steps:

- Review the mini-game UX on the user's real screen and tune mode names/rules if needed.

### Increase Openings Board While Keeping Compact Layout

Owner: Chat 2 - Frontend/UI (`xxkurai`)
Status: Done
Date: 2026-06-02
Files/areas: `index.html`, `AI_CONTEXT/TASKS.md`, `AI_CONTEXT/THREADS.md`

Increased the Openings board size on desktop while preserving the compact no-inner-scroll layout.

## Handoff - 2026-06-02 - Increase Openings Board While Keeping Compact Layout

Owner: Chat 2 - Frontend/UI (`xxkurai`)
Status: Done

What changed:

- Increased the default Openings board size formula from a conservative `38vw`/`520px` cap to a larger height-aware desktop formula.
- Increased the medium-height desktop board size while keeping the ultra-low-height fallback compact.
- Added a focus layout up to `920px` height that hides secondary explanation sections and the move strip so board + navigation stay visible.
- Tightened the narrow desktop variation-column minimum so the larger board still has room beside it.

Files touched:

- `index.html`
- `AI_CONTEXT/TASKS.md`
- `AI_CONTEXT/THREADS.md`

Checks run:

- `git diff --check`
- Local server on `PORT=8130 ./run.sh`
- Browser layout checks at `2048x797`, `1440x900`, `1280x720`, and `1024x500`.
- Confirmed no horizontal page scroll, no internal opening guide scroll, and board navigation remains visible.

Known issues:

- `main.py` was already modified before this task and was not touched here.
- Lichess Explorer still shows the existing token warning when `LICHESS_TOKEN` is absent; unrelated to this layout sizing.

Next steps:

- Review on the user's real monitor; the board can be nudged a little larger only if hiding more secondary UI is acceptable.

### Make Openings View Fit Without Inner Board Scroll

Owner: Chat 2 - Frontend/UI (`xxkurai`)
Status: Done
Date: 2026-06-02
Files/areas: `index.html`, `AI_CONTEXT/TASKS.md`, `AI_CONTEXT/THREADS.md`

Reworked the Openings view spacing so the enlarged board, controls, and variations fit as one compact screen instead of making the opening guide card scroll internally.

## Handoff - 2026-06-02 - Make Openings View Fit Without Inner Board Scroll

Owner: Chat 2 - Frontend/UI (`xxkurai`)
Status: Done

What changed:

- Replaced the opening guide's internal vertical scrolling with visible overflow scoped only to `#viewOpenings`.
- Tuned Openings layout variables for panel height and board size so low-height desktop screens stay compact.
- Moved the Lichess Explorer block into the variations column to keep the board column focused on board + navigation.
- Hid lower-priority Openings details on low-height desktop screens so the board and primary lines remain visible.
- Reduced Openings title, line, card, filter, and control spacing for compact desktop layouts.

Files touched:

- `index.html`
- `AI_CONTEXT/TASKS.md`
- `AI_CONTEXT/THREADS.md`

Checks run:

- `git diff --check`
- Local server on `PORT=8130 ./run.sh`
- Browser layout check at `1024x500`: no page vertical scroll, no horizontal scroll, no internal opening guide scroll, board/nav visible.
- Browser layout check at `1280x720`: no page vertical scroll, no horizontal scroll, no internal opening guide scroll, board/nav visible.

Known issues:

- `main.py` was already modified before this task and was not touched here.
- Lichess Explorer still shows the existing token warning when `LICHESS_TOKEN` is absent; unrelated to this layout fix.

Next steps:

- Review the layout on the user's full desktop viewport and adjust max board size if they want the board even larger.

### Replace Evaluation Chart Text Legend

Owner: Chat 2 - Frontend/UI (`xxkurai`)
Status: Done
Date: 2026-06-02
Files/areas: `index.html`, `AI_CONTEXT/TASKS.md`, `AI_CONTEXT/THREADS.md`

Removed the wordy `Верх/Низ` chart legend and replaced it with an in-chart visual side rail: white marker at the top, green equality marker in the middle, and black marker at the bottom.

## Handoff - 2026-06-02 - Replace Evaluation Chart Text Legend

Owner: Chat 2 - Frontend/UI (`xxkurai`)
Status: Done

What changed:

- Removed the `eval-chart-legend` text row.
- Added a compact visual rail inside the chart canvas area.
- Added nonverbal white/equal/black markers using side color and chess king symbols.

Files touched:

- `index.html`
- `AI_CONTEXT/TASKS.md`
- `AI_CONTEXT/THREADS.md`

Checks run:

- `git diff --check`
- Local server on `PORT=8130 ./run.sh`
- Browser analysis with PGN `1. f4 e6 2. g4 Qh4#`
- Browser DOM check: `legendCount: 0`, `markerCount: 2`, zero marker present.
- Browser console error check: no errors.

Known issues:

- None for this legend replacement.

Next steps:

- If desired, tune marker icons/colors after viewing on the user's actual screen.

### Fix Engine Best Move Arrow Fill

Owner: Chat 2 - Frontend/UI (`xxkurai`)
Status: Done
Date: 2026-06-02
Files/areas: `index.html`, `AI_CONTEXT/TASKS.md`, `AI_CONTEXT/THREADS.md`

Removed the dashed rendering from the blue Stockfish best-move arrow so it appears as a solid filled arrow with a soft halo instead of rounded oval segments.

## Handoff - 2026-06-02 - Fix Engine Best Move Arrow Fill

Owner: Chat 2 - Frontend/UI (`xxkurai`)
Status: Done

What changed:

- Removed `dash: [10, 7]` from the Stockfish best-move arrow call.
- Slightly increased the arrow halo width to keep the blue recommendation visually distinct from the green played-move arrow.

Files touched:

- `index.html`
- `AI_CONTEXT/TASKS.md`
- `AI_CONTEXT/THREADS.md`

Checks run:

- `git diff --check`
- Local server on `PORT=8130 ./run.sh`
- Browser analysis with PGN `1. f4 e6 2. g4 Qh4#`
- Visual check on move `2. g4`: blue best-move arrow is solid, not dashed/oval.

Known issues:

- `index.html` still includes broader pre-existing uncommitted frontend changes.

Next steps:

- None for this arrow-fill fix.

### Redesign Analysis Evaluation Chart

Owner: Chat 2 - Frontend/UI (`xxkurai`)
Status: Done
Date: 2026-06-02
Files/areas: `index.html`, `AI_CONTEXT/TASKS.md`, `AI_CONTEXT/THREADS.md`

Redesigned the Analyze view Stockfish evaluation chart into a site-matched card with clearer labels, white/black advantage framing, richer Chart.js hover details, and move-chip native tooltips.

## Handoff - 2026-06-02 - Redesign Analysis Evaluation Chart

Owner: Chat 2 - Frontend/UI (`xxkurai`)
Status: Done

What changed:

- Replaced the old Lichess-styled chart wrapper with a dedicated evaluation chart card.
- Added summary text that updates on current move and chart hover.
- Updated Chart.js tooltip to show move number, side, SAN, evaluation, narrative advantage, category, and CPL loss when relevant.
- Added point markers for important move categories.
- Added native hover titles to move chips.
- Clarified chart orientation with `Верх: белые лучше` and `Низ: черные лучше`.

Files touched:

- `index.html`
- `AI_CONTEXT/TASKS.md`
- `AI_CONTEXT/THREADS.md`

Checks run:

- `git diff --check`
- Local server on `PORT=8130 ./run.sh`
- Browser analysis with test PGN `1. e4 e5 2. Nf3 Nc6 3. Bc4 d6 4. Nc3 Bg4 5. h3 Bh5 6. Nxe5 Bxd1 7. Bxf7+ Ke7 8. Nd5#`
- Browser hover check: summary changed to `На графике · 6. Белые Nxe5 · +1.9 Блестящий · Преимущество белых`.
- Browser console error check: no errors.

Known issues:

- `index.html` still includes broader pre-existing uncommitted frontend changes.
- Gemini/Lichess token warnings are unrelated to this chart task.

Next steps:

- Review with a longer real game to tune chart density if needed.

### Reduce Report Glow And Gloss

Owner: Chat 2 - Frontend/UI (`xxkurai`)
Status: Done
Date: 2026-06-02
Files/areas: `index.html`, `AI_CONTEXT/TASKS.md`, `AI_CONTEXT/THREADS.md`

Reduced the brightness of report highlights, badge glows, card reflections, and text/progress shadows so the UI feels calmer and less glossy.

## Handoff - 2026-06-02 - Reduce Report Glow And Gloss

Owner: Chat 2 - Frontend/UI (`xxkurai`)
Status: Done

What changed:

- Lowered radial highlight opacity on accuracy cards and badges.
- Reduced text shadows on accuracy percentages.
- Reduced progress-bar glow.
- Removed outer colored glow from category chips, category report badges, stage badges, and AI badges.
- Kept subtle depth through borders and dark shadows.

Files touched:

- `index.html`
- `AI_CONTEXT/TASKS.md`
- `AI_CONTEXT/THREADS.md`

Checks run:

- `git diff --check`
- Headless Chrome visual check of the report accuracy + category section.

Known issues:

- `index.html` still includes broader pre-existing uncommitted frontend changes.

Next steps:

- Review in the live app after a real analysis to tune one more notch if needed.

### Differentiate Played And Best Move Arrows

Owner: Chat 2 - Frontend/UI (`xxkurai`)
Status: Done
Date: 2026-06-02
Files/areas: `index.html`, `AI_CONTEXT/TASKS.md`, `AI_CONTEXT/THREADS.md`

Made played-move arrows and Stockfish best-move arrows visually distinct: played moves are solid green, while Stockfish suggestions are blue with a pale halo and dashed shaft.

## Handoff - 2026-06-02 - Differentiate Played And Best Move Arrows

Owner: Chat 2 - Frontend/UI (`xxkurai`)
Status: Done

What changed:

- Replaced near-identical green arrow constants with `ARROW_PLAYED`, `ARROW_ENGINE_BEST`, and `ARROW_ENGINE_BEST_HALO`.
- Extended `drawArrow` with optional halo, alpha, and dash styling.
- Kept played/user arrows solid green.
- Made Stockfish best-move arrows blue, dashed, and haloed for clear contrast.

Files touched:

- `index.html`
- `AI_CONTEXT/TASKS.md`
- `AI_CONTEXT/THREADS.md`

Checks run:

- `git diff --check`
- Headless Chrome visual check of both arrow styles on a chessboard-colored background.

Known issues:

- `index.html` still includes broader pre-existing uncommitted frontend changes.

Next steps:

- Review during a real blunder/mistake position where both arrows appear over actual pieces.

### Rework Move Category Badges

Owner: Chat 2 - Frontend/UI (`xxkurai`)
Status: Done
Date: 2026-06-02
Files/areas: `index.html`, `AI_CONTEXT/TASKS.md`, `AI_CONTEXT/THREADS.md`

Replaced emoji-style report category icons, stage icons, button symbols, and coach faces with calmer typographic badges and AI/status markers.

## Handoff - 2026-06-02 - Rework Move Category Badges

Owner: Chat 2 - Frontend/UI (`xxkurai`)
Status: Done

What changed:

- Replaced category emoji icons with typographic markers: `!!`, `!`, `★`, `✓`, `+`, `B`, `?!`, `?`, `×`, `??`.
- Reworked category badge colors to use shared CSS variables, darker surfaces, thin borders, and soft glows.
- Replaced stage breakdown emoji with compact status badges.
- Replaced coach face emoji with an `AI` / `!` / `B` / `✓` status token.
- Replaced remaining emoji in primary report controls with cleaner text symbols.

Files touched:

- `index.html`
- `AI_CONTEXT/TASKS.md`
- `AI_CONTEXT/THREADS.md`

Checks run:

- `rg -n -P "[\\x{1F300}-\\x{1FAFF}]" index.html`
- `git diff --check`
- Headless Chrome visual check of the category grid.

Known issues:

- `index.html` still includes broader pre-existing uncommitted frontend changes.

Next steps:

- Review the full report after a real PGN analysis to judge the new badges in context.

### Rework Game Report Accuracy Card Colors

Owner: Chat 2 - Frontend/UI (`xxkurai`)
Status: Done
Date: 2026-06-02
Files/areas: `index.html`, `AI_CONTEXT/TASKS.md`, `AI_CONTEXT/THREADS.md`

Replaced the harsh orange/green/purple accuracy card palette with side-based accents: White uses a soft porcelain/mint treatment, Black uses a muted lavender treatment, and progress bars are no longer tied to winner/loser classes.

## Handoff - 2026-06-02 - Rework Game Report Accuracy Card Colors

Owner: Chat 2 - Frontend/UI (`xxkurai`)
Status: Done

What changed:

- Updated `.players-accuracy` and `.player-acc-block` styling in `index.html`.
- Accuracy percentages inside the report now inherit side-specific colors instead of score status colors.
- Progress bars now use side-specific CSS variables instead of `.winner` / `.loser` colors.

Files touched:

- `index.html`
- `AI_CONTEXT/TASKS.md`
- `AI_CONTEXT/THREADS.md`

Checks run:

- Confirmed the existing FastAPI server responds on `http://127.0.0.1:8000`.
- Captured a headless Chrome visual check of the accuracy block with `81.9% / 86.9%`.

Known issues:

- `index.html` still includes broader pre-existing uncommitted frontend changes.

Next steps:

- Review in the full app after running a real PGN analysis.

### Increase Openings Board Size And Rebalance Layout

Owner: Chat 2 - Frontend/UI (`xxkurai`)
Status: Done
Date: 2026-06-02
Files/areas: `index.html`, `AI_CONTEXT/TASKS.md`, `AI_CONTEXT/THREADS.md`

Made the Openings view use wide desktop space more efficiently: expanded the overall container, narrowed the sidebar range, made the Openings panels viewport-height aware, increased `#openingBoard` from 360px to 560px on roomy screens, and added a medium-screen breakpoint so variations move below the board instead of squeezing it.

## Handoff - 2026-06-02 - Increase Openings Board Size And Rebalance Layout

Owner: Chat 2 - Frontend/UI (`xxkurai`)
Status: Done

What changed:

- Rebalanced Openings grid columns and panel heights.
- Increased the Openings board to 560px on desktop.
- Added responsive fallback for medium screens to avoid horizontal overflow.

Files touched:

- `index.html`
- `AI_CONTEXT/TASKS.md`
- `AI_CONTEXT/THREADS.md`

Checks run:

- `git diff --check`
- Local server on `PORT=8130 ./run.sh`
- Browser layout check at 2048x1000: board measured 560px wide, no horizontal overflow.
- Browser layout check at 1024x800: board measured 560px wide, variations moved below board, no horizontal overflow.

Known issues:

- `index.html` still has pre-existing uncommitted changes unrelated to this board layout task.
- Lichess Explorer can still show 401 without `LICHESS_TOKEN`; unrelated to layout.

Next steps:

- Commit/push the branch after reviewing all uncommitted frontend changes.

### Create Shared AI Context Folder

Owner: Current chat
Status: Done
Date: 2026-06-02
Files/areas: `AGENTS.md`, `AI_CONTEXT/`

Created shared memory and coordination files in `/Users/cight/Desktop/chess-analyzer`.
