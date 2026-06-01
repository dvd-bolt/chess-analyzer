"""
Chess Analyzer Backend — Этап 2
Анализ CPL (Centipawn Loss), подсчёт материала, категоризация ходов,
эвристика «бриллиантовых» ходов.
"""

import io
from typing import Optional

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
    version="0.2.0",
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

PIECE_VALUES = {
    chess.PAWN: 1,
    chess.KNIGHT: 3,
    chess.BISHOP: 3,
    chess.ROOK: 5,
    chess.QUEEN: 9,
}

MATE_SCORE = 10_000  # сантипешки, заменяющие мат


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def get_material_value(board: chess.Board, color: chess.Color) -> int:
    """Суммарная ценность фигур указанного цвета (без короля)."""
    value = 0
    for piece_type, worth in PIECE_VALUES.items():
        value += len(board.pieces(piece_type, color)) * worth
    return value


def score_to_cp(score: chess.engine.Score, pov: chess.Color) -> int:
    """
    Преобразует объект Score в целые сантипешки с точки зрения *pov*.
    Мат приравнивается к ±MATE_SCORE.
    """
    relative = score.pov(pov)
    cp = relative.score(mate_score=MATE_SCORE)
    if cp is None:
        return 0
    return cp


def categorize_move(cpl: int) -> tuple[str, str]:
    """Возвращает (категория, иконка) по величине CPL."""
    if cpl <= 15:
        return "Отличный", "🌟"
    if cpl <= 50:
        return "Хороший", "✅"
    if cpl <= 100:
        return "Неточность", "⁉️"
    if cpl <= 300:
        return "Ошибка", "❓"
    return "Зевок", "🤡"


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
    Принимает PGN-строку, анализирует каждый ход движком Stockfish и
    возвращает список с оценкой CPL, категорией и иконкой для каждого хода.
    """
    # --- 1. Парсинг PGN ---
    game = chess.pgn.read_game(io.StringIO(request.pgn))
    if game is None:
        raise HTTPException(status_code=400, detail="Не удалось распарсить PGN")

    # --- 2. Анализ ходов ---
    moves_data: list[dict] = []
    board = game.board()
    engine: Optional[chess.engine.SimpleEngine] = None

    try:
        engine = chess.engine.SimpleEngine.popen_uci(STOCKFISH_PATH)

        for move in game.mainline_moves():
            # Чей ход
            side = board.turn  # WHITE или BLACK
            san = board.san(move)

            # Оценка ДО хода (с точки зрения стороны, делающей ход)
            info_before = engine.analyse(board, chess.engine.Limit(time=0.2))
            cp_before = score_to_cp(info_before["score"], side)

            # Материал ДО хода
            material_before = get_material_value(board, side)

            # Делаем ход
            board.push(move)

            # Оценка ПОСЛЕ хода (с точки зрения той же стороны)
            info_after = engine.analyse(board, chess.engine.Limit(time=0.2))
            cp_after = score_to_cp(info_after["score"], side)

            # Материал ПОСЛЕ хода
            material_after = get_material_value(board, side)

            # CPL = насколько оценка упала после хода (>= 0)
            cpl = max(0, cp_before - cp_after)

            # Категоризация
            category, icon = categorize_move(cpl)

            # 💎 Бриллиантовый ход: жертва материала без потери оценки
            if cpl <= 15 and material_after < material_before:
                category = "Бриллиантовый"
                icon = "💎"

            moves_data.append(
                {
                    "san": san,
                    "color": "white" if side == chess.WHITE else "black",
                    "cpl": cpl,
                    "category": category,
                    "icon": icon,
                }
            )

    except FileNotFoundError:
        raise HTTPException(
            status_code=503,
            detail=f"Движок Stockfish не найден по пути: {STOCKFISH_PATH}",
        )
    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail=f"Ошибка при анализе: {exc}",
        )
    finally:
        if engine is not None:
            engine.quit()

    # --- 3. Ответ ---
    return {"moves_data": moves_data}
