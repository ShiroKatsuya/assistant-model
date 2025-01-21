from flask import Flask, request, Response
import chess
import chess.svg
from flask_cors import CORS
import json
import queue
import threading

app = Flask(__name__)
CORS(app)

# Global board state
board = chess.Board()
# Queue for updates
updates = queue.Queue()

@app.route('/', methods=['GET', 'POST'])
def display_board():
    svg_content = chess.svg.board(board, size=350)
    html_content = f'''
    <!DOCTYPE html>
    <html>
    <head>
        <style>
            body {{ 
                display: flex;
                flex-direction: column;
                align-items: center;
                font-family: Arial, sans-serif;
            }}
            .status {{
                margin: 20px;
                font-size: 18px;
            }}
        </style>
        <script>
            const evtSource = new EventSource('/stream');
            evtSource.onmessage = function(event) {{
                if (event.data === 'update') {{
                    window.location.reload();
                }}
            }};
        </script>
    </head>
    <body>
        {svg_content}
        <div class="status">
            <p>Current turn: {'White' if board.turn else 'Black'}</p>
            <p>Game status: {'Checkmate!' if board.is_checkmate() else 'Check!' if board.is_check() else 'Ongoing'}</p>
        </div>
    </body>
    </html>
    '''
    return html_content

@app.route('/stream')
def stream():
    def event_stream():
        while True:
            message = updates.get()  # This blocks until an item is available
            yield f"data: {message}\n\n"
    
    return Response(event_stream(), mimetype="text/event-stream")

@app.route('/make_move/<move>', methods=['POST'])
def make_move(move):
    try:
        board.push_san(move)
        updates.put('update')  # Signal that an update is available
        return json.dumps({'status': 'success'})
    except ValueError:
        return json.dumps({'status': 'error', 'message': 'Invalid move'})

@app.route('/game_state', methods=['POST'])
def game_state():
    updates.put('update')  # Signal that an update is available
    return json.dumps({
        'is_game_over': board.is_game_over(),
        'is_checkmate': board.is_checkmate(),
        'is_stalemate': board.is_stalemate(),
        'is_insufficient_material': board.is_insufficient_material(),
        'turn': 'white' if board.turn else 'black'
    })

if __name__ == '__main__':
    print("Starting server on http://localhost:5000")
    app.run(port=5000, debug=False, threaded=True)