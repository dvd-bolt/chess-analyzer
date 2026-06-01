from main import check_is_sacrifice, get_material_value
import chess

board = chess.Board("r2qkbnr/ppp2ppp/2np4/4p3/2B1P1b1/2N2N1P/PPPP1PP1/R1BQK2R b KQkq - 0 5")
move = chess.Move.from_uci("g4f3")
# Wait, h3 is white's move.
board_before = chess.Board("r2qkbnr/ppp2ppp/2np4/4p3/2B1P1b1/2N2N2/PPPP1PPP/R1BQK2R w KQkq - 2 5")
board_after = chess.Board("r2qkbnr/ppp2ppp/2np4/4p3/2B1P1b1/2N2N1P/PPPP1PP1/R1BQK2R b KQkq - 0 5")
move = chess.Move.from_uci("h2h3")
pv0 = chess.Move.from_uci("g4f3")
side = chess.WHITE

print("Adv before:", get_material_value(board_before, side) - get_material_value(board_before, not side))
board_after.push(pv0)
print("Adv after pv0:", get_material_value(board_after, side) - get_material_value(board_after, not side))
board_after.pop()

print("Is sac?", check_is_sacrifice(board_before, board_after, move, pv0, side))
