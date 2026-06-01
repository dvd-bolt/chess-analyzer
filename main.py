"""
Chess Analyzer Backend — Этап 1
Базовый сервер FastAPI: приём PGN, парсинг ходов, подключение к Stockfish.
"""

import io

import chess
import chess.engine
import chess.pgn
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

# ---------------------------------------------------------------------------
# App & CORS
# ---------------------------------------------------------------------------
app = FastAPI(
    title="Chess Analyzer API",
    description="Веб-приложение для анализа шахматных партий",
    version="0.1.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------
STOCKFISH_PATH = "stockfish/stockfish.exe"

# ---------------------------------------------------------------------------
# Models
# ---------------------------------------------------------------------------

class PGNRequest(BaseModel):
    pgn: str


# ---------------------------------------------------------------------------
# Endpoints
# ---------------------------------------------------------------------------

@app.post("/analyze")
def analyze(request: PGNRequest):
    """
    Принимает PGN-строку, парсит партию и возвращает список ходов в формате SAN.
    Подключается к Stockfish (пока без логики оценки CPL).
    """
    # --- 1. Парсинг PGN ---
    game = chess.pgn.read_game(io.StringIO(request.pgn))
    if game is None:
        raise HTTPException(status_code=400, detail="Не удалось распарсить PGN")

    # --- 2. Сбор ходов в SAN ---
    moves_san: list[str] = []
    board = game.board()
    for move in game.mainline_moves():
        moves_san.append(board.san(move))
        board.push(move)

    # --- 3. Подключение к Stockfish (проверка работоспособности) ---
    engine = None
    try:
        engine = chess.engine.SimpleEngine.popen_uci(STOCKFISH_PATH)
        # TODO: Этап 2 — реализовать расчёт CPL для каждого хода
    except Exception as exc:
        # Движок может отсутствовать на этапе разработки — не блокируем ответ
        print(f"[WARNING] Не удалось запустить Stockfish: {exc}")
    finally:
        if engine is not None:
            engine.quit()

    # --- 4. Ответ ---
    return {"moves": moves_san}
