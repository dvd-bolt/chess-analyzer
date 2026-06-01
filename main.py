"""
Chess Analyzer Backend — Этап 6 (Game Report)
Полный анализ CPL, точность, счетчики категорий, эвристика «бриллиантовых» ходов,
интеграция Chess.com API, комментарии Gemini AI + оценка ELO.
"""

import io
import json
import os

import urllib.request
urllib.request.getproxies = lambda: {}

import math
import re
from pathlib import Path
from typing import Optional

import chess
import chess.engine
import chess.pgn
from google import genai
from google.genai import types
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
    gemini_client = genai.Client(
        api_key=GEMINI_API_KEY,
        http_options=types.HttpOptions(
            client_args={'http2': False}
        )
    )

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


# --- 10-категорийная классификация ходов (Chess.com style) ---
CATEGORIES = [
    # (max_cpl, key, label_ru, icon)
    (0,   "brilliant",  "Блестящий",           "!!"),
    (0,   "great",      "Замечательный",       "!"),
    (0,   "best",       "Лучший",              "⭐"),
    (5,   "excellent",  "Отлично",             "👍"),
    (20,  "good",       "Хорошо",              "✅"),
    (0,   "book",       "Теоретический",       "📖"),
    (80,  "inaccuracy", "Неточность",          "?!"),
    (200, "mistake",    "Ошибка",              "?"),
    (0,   "miss",       "Упущение",            "❌"),
    (999999, "blunder", "Зевок",               "??"),
]

CAT_KEYS = [c[1] for c in CATEGORIES]


def categorize_move(
    cpl: int,
    *,
    is_sacrifice: bool = False,
    is_best_move: bool = False,
    is_book: bool = False,
    had_advantage_before: bool = False,
) -> tuple[str, str, str]:
    """Возвращает (key, label_ru, icon) по CPL и эвристикам."""
    if is_book:
        return "book", "Теоретический", "📖"
    if cpl <= 0 and is_sacrifice:
        return "brilliant", "Блестящий", "!!"
    if cpl <= 0 and is_best_move:
        return "best", "Лучший", "⭐"
    if cpl <= 5:
        return "excellent", "Отлично", "👍"
    if cpl <= 20:
        return "good", "Хорошо", "✅"
    if cpl <= 80:
        return "inaccuracy", "Неточность", "?!"
    if cpl <= 200:
        return "mistake", "Ошибка", "?"
    return "blunder", "Зевок", "??"


def estimate_elo(accuracy: float) -> int:
    """Грубая оценка ELO по точности партии."""
    if accuracy >= 98: return 2700
    if accuracy >= 95: return 2200
    if accuracy >= 90: return 1800
    if accuracy >= 85: return 1500
    if accuracy >= 78: return 1200
    if accuracy >= 70: return 1000
    if accuracy >= 60: return 800
    if accuracy >= 45: return 600
    return 400


def get_total_material(board: chess.Board) -> int:
    """Суммарная ценность фигур обеих сторон (без королей)."""
    v = 0
    for pt, w in PIECE_VALUES.items():
        v += len(board.pieces(pt, chess.WHITE)) * w
        v += len(board.pieces(pt, chess.BLACK)) * w
    return v


def detect_stage(move_index: int, total_material: int) -> str:
    """Определяет стадию партии."""
    if move_index < 20:  # первые ~10 ходов (20 полуходов)
        return "opening"
    if total_material <= 24:  # мало фигур → эндшпиль
        return "endgame"
    return "middlegame"


def compute_stats(moves_data: list[dict]) -> dict:
    """Рассчитывает точность, счётчики, стадии и ELO для обеих сторон."""
    side_cpls = {"white": [], "black": []}
    cats = {"white": {k: 0 for k in CAT_KEYS}, "black": {k: 0 for k in CAT_KEYS}}
    stage_cpls = {
        "white": {"opening": [], "middlegame": [], "endgame": []},
        "black": {"opening": [], "middlegame": [], "endgame": []},
    }

    for m in moves_data:
        color = m["color"]
        cpl = m["cpl"]
        side_cpls[color].append(cpl)
        cat_key = m.get("cat_key", "good")
        if cat_key in cats[color]:
            cats[color][cat_key] += 1
        stage = m.get("stage", "middlegame")
        stage_cpls[color][stage].append(cpl)

    def accuracy(cpls: list) -> float:
        if not cpls:
            return 100.0
        avg = sum(cpls) / len(cpls)
        return round(min(100.0, max(0.0, 100.0 * math.exp(-0.005 * avg))), 1)

    def stage_verdict(cpls: list) -> str:
        acc = accuracy(cpls)
        if acc >= 90:
            return "check"
        if acc >= 70:
            return "thumb"
        return "inaccuracy"

    result = {}
    for color in ("white", "black"):
        acc = accuracy(side_cpls[color])
        result[color] = {
            "accuracy": acc,
            "avg_cpl": round(sum(side_cpls[color]) / len(side_cpls[color]), 1) if side_cpls[color] else 0,
            "moves": len(side_cpls[color]),
            "elo": estimate_elo(acc),
            **cats[color],
            "stages": {
                "opening": stage_verdict(stage_cpls[color]["opening"]),
                "middlegame": stage_verdict(stage_cpls[color]["middlegame"]),
                "endgame": stage_verdict(stage_cpls[color]["endgame"]),
            },
        }
    return result


def ask_gemini(game_log: list[dict], stats: dict) -> dict:
    """
    Отправляет полный лог партии в Gemini.
    Возвращает dict с ключами: числовые индексы → комментарии,
    elo_verdict → строка, coach_summary → строка.
    """
    if gemini_client is None:
        return {}

    stats_summary = (
        f"Статистика партии:\n"
        f"Белые: точность {stats['white']['accuracy']}%, "
        f"ELO ~{stats['white']['elo']}, "
        f"зевков {stats['white']['blunder']}, ошибок {stats['white']['mistake']}, "
        f"неточностей {stats['white']['inaccuracy']}.\n"
        f"Чёрные: точность {stats['black']['accuracy']}%, "
        f"ELO ~{stats['black']['elo']}, "
        f"зевков {stats['black']['blunder']}, ошибок {stats['black']['mistake']}, "
        f"неточностей {stats['black']['inaccuracy']}.\n"
    )

    prompt = (
        "Ты — опытный шахматный тренер-персонаж, который обучает новичка. "
        "Я передаю тебе JSON со всей историей партии и оценками Stockfish. "
        "Изучи партию целиком и напиши ОДНО короткое предложение-комментарий "
        "на русском языке к КАЖДОМУ ходу.\n\n"
        + stats_summary +
        "\nВерни ответ СТРОГО в формате JSON со следующими ключами:\n"
        "- Числовые ключи (0, 1, 2...) — комментарии к ходам.\n"
        "- \"coach_summary\" — 1-2 предложения общего резюме партии на русском "
        "(например: \"Получив тяжёлую позицию, вы упорно боролись в этой партии. "
        "Обращайте внимание на тактику!\").\n"
        "- \"elo_verdict\" — строка вида \"Белые ~1200, Чёрные ~700\".\n\n"
        "Ничего кроме JSON не пиши.\n\n"
        f"```json\n{json.dumps(game_log, ensure_ascii=False)}\n```"
    )

    try:
        response = gemini_client.models.generate_content(
            model='gemini-3.1-flash-lite',
            contents=prompt,
            config={'response_mime_type': 'application/json'},
        )
        text = response.text.strip()
        text = re.sub(r"^```(?:json)?\s*\n?", "", text, flags=re.DOTALL)
        text = re.sub(r"\n?\s*```\s*$", "", text, flags=re.DOTALL)
        text = text.strip()
        parsed = json.loads(text)
        print(f"[INFO] Gemini returned {len(parsed)} keys")
        return parsed
    except Exception as exc:
        raw = ""
        try:
            raw = response.text[:500]
        except Exception:
            raw = "(no text)"
        print(f"[ERROR] Gemini error: {exc}")
        print(f"[ERROR] Gemini raw: {raw}")
        return {}


def ask_gemini_blunder(fen: str, prev_fen: str, move_san: str, refutation_move: str) -> str:
    """Запрашивает короткий комментарий при зевках, передавая ход-опровержение от Stockfish."""
    if gemini_client is None:
        return ""

    prompt = (
        f"Пользователь сделал ход {move_san}. Этот ход является тактической ошибкой (зевком). "
        f"Шахматный движок Stockfish говорит, что лучшим ответом для соперника "
        f"сейчас является ход: {refutation_move}.\n\n"
        "Объясни новичку (рейтинг ~400 Elo) в одно короткое, ёмкое предложение на русском языке, "
        "почему его ход плох, основываясь СТРОГО на этом ответе движка "
        "(например: \"Ты подставил ферзя под удар слона на a8\" или "
        "\"Этот ход зевает ладью\"). Не придумывай другие ходы, пиши строго по делу. "
        "Верни СТРОГО текст комментария."
    )

    try:
        response = gemini_client.models.generate_content(
            model='gemini-3.1-flash-lite',
            contents=prompt,
        )
        return response.text.strip()
    except Exception as exc:
        print(f"[ERROR] Gemini blunder error: {exc}")
        return ""


# ---------------------------------------------------------------------------
# Models
# ---------------------------------------------------------------------------


class PGNRequest(BaseModel):
    pgn: str


class PositionRequest(BaseModel):
    fen: str
    prev_fen: Optional[str] = None
    move_san: str


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
    game_log: list[dict] = []
    board = game.board()
    engine: Optional[chess.engine.SimpleEngine] = None

    try:
        engine = chess.engine.SimpleEngine.popen_uci(STOCKFISH_PATH)
        move_index = 0

        for move in game.mainline_moves():
            side = board.turn
            san = board.san(move)

            # Best move from engine BEFORE making the move
            info_before = engine.analyse(
                board, chess.engine.Limit(time=0.2)
            )
            cp_before = score_to_cp(info_before["score"], side)
            best_pv = info_before.get("pv", [])
            best_move = best_pv[0] if best_pv else None

            material_before_side = get_material_value(board, side)
            total_mat = get_total_material(board)
            stage = detect_stage(move_index, total_mat)
            is_book = move_index < 10 and total_mat >= 70  # rough heuristic

            board.push(move)

            info_after = engine.analyse(
                board, chess.engine.Limit(time=0.2)
            )
            cp_after = score_to_cp(info_after["score"], side)
            material_after_side = get_material_value(board, side)

            cpl = max(0, cp_before - cp_after)
            is_sacrifice = cpl <= 5 and material_after_side < material_before_side
            is_best = (best_move == move) if best_move else False

            cat_key, category, icon = categorize_move(
                cpl,
                is_sacrifice=is_sacrifice,
                is_best_move=is_best,
                is_book=is_book,
                had_advantage_before=(cp_before > 50),
            )

            eval_white = score_to_cp(info_after["score"], chess.WHITE)
            score_display = format_score_display(info_after["score"], chess.WHITE)

            moves_data.append({
                "san": san,
                "color": "white" if side == chess.WHITE else "black",
                "cpl": cpl,
                "eval": eval_white,
                "score_display": score_display,
                "category": category,
                "cat_key": cat_key,
                "icon": icon,
                "comment": "",
                "stage": stage,
            })

            game_log.append({
                "index": move_index,
                "san": san,
                "color": "white" if side == chess.WHITE else "black",
                "score": score_display,
                "cpl": cpl,
                "category": category,
            })

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

    # --- 3. Статистика ---
    stats = compute_stats(moves_data)

    # --- 4. Комментарии Gemini ---
    gemini_result = ask_gemini(game_log, stats)
    elo_verdict = ""
    coach_summary = ""
    for key, value in gemini_result.items():
        sk = str(key)
        if sk == "elo_verdict":
            elo_verdict = str(value)
        elif sk == "coach_summary":
            coach_summary = str(value)
        elif sk.isdigit():
            idx = int(sk)
            if 0 <= idx < len(moves_data):
                moves_data[idx]["comment"] = str(value)

    # --- 5. Ответ ---
    return {
        "moves_data": moves_data,
        "stats": stats,
        "elo_verdict": elo_verdict,
        "coach_summary": coach_summary,
    }


@app.post("/analyze_position")
def analyze_position(request: PositionRequest):
    """Быстрый анализ одиночного хода для песочницы."""
    engine: Optional[chess.engine.SimpleEngine] = None
    try:
        engine = chess.engine.SimpleEngine.popen_uci(STOCKFISH_PATH)
        board = chess.Board(request.fen)
        
        # Сторона, которая только что сделала ход (если сейчас ход черных, значит ходили белые)
        side_moved = not board.turn
        
        info_after = engine.analyse(board, chess.engine.Limit(depth=10))
        cp_after = score_to_cp(info_after["score"], side_moved)
        
        cpl = 0
        category = "Хороший"
        icon = "✅"
        comment = ""
        
        # Если передан предыдущий FEN, считаем CPL
        if request.prev_fen:
            prev_board = chess.Board(request.prev_fen)
            info_before = engine.analyse(prev_board, chess.engine.Limit(depth=10))
            cp_before = score_to_cp(info_before["score"], side_moved)
            
            cpl = max(0, cp_before - cp_after)
            category, icon = categorize_move(cpl)
            
            # Зевок (> 200 сантипешек) — достаём ход-опровержение из PV Stockfish
            if cpl > 200:
                refutation_san = ""
                pv = info_after.get("pv", [])
                if pv:
                    try:
                        refutation_san = board.san(pv[0])
                    except Exception:
                        refutation_san = str(pv[0])
                comment = ask_gemini_blunder(
                    request.fen, request.prev_fen, request.move_san, refutation_san
                )
                
            # Проверка на бриллиант
            material_before = get_material_value(prev_board, side_moved)
            material_after = get_material_value(board, side_moved)
            if cpl <= 15 and material_after < material_before:
                category = "Бриллиантовый"
                icon = "💎"

        eval_white = score_to_cp(info_after["score"], chess.WHITE)
        score_display = format_score_display(info_after["score"], chess.WHITE)
        
        return {
            "san": request.move_san,
            "color": "white" if side_moved == chess.WHITE else "black",
            "cpl": cpl,
            "eval": eval_white,
            "score_display": score_display,
            "category": category,
            "icon": icon,
            "comment": comment
        }
    except FileNotFoundError:
        raise HTTPException(
            status_code=503,
            detail=f"Движок Stockfish не найден по пути: {STOCKFISH_PATH}",
        )
    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail=f"Ошибка при анализе позиции: {exc}",
        )
    finally:
        if engine is not None:
            engine.quit()
