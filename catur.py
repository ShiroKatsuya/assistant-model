import chess
import chess.svg
import webbrowser
import tempfile
import os
import time
from google import genai
from google.genai.types import GenerateContentConfig

class ChessGame:
    def __init__(self, api_key):
        self.client = genai.Client(api_key=api_key)
        self.model_id = "gemini-2.0-flash-exp"
        self.board = chess.Board()
        self.temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.html')
        
        # Konfigurasi untuk model Gemini
        self.gemini_config = GenerateContentConfig(
            temperature=0.2,
            top_p=0.95,
            top_k=20,
            candidate_count=1,
            max_output_tokens=10,
            stop_sequences=["STOP!"],
        )
    
    def get_ai_move(self):
        try:
            fen = self.board.fen()
            legal_moves = [str(m) for m in self.board.legal_moves]
            
            if not legal_moves:
                return None
                
            prompt = f"""Given this chess position in FEN notation: {fen}
Suggest an aggressive attacking move for {'White' if self.board.turn else 'Black'}.
Prioritize:
1. Capturing opponent's pieces
2. Checking the opponent's king
3. Threatening key pieces
4. Controlling the center aggressively
You must return ONLY the move in UCI format (e.g., e2e4, b1c3).
Legal moves: {legal_moves}"""
            
            response = self.client.models.generate_content(
                model=self.model_id,
                config=self.gemini_config, 
                contents=[prompt]
            )
            
            move = response.text.strip().lower()
            move = ''.join(c for c in move if c.isalnum())
            
            if move in legal_moves:
                return move
            
            print(f"AI suggested invalid move: {move}")
            return None
            
        except Exception as e:
            print(f"Error in get_ai_move: {str(e)}")
            return None
    
    def update_display(self):
        try:
            svg_content = chess.svg.board(self.board, size=400)
            with open(self.temp_file.name, 'w', encoding='utf-8') as f:
                f.write(f'''
                <!DOCTYPE html>
                <html>
                <head>
                    <meta charset="utf-8">
                    <meta http-equiv="refresh" content="2">
                    <style>
                        body {{ 
                            font-family: Arial, sans-serif;
                            display: flex;
                            flex-direction: column;
                            align-items: center;
                            background-color: #f0f0f0;
                        }}
                        .status {{
                            margin: 20px;
                            padding: 10px;
                            border-radius: 5px;
                            background-color: white;
                            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
                        }}
                    </style>
                </head>
                <body>
                    {svg_content}
                    <div class="status">
                        <div>Giliran: {'Putih' if self.board.turn else 'Hitam'}</div>
                        <div>Status: {'Skakmat!' if self.board.is_checkmate() else 'Skak!' if self.board.is_check() else 'Sedang Berlangsung'}</div>
                    </div>
                </body>
                </html>
                ''')
        except Exception as e:
            print(f"Error in update_display: {str(e)}")
    
    def play_game(self):
        # Buka browser di awal permainan
        webbrowser.open('file://' + os.path.realpath(self.temp_file.name))
        self.update_display()
        
        max_retries = 3
        while not self.board.is_game_over():
            try:
                print(f"AI sedang berpikir...")
                
                # Implementasi sistem retry
                for _ in range(max_retries):
                    move = self.get_ai_move()
                    if move:
                        print(f"AI memainkan: {move}")
                        self.board.push_uci(move)
                        self.update_display()
                        time.sleep(1)
                        break
                else:
                    print(f"Gagal mendapatkan langkah valid setelah {max_retries} percobaan")
                    break
                    
            except Exception as e:
                print(f"Error dalam play_game: {str(e)}")
                continue
        
        # Tampilkan hasil akhir
        self.show_game_result()
        
    def show_game_result(self):
        print("\nPermainan Selesai!")
        if self.board.is_checkmate():
            print("Skakmat!")
            winner = "Hitam" if self.board.turn else "Putih"
            print(f"Pemenang: {winner}")
        elif self.board.is_stalemate():
            print("Remis - Pat!")
        elif self.board.is_insufficient_material():
            print("Remis - Material Tidak Cukup!")
        elif self.board.is_fifty_moves():
            print("Remis - Aturan 50 Langkah!")
        elif self.board.is_repetition():
            print("Remis - Pengulangan Posisi!")
        
    def cleanup(self):
        try:
            os.unlink(self.temp_file.name)
        except Exception as e:
            print(f"Error saat membersihkan file temporary: {str(e)}")

# Penggunaan
if __name__ == "__main__":
    API_KEY = "AIzaSyBovFnjwweKGUnaaihbLi3aacQfK3DZgBk"  # Ganti dengan API key Anda
    game = ChessGame(API_KEY)
    try:
        game.play_game()
    finally:
        game.cleanup()