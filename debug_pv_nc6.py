import os
from main import get_material_value
import chess
import chess.engine

STOCKFISH_PATH = os.path.join(os.path.dirname(__file__), "stockfish", "stockfish.exe")
engine = chess.engine.SimpleEngine.popen_uci(STOCKFISH_PATH)

board = chess.Board("rnbqkbnr/pppp1ppp/8/4p3/4P3/5N2/PPPP1PPP/RNBQKB1R b KQkq - 1 2")
move = chess.Move.from_uci("b8c6")
side = chess.BLACK

info = engine.analyse(board, chess.engine.Limit(depth=10))
board.push(move)
info_after = engine.analyse(board, chess.engine.Limit(depth=10))

pv = info_after.get("pv", [])
print("PV:", pv)
adv_before = get_material_value(board, side) - get_material_value(board, not side)

for p in pv:
    board.push(p)
adv_after_pv = get_material_value(board, side) - get_material_value(board, not side)

print("adv_before:", adv_before)
print("adv_after_full_pv:", adv_after_pv)

engine.quit()
