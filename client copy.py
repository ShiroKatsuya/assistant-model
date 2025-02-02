import chess
import chess.svg
import webbrowser
import tempfile
import os
import google.generativeai as genai
import time

genai.configure(api_key="AIzaSyC3mPmd3ps_fGEXMwCjXOUPw7jMpXIeAoE")
model = genai.GenerativeModel('gemini-1.5-flash')

# Create initial HTML file
temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.html')
board = chess.Board()
print(board)


import ollama
model_name = "deepseek-r1:1.5b"

def get_ai_move_aggressive():
    fen = board.fen()
    

    print(fen)

    # print(board.turn)
    
    prompt = f"""You are a merciless chess engine analyzing this position: {fen}
            Prioritize in this order:


            Direct Checkmate
            Find a move that ensures an immediate checkmate on this turn, leaving no chance for the opponent to defend. Ensure the move is not only effective but also accounts for all possible responses from the opponent to secure an airtight victory.

            Moves That Create Multiple Threats
            Identify moves that exert maximum pressure on the opponent by creating multiple threats simultaneously. Choose moves that force your opponent into difficult decisions, increasing the likelihood of a mistake.

            Utilize All Piece Capabilities {fen}
            Carefully analyze the position and utilize all available pieces based on the {fen} position to maximize your winning chances. Consider the synergy between pieces and the optimal positioning for each move to ensure maximum impact.

            Analyze the Best Tactical Solution to Conclude the Game
            Find the most effective tactical solution to finish the game quickly while avoiding traps set by the opponent. Prioritize moves that exploit your opponent's mistakes or weaknesses in their defensive structure.

            Explore All Possible Alternatives to Secure Victory
            Examine all alternative moves and strategic paths, then choose the best approach to guarantee victory. Don't hesitate to consider more complex lines if they provide a more certain path to win.

            Control Critical Files or Ranks
            Focus on dominating files or ranks that play a pivotal role in the game. Use heavy pieces like rooks or the queen to maintain control in these areas, block your opponent’s mobility, and exploit their weaknesses.

            Take Advantage of Double Attacks
            Spot opportunities for double attacks using the queen, knight, or other pieces. These moves can force your opponent to lose important material or weaken their defensive setup.

            Create Direct Checks to Open Opponent’s Position
            Use checks as a tool to force your opponent to move their king or other critical pieces to weaker positions, increasing your chances of winning.

            Break Down the Opponent’s Defensive Structure
            Analyze the placement of your opponent’s defensive pieces and find moves to disrupt or weaken their coordination. If they have a solid fortress, prioritize moves that dismantle it.

            Consolidate Material Advantage
            If you have a material advantage, focus on simplifying the game by exchanging pieces without losing your positional edge. This makes your path to victory more straightforward.

            Ensure Your Own Defense is Secure
            Before launching a major attack, ensure there are no counter-threats from your opponent that could disrupt your plans. Double-check the positioning of your defensive pieces to maintain stability.

            Leverage Passed Pawns
            If you have a passed pawn, push it forward with support from other pieces. The threat of promotion often forces significant concessions or even resignation from your opponent.

            Use Knights for Tactical Strikes
            Knights are often effective in creating unexpected tactical threats. Look for opportunities to execute forks or surprise attacks with your knight.

            Avoid Stalemates to Prevent Draws
            If you have a significant advantage, avoid creating stalemate positions that would result in a draw. Ensure your moves leave the opponent’s king with space to maneuver.

            Utilize Long-Range Pieces
            Deploy queens, rooks, and bishops for long-range attacks. This forces your opponent into difficult defensive positions while minimizing risks to your own position.

            Build Gradual Threats
            Construct your attack step by step by creating layered threats. This method overwhelms your opponent as small threats accumulate into a decisive advantage.

            Block the Opponent’s King Mobility
            Identify the squares available to the opponent’s king and focus on restricting its movement with your pieces. A trapped king makes delivering checkmate significantly easier.

            Employ Strategic Sacrifices
            Consider sacrificing material to gain positional advantages or create a clear path to checkmate. Ensure the sacrifice provides a substantial payoff.

            Avoid Blunders in Critical Moments
            In crucial moments nearing victory, stay vigilant to avoid blunders that could turn the game around. Carefully reassess each move to ensure accuracy.

            Apply Chess Mathematical Combinations
            Identify and execute known tactical patterns, such as double checks, pins, or traps. These combinations often unlock victories in complex positions.
   

            Look for the fastest path to victory - if you see a winning combination, take it!
            Provide ONLY a single move in UCI format (e.g. e2e4, g1f3).
            Valid moves are: {[move.uci() for move in board.legal_moves]}"""


    max_retries = 3
    retry_delay = 10  # seconds
    last_error = None
    print("listboard",board.fen())

    for attempt in range(max_retries):
        try:

            response = ollama.generate(
                model=model_name,
                system=prompt,
                 prompt=board.fen()
                )
            move = response['response'].strip().split()[0]
            try:
                chess_move = chess.Move.from_uci(move)
                if chess_move in board.legal_moves:
                    board.push(chess_move)
                    is_checkmate = board.is_checkmate()
                    board.pop()  
                    
                    if is_checkmate:
                        return move
                    if board.gives_check(chess_move):
                        return move
                    return move
            except ValueError:
                print(f"Invalid move format received: {move}")
            
            legal_moves = list(board.legal_moves)
            if legal_moves:
                for m in legal_moves:
                    board.push(m)
                    is_checkmate = board.is_checkmate()
                    board.pop()
                    if is_checkmate:
                        return m.uci()
                for m in legal_moves:
                    if board.gives_check(m) or board.is_capture(m):
                        return m.uci()
                return legal_moves[0].uci()
            return None
            
        except Exception as e:
            last_error = e
            if "429" in str(e) and attempt < max_retries - 1:
                print(f"Rate limit hit, retrying in {retry_delay} seconds...")
                time.sleep(retry_delay)
                retry_delay *= 2  # Exponential backoff
                continue
            elif attempt < max_retries - 1:
                print(f"Error occurred, retrying... ({str(e)})")
                time.sleep(retry_delay)
                continue
    
    print(f"All retries failed. Last error: {str(last_error)}")
    # Fall back to a legal move if available
    legal_moves = list(board.legal_moves)
    return legal_moves[0].uci() if legal_moves else None

def get_ai_move_aggressive_2():
    fen = board.fen()
    print(fen)
    
    prompt = f"""You are a bloodthirsty chess engine analyzing this position: {fen}

Prioritize in this order:
1. Immediate checkmate
2. Moves that attack the enemy king
3. Captures that weaken king protection
4. Aggressive piece deployment targeting the king
5. Pawn breaks that open lines to the king

Look for the fastest path to victory - if you see a winning combination, take it!
Provide ONLY a single move in UCI format (e.g. e2e4, g1f3).
Valid moves are: {[move.uci() for move in board.legal_moves]}"""

    max_retries = 3
    retry_delay = 10  # seconds
    last_error = None

    for attempt in range(max_retries):
        try:
            chat = model.start_chat(history=[])
            response = chat.send_message(prompt)
            move = response.text.strip().split()[0]
            
            try:
                chess_move = chess.Move.from_uci(move)
                if chess_move in board.legal_moves:
                    # Make the move temporarily to check if it gives checkmate
                    board.push(chess_move)
                    is_checkmate = board.is_checkmate()
                    board.pop()  # Undo the move
                    
                    if is_checkmate:
                        return move
                    # Then prioritize moves that give check
                    if board.gives_check(chess_move):
                        return move
                    return move
            except ValueError:
                print(f"Invalid move format received: {move}")
            
            legal_moves = list(board.legal_moves)
            if legal_moves:
                # Look for immediate winning moves first
                for m in legal_moves:
                    board.push(m)
                    is_checkmate = board.is_checkmate()
                    board.pop()
                    if is_checkmate:
                        return m.uci()
                # Then look for checks and captures
                for m in legal_moves:
                    if board.gives_check(m) or board.is_capture(m):
                        return m.uci()
                return legal_moves[0].uci()
            return None
            
        except Exception as e:
            last_error = e
            if "429" in str(e) and attempt < max_retries - 1:
                print(f"Rate limit hit, retrying in {retry_delay} seconds...")
                time.sleep(retry_delay)
                retry_delay *= 2
                continue
            elif attempt < max_retries - 1:
                print(f"Error occurred, retrying... ({str(e)})")
                time.sleep(retry_delay)
                continue
    
    print(f"All retries failed. Last error: {str(last_error)}")
    legal_moves = list(board.legal_moves)
    return legal_moves[0].uci() if legal_moves else None

def update_display():
    # Generate SVG of current board state
    svg_content = chess.svg.board(
        board,
        size=350,
    )
    
    move_history = []
    for move in board.move_stack:
        print(move)
        move_history.append(move.uci())
    
    with open(temp_file.name, 'w') as f:
        f.write(f'''
        <html>
        <head>
            <meta http-equiv="refresh" content="2">
            <style>
                body {{ font-family: Arial, sans-serif; }}
                .status {{ margin: 10px 0; }}
            </style>
        </head>
        <body>
            {svg_content}
            <div class="status">
                <p>Current turn: {'White' if board.turn else 'Black'}</p>
                <p>Game status: {'Checkmate!' if board.is_checkmate() else 'Check!' if board.is_check() else 'Ongoing'}</p>
                <p>Move history: {' '.join(move_history)}</p>
                <p>Number of moves: {len(move_history)}</p>
            </div>
        </body>
        </html>
        ''')

# Open browser once at start
webbrowser.open('file://' + os.path.realpath(temp_file.name))
update_display()

# Game loop
while not board.is_game_over():
    try:
        current_player = 'White' if board.turn else 'Black'
        print(f"\n{current_player} is thinking...")
        
        start_time = time.time()
        # Both players play aggressively with different strategies
        move = get_ai_move_aggressive() if board.turn else get_ai_move_aggressive_2()
        elapsed_time = time.time() - start_time
        
        if move and board.is_legal(chess.Move.from_uci(move)):
            print(f"{current_player} plays: {move} (took {elapsed_time:.1f}s)")
            board.push(chess.Move.from_uci(move))
            update_display()
            # Variable delay based on move time
            delay = max(1, 3 - elapsed_time)
            time.sleep(delay)
        else:
            if board.is_game_over():
                break
            print("Invalid move received, retrying...")
            continue
            
    except Exception as e:
        print(f"Error occurred: {str(e)}")
        continue

print("Game Over!")
if board.is_checkmate():
    winner = "Black" if board.turn else "White"
    print(f"Checkmate! {winner} wins!")
elif board.is_stalemate():
    print("Stalemate! It's a draw!")
elif board.is_insufficient_material():
    print("Draw - Insufficient material!")