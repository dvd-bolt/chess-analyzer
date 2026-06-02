from main import STOCKFISH_PATH, get_material_value
import chess
import chess.engine

engine = chess.engine.SimpleEngine.popen_uci(STOCKFISH_PATH)

# Before Nxe5
board = chess.Board("r2qkbnr/ppp2ppp/2np4/4p3/2B1P1b1/2N2N1P/PPPP1PP1/R1BQK2R w KQkq - 0 6")
move = chess.Move.from_uci("f3e5")
side = chess.WHITE

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
