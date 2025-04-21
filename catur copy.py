import chess
import chess.svg
import webbrowser
import tempfile
import os
from google import genai
import time

client = genai.Client(api_key="AIzaSyBovFnjwweKGUnaaihbLi3aacQfK3DZgBk")
model_id = "gemini-2.0-flash-exp"

# Create initial HTML file
temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.html')
board = chess.Board()

def get_ai_move():
    try:
        fen = board.fen()
        # Modifikasi prompt untuk mendorong langkah yang lebih agresif
        prompt = f"""Given this chess position in FEN notation: {fen}
Suggest an aggressive attacking move for {'White' if board.turn else 'Black'}.
Prioritize:
1. Capturing opponent's pieces
2. Checking the opponent's king
3. Threatening key pieces
4. Controlling the center aggressively
You must return ONLY the move in UCI format (e.g., e2e4, b1c3).
Do not include any other text or explanation.
The move must be a legal move from the current position.
Only suggest moves from the list of legal moves: {[str(m) for m in board.legal_moves]}"""
        
        response = client.models.generate_content(model=model_id, contents=[prompt])
        move = response.text.strip().lower()
        move = ''.join(c for c in move if c.isalnum())
        
        if len(move) not in [4, 5]:
            print(f"Invalid move format: {move}")
            return None
            
        legal_moves = [str(m) for m in board.legal_moves]
        if move in legal_moves:
            return move
        print(f"Invalid move suggested: {move}")
        return None
            
    except Exception as e:
        print(f"Error occurred: {str(e)}")
        return None

def update_display():
    svg_content = chess.svg.board(board, size=350)
    with open(temp_file.name, 'w') as f:
        f.write(f'''
        <html>
        <head>
            <meta http-equiv="refresh" content="1"> <!-- Dipercepat refresh rate -->
        </head>
        <body>
            {svg_content}
            <br>
            <div>Current turn: {'White' if board.turn else 'Black'}</div>
            <div>Game status: {'Checkmate!' if board.is_checkmate() else 'Check!' if board.is_check() else 'Ongoing'}</div>
        </body>
        </html>
        ''')

# Open browser once at start
webbrowser.open('file://' + os.path.realpath(temp_file.name))
update_display()

while not board.is_game_over():
    try:
        print(f"AI is thinking...")
        move = get_ai_move()
        if move:
            print(f"AI plays: {move}")
            board.push_uci(move)
            update_display()
            time.sleep(0.5)  # Waktu tunggu dipercepat
        else:
            print("No valid move found, retrying...")
            continue
    except Exception as e:
        print(f"Error occurred: {str(e)}")
        continue

print("Game Over!")
if board.is_checkmate():
    print("Checkmate!")
elif board.is_stalemate():
    print("Stalemate!")
elif board.is_insufficient_material():
    print("Draw - Insufficient material!")