import math
import time
from pydobot import Dobot
import serial

# Mocking Dobot commands
class MockDobot:
    def move_to(self, x, y, z, r):
        print(f"Moving to ({x}, {y}, {z}, {r})")

    def suck(self, enable):
        print("Suction " + ("enabled" if enable else "disabled"))

    def close(self):
        print("Closing connection.")

# Use the mock instead of the actual Dobot
device = MockDobot()

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

# Function to read sensor input from Arduino
def read_sensor_values():
    try:
        # Replace 'COM4' with the port your Arduino is connected to
        with serial.Serial('COM4', 9600, timeout=1) as ser:
            ser.write(b'R')  # Send a signal to request data
            line = ser.readline().decode('utf-8').strip()
            sensor_values = [int(value) for value in line.split(',')]
            if len(sensor_values) != 9:
                raise ValueError("Invalid sensor data length.")
            return sensor_values
    except Exception as e:
        print(f"Error reading sensor values: {e}")
        return [0] * 9  # Default to no input if an error occurs

# Main game loop
def play_game():
    global sensor_values, last_board, player_turn
    while True:
        sensor_values = read_sensor_values()  # Get input from Arduino
        update_virtual_map(sensor_values, last_board, player_turn)
        bot_move = find_best_move(sensor_values, last_board, player_turn)

        # Find the first unused cube
        cube_idx = next((i for i, used in enumerate(cube_used) if not used), -1)
        if cube_idx == -1:
            print("No cubes available to play.")
            break

        # Execute Dobot movement
        pick_and_place(cube_idx, bot_move)
        cube_used[cube_idx] = True  # Mark cube as used

        print(f"Bot played at position: {bot_move}")
        last_board[bot_move] = 2  # Update the board with bot's move

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
