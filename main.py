"""
Chess Analyzer Backend — Этап 5 (MVP)
Полный анализ CPL, эвристика «бриллиантовых» ходов,
интеграция Chess.com API, комментарии Gemini AI.
"""

import io
import json
import os

# Перенаправляем все системные запросы Python на стабильный HTTP-порт нашего VPN
os.environ["HTTP_PROXY"] = "http://127.0.0.1:10809"
os.environ["HTTPS_PROXY"] = "http://127.0.0.1:10809"
os.environ["ALL_PROXY"] = "http://127.0.0.1:10809"
os.environ["http_proxy"] = "http://127.0.0.1:10809"
os.environ["https_proxy"] = "http://127.0.0.1:10809"
os.environ["all_proxy"] = "http://127.0.0.1:10809"

import re
from pathlib import Path
from typing import Optional

import chess
import chess.engine
import chess.pgn
from google import genai
import requests
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from pydantic import BaseModel

# ---------------------------------------------------------------------------
# Environment & Gemini
# ---------------------------------------------------------------------------
load_dotenv()

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
gemini_client = None
if GEMINI_API_KEY and GEMINI_API_KEY != "PLACEHOLDER":
    gemini_client = genai.Client(api_key=GEMINI_API_KEY)

# ---------------------------------------------------------------------------
# App & CORS
# ---------------------------------------------------------------------------
app = FastAPI(
    title="Chess Analyzer API",
    description="Веб-приложение для анализа шахматных партий с ИИ-тренером",
    version="1.0.0",
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
BASE_DIR = Path(__file__).resolve().parent

PIECE_VALUES = {
    chess.PAWN: 1,
    chess.KNIGHT: 3,
    chess.BISHOP: 3,
    chess.ROOK: 5,
    chess.QUEEN: 9,
}

MATE_SCORE = 10_000

CHESSCOM_HEADERS = {
    "User-Agent": "ChessAnalyzerApp/1.0 (educational project)",
}

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


def format_score_display(score: chess.engine.Score, pov: chess.Color) -> str:
    """
    Формат оценки для отображения: если мат, то '#M2' / '#-M3',
    иначе — обычные сантипешки.
    """
    relative = score.pov(pov)
    mate = relative.mate()
    if mate is not None:
        sign = "" if mate >= 0 else "-"
        return f"#{sign}M{abs(mate)}"
    cp = relative.score()
    if cp is None:
        return "0"
    return str(cp)


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


def ask_gemini(game_log: list[dict]) -> dict[int, str]:
    """
    Отправляет полный лог партии в Gemini одним запросом.
    Возвращает dict {index: comment}.
    """
    if gemini_client is None:
        return {}

    prompt = (
        "Ты — опытный шахматный тренер, который обучает новичка (рейтинг ~400 Elo). "
        "Я передаю тебе JSON со всей историей партии и оценками движка Stockfish. "
        "Изучи партию целиком, пойми стратегические планы сторон "
        "(обрати внимание, если это Староиндийская защита/нападение) "
        "и напиши ОДНО короткое, емкое предложение-комментарий на русском языке "
        "к КАЖДОМУ ходу. Объясняй человеческим языком: зачем сделан ход, "
        "какую угрозу он несет, почему движку не нравится неточность или "
        "в чем гениальность жертвы (бриллианта). "
        "Верни ответ СТРОГО в формате JSON, где ключи — индексы ходов (числа), "
        "а значения — твои комментарии-советы. Ничего кроме JSON не пиши.\n\n"
        f"```json\n{json.dumps(game_log, ensure_ascii=False)}\n```"
    )

    try:
        response = gemini_client.models.generate_content(
            model='gemini-2.0-flash',
            contents=prompt,
            config={'response_mime_type': 'application/json'},
        )
        text = response.text.strip()
        # Подстраховка: убираем ```json ... ``` если модель всё равно обернула
        text = re.sub(r"^```(?:json)?\s*\n?", "", text, flags=re.DOTALL)
        text = re.sub(r"\n?\s*```\s*$", "", text, flags=re.DOTALL)
        text = text.strip()
        parsed = json.loads(text)
        print(f"[INFO] Gemini вернул комментарии к {len(parsed)} ходам")
        return {int(k): str(v) for k, v in parsed.items()}
    except Exception as exc:
        raw = ""
        try:
            raw = response.text[:500]
        except Exception:
            raw = "(не удалось получить текст ответа)"
        print(f"[ERROR] Gemini error: {exc}")
        print(f"[ERROR] Gemini raw response: {raw}")
        return {}


# ---------------------------------------------------------------------------
# Models
# ---------------------------------------------------------------------------


class PGNRequest(BaseModel):
    pgn: str


# ---------------------------------------------------------------------------
# Endpoints
# ---------------------------------------------------------------------------


@app.get("/", response_class=FileResponse)
def index():
    """Отдаёт главную HTML-страницу."""
    return FileResponse(BASE_DIR / "index.html", media_type="text/html")


@app.get("/get_latest_game/{username}")
def get_latest_game(username: str):
    """
    Получает последнюю партию игрока с Chess.com и возвращает PGN.
    """
    # 1. Получаем список архивов
    archives_url = f"https://api.chess.com/pub/player/{username}/games/archives"
    try:
        resp = requests.get(archives_url, headers=CHESSCOM_HEADERS, timeout=10)
        resp.raise_for_status()
    except requests.RequestException as exc:
        raise HTTPException(
            status_code=502,
            detail=f"Не удалось подключиться к Chess.com: {exc}",
        )

    archives = resp.json().get("archives", [])
    if not archives:
        raise HTTPException(
            status_code=404,
            detail=f"У игрока '{username}' не найдено партий на Chess.com",
        )

    # 2. Берём самый свежий месяц
    latest_url = archives[-1]
    try:
        resp = requests.get(latest_url, headers=CHESSCOM_HEADERS, timeout=10)
        resp.raise_for_status()
    except requests.RequestException as exc:
        raise HTTPException(status_code=502, detail=f"Ошибка загрузки партий: {exc}")

    games = resp.json().get("games", [])
    if not games:
        raise HTTPException(
            status_code=404,
            detail="В последнем месяце нет партий",
        )

    # 3. Последняя партия
    last_game = games[-1]
    pgn_text = last_game.get("pgn", "")
    if not pgn_text:
        raise HTTPException(status_code=404, detail="PGN последней партии пуст")

    return {"pgn": pgn_text, "url": last_game.get("url", "")}


@app.post("/analyze")
def analyze(request: PGNRequest):
    """
    Принимает PGN-строку, анализирует каждый ход движком Stockfish,
    запрашивает комментарии у Gemini и возвращает полный отчёт.
    """
    # --- 1. Парсинг PGN ---
    game = chess.pgn.read_game(io.StringIO(request.pgn))
    if game is None:
        raise HTTPException(status_code=400, detail="Не удалось распарсить PGN")

    # --- 2. Анализ ходов ---
    moves_data: list[dict] = []
    game_log: list[dict] = []  # для Gemini
    board = game.board()
    engine: Optional[chess.engine.SimpleEngine] = None

    try:
        engine = chess.engine.SimpleEngine.popen_uci(STOCKFISH_PATH)
        move_index = 0

        for move in game.mainline_moves():
            side = board.turn
            san = board.san(move)

            # Оценка ДО хода
            info_before = engine.analyse(board, chess.engine.Limit(time=0.2))
            cp_before = score_to_cp(info_before["score"], side)

            # Материал ДО хода
            material_before = get_material_value(board, side)

            # Делаем ход
            board.push(move)

            # Оценка ПОСЛЕ хода
            info_after = engine.analyse(board, chess.engine.Limit(time=0.2))
            cp_after = score_to_cp(info_after["score"], side)

            # Материал ПОСЛЕ хода
            material_after = get_material_value(board, side)

            # CPL
            cpl = max(0, cp_before - cp_after)

            # Категоризация
            category, icon = categorize_move(cpl)

            # 💎 Бриллиантовый ход
            if cpl <= 15 and material_after < material_before:
                category = "Бриллиантовый"
                icon = "💎"

            # Оценка для графика (от белых)
            eval_white = score_to_cp(info_after["score"], chess.WHITE)

            # Формат оценки с матом
            score_display = format_score_display(info_after["score"], chess.WHITE)

            moves_data.append(
                {
                    "san": san,
                    "color": "white" if side == chess.WHITE else "black",
                    "cpl": cpl,
                    "eval": eval_white,
                    "score_display": score_display,
                    "category": category,
                    "icon": icon,
                    "comment": "",  # заполним из Gemini
                }
            )

            # Лог для Gemini
            game_log.append(
                {
                    "index": move_index,
                    "san": san,
                    "color": "white" if side == chess.WHITE else "black",
                    "score": score_display,
                    "cpl": cpl,
                    "category": category,
                }
            )

            move_index += 1

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

    # --- 3. Комментарии Gemini ---
    comments = ask_gemini(game_log)
    for idx, comment in comments.items():
        if 0 <= idx < len(moves_data):
            moves_data[idx]["comment"] = comment

    # --- 4. Ответ ---
    return {"moves_data": moves_data}
