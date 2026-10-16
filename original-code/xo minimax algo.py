import math

def is_winner(board, player):
    """Check if a player has won."""
    win_positions = [
        [0, 1, 2], [3, 4, 5], [6, 7, 8],  # Rows
        [0, 3, 6], [1, 4, 7], [2, 5, 8],  # Columns
        [0, 4, 8], [2, 4, 6]             # Diagonals
    ]
    for pos in win_positions:
        if all(board[i] == player for i in pos):
            return True
    return False

def is_draw(board):
    """Check if the game is a draw."""
    return all(cell != 0 for cell in board) and not is_winner(board, 1) and not is_winner(board, 2)

def minimax(board, depth, is_maximizing):
    """Minimax algorithm to find the optimal move."""
    if is_winner(board, 2):  # Bot wins
        return 10 - depth
    if is_winner(board, 1):  # Player wins
        return depth - 10
    if is_draw(board):
        return 0

    if is_maximizing:
        best_score = -math.inf
        for i in range(9):
            if board[i] == 0:  # Check if the cell is empty
                board[i] = 2  # Bot plays
                score = minimax(board, depth + 1, False)
                board[i] = 0  # Undo move
                best_score = max(best_score, score)
        return best_score
    else:
        best_score = math.inf
        for i in range(9):
            if board[i] == 0:  # Check if the cell is empty
                board[i] = 1  # Player plays
                score = minimax(board, depth + 1, True)
                board[i] = 0  # Undo move
                best_score = min(best_score, score)
        return best_score

def update_virtual_map(sensor_values, last_board, player_turn):
    """Update the virtual map based on sensor changes."""
    for i in range(9):
        if sensor_values[i] == 1 and last_board[i] == 0:
            last_board[i] = 1 if player_turn else 2
    return last_board

def find_best_move(sensor_values, last_board, player_turn):
    """Find the best move for the bot based on updated sensor values."""
    board = update_virtual_map(sensor_values, last_board, player_turn)
    best_score = -math.inf
    best_move = -1
    for i in range(9):
        if board[i] == 0:  # Check if the cell is empty
            board[i] = 2  # Bot plays
            score = minimax(board, 0, False)
            board[i] = 0  # Undo move
            if score > best_score:
                best_score = score
                best_move = i
    return best_move

# Example Usage
# Sensor Values: 0: Empty, 1: Block placed (X or O, determined by turn)
# Initial board: 0: Empty, 1: Player's move, 2: Bot's move
sensor_values = [0, 0, 0, 0, 0, 0, 0, 0, 0]
last_board = [0, 0, 0, 0, 0, 0, 0, 0, 0]
player_turn = True  # True for Player's turn, False for Bot's turn

# Update the board and find the bot's move
bot_move = find_best_move(sensor_values, last_board, player_turn)
print(f"Bot should play at position: {bot_move}")
