import chess

board = chess.Board()

chess.Move.from_uci("a8a1") in board.legal_moves

print(board)