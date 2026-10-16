import math
import tkinter as tk
from tkinter import messagebox
from pydobot import Dobot
import time

# Dobot initialization
port = "COM3"  # Update this with your Dobot's port
device = Dobot(port)

# Preset coordinates for cubes and board positions
cube_coordinates = [
    (200, 0, -50),  # Cube 1
    (200, 50, -50),  # Cube 2
    (200, 100, -50),  # Cube 3
    (200, 150, -50)  # Cube 4
]

board_coordinates = [
    (100, -100, 0), (100, 0, 0), (100, 100, 0),  # Row 1
    (150, -100, 0), (150, 0, 0), (150, 100, 0),  # Row 2
    (200, -100, 0), (200, 0, 0), (200, 100, 0)   # Row 3
]

cube_used = [False] * 4  # Track used cubes

# Preset safe coordinate
safe_coordinate = (150, 150, 50)  # Adjust these values based on your setup

# Function to pick and place a cube
def pick_and_place(cube_idx, position_idx):
    if cube_idx < 0 or cube_idx >= len(cube_coordinates):
        print("Invalid cube index.")
        return

    if position_idx < 0 or position_idx >= len(board_coordinates):
        print("Invalid position index.")
        return

    # Pick cube
    cube_x, cube_y, cube_z = cube_coordinates[cube_idx]
    device.move_to(cube_x, cube_y, cube_z, 0)  # Move to cube position
    device.suck(True)  # Turn on suction
    time.sleep(1)
    device.move_to(cube_x, cube_y, cube_z + 50, 0)  # Lift cube

    # Move to safe coordinate
    safe_x, safe_y, safe_z = safe_coordinate
    device.move_to(safe_x, safe_y, safe_z, 0)

    # Place cube
    pos_x, pos_y, pos_z = board_coordinates[position_idx]
    device.move_to(pos_x, pos_y, pos_z + 50, 0)  # Move above target position
    device.move_to(pos_x, pos_y, pos_z, 0)  # Place cube
    device.suck(False)  # Turn off suction
    time.sleep(1)
    device.move_to(pos_x, pos_y, pos_z + 50, 0)  # Lift after placing

    # Return to safe coordinate
    device.move_to(safe_x, safe_y, safe_z, 0)

# Tic Tac Toe functions
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

# GUI Implementation
def play_game():
    global sensor_values, last_board, player_turn

    def update_and_replay():
        try:
            sensor_input = entry.get().split(",")
            updated_sensors = [int(value) for value in sensor_input]
            if len(updated_sensors) != 9:
                raise ValueError
            global sensor_values
            sensor_values = updated_sensors
            update_board_visualization(sensor_values, last_board)
            bot_move = find_best_move(sensor_values, last_board, player_turn)

            # Find the first unused cube
            cube_idx = next((i for i, used in enumerate(cube_used) if not used), -1)
            if cube_idx == -1:
                messagebox.showerror("Error", "No cubes available to play.")
                return

            # Execute Dobot movement
            pick_and_place(cube_idx, bot_move)
            cube_used[cube_idx] = True  # Mark cube as used

            messagebox.showinfo("Bot Move", f"Bot played at position: {bot_move}")
            last_board[bot_move] = 2  # Update the board with bot's move
            update_board_visualization(sensor_values, last_board)
        except ValueError:
            messagebox.showerror("Input Error", "Please enter a valid sensor list with 9 values (0 or 1) separated by commas.")

    def update_board_visualization(sensor_values, board):
        for i in range(9):
            row, col = divmod(i, 3)  # Convert 1D index to 2D row and column
            if board[i] == 1:
                buttons[row][col]["text"] = "X"
            elif board[i] == 2:
                buttons[row][col]["text"] = "O"
            else:
                buttons[row][col]["text"] = ""

    root = tk.Tk()
    root.title("Tic Tac Toe Bot")

    tk.Label(root, text="Enter sensor values (comma-separated):").pack(pady=10)

    entry = tk.Entry(root, width=30)
    entry.pack(pady=5)
    entry.insert(0, "0,0,0,0,0,0,0,0,0")

    tk.Button(root, text="Find Bot Move", command=update_and_replay).pack(pady=10)

    board_frame = tk.Frame(root)
    board_frame.pack(pady=10)

    buttons = []
    for row in range(3):
        button_row = []
        for col in range(3):
            btn = tk.Button(board_frame, text="", width=5, height=2, font=("Arial", 24))
            btn.grid(row=row, column=col, padx=5, pady=5)
            button_row.append(btn)
        buttons.append(button_row)

    root.mainloop()

# Example Usage
sensor_values = [0, 0, 0, 0, 0, 0, 0, 0, 0]
last_board = [0, 0, 0, 0, 0, 0, 0, 0, 0]
player_turn = True  # True for Player's turn, False for Bot's turn
play_game()

# Close the Dobot connection when done
def close_connection():
    device.close()
    print("Dobot connection closed.")

import atexit
atexit.register(close_connection)
