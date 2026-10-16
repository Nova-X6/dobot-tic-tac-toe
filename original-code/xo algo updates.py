import time
from pydobot import Dobot

# Initialize Dobot Connection
try:
    port = "COM7"  # Replace with the appropriate port for the Dobot
    device = Dobot(port=port, verbose=True)
except Exception as e:
    print(f"Error connecting to Dobot: {e}")
    device = None

# Board State
board = {1: ' ', 2: ' ', 3: ' ',
         4: ' ', 5: ' ', 6: ' ',
         7: ' ', 8: ' ', 9: ' '}
player = 'O'
computer = 'X'

# Predefined Coordinates for Robot Movement
robot_coordinates = {
    1: (200, 200, -50, 0),  # Top-left
    2: (250, 200, -50, 0),  # Top-center
    3: (300, 200, -50, 0),  # Top-right
    4: (200, 250, -50, 0),  # Middle-left
    5: (250, 250, -50, 0),  # Middle-center
    6: (300, 250, -50, 0),  # Middle-right
    7: (200, 300, -50, 0),  # Bottom-left
    8: (250, 300, -50, 0),  # Bottom-center
    9: (300, 300, -50, 0)   # Bottom-right
}

# Predefined Locations for Player 'O' Cubes
player_cubes = {
    1: (100, 100, -50, 0),
    2: (120, 100, -50, 0),
    3: (140, 100, -50, 0),
    4: (160, 100, -50, 0),
    5: (180, 100, -50, 0),
    6: (200, 100, -50, 0),
    7: (220, 100, -50, 0),
    8: (240, 100, -50, 0),
    9: (260, 100, -50, 0)
}

# Predefined Locations for Computer 'X' Cubes
computer_cubes = {
    1: (300, 100, -50, 0),
    2: (320, 100, -50, 0),
    3: (340, 100, -50, 0),
    4: (360, 100, -50, 0),
    5: (380, 100, -50, 0),
    6: (400, 100, -50, 0),
    7: (420, 100, -50, 0),
    8: (440, 100, -50, 0),
    9: (460, 100, -50, 0)
}

# Functions for Algorithm
def printBoard(board):
    print(board[1] + "|" + board[2] + "|" + board[3])
    print("-+-+-")
    print(board[4] + "|" + board[5] + "|" + board[6])
    print("-+-+-")
    print(board[7] + "|" + board[8] + "|" + board[9])
    print("\n")

def spaceIsFree(position):
    return board[position] == ' '

def insertLetter(letter, position):
    if spaceIsFree(position):
        board[position] = letter
        printBoard(board)
        if checkWin():
            if letter == computer:
                print("Bot wins!")
                exit()
            else:
                print("Player wins!")
                exit()
        if checkDraw():
            print("Draw!")
            exit()
    else:
        print(f"Position {position} is already occupied.")

def checkWin():
    # Check rows, columns, diagonals
    return (
        (board[1] == board[2] == board[3] != ' ') or
        (board[4] == board[5] == board[6] != ' ') or
        (board[7] == board[8] == board[9] != ' ') or
        (board[1] == board[4] == board[7] != ' ') or
        (board[2] == board[5] == board[8] != ' ') or
        (board[3] == board[6] == board[9] != ' ') or
        (board[1] == board[5] == board[9] != ' ') or
        (board[3] == board[5] == board[7] != ' ')
    )

def checkDraw():
    return all(board[key] != ' ' for key in board.keys())

def compMove():
    bestScore = -800
    bestMove = 0
    for key in board.keys():
        if board[key] == ' ':
            board[key] = computer
            score = minimax(board, False)
            board[key] = ' '
            if score > bestScore:
                bestScore = score
                bestMove = key
    insertLetter(computer, bestMove)
    executeRobotMove(bestMove, computer)

def minimax(board, isMaximizing):
    if checkWin():
        if isMaximizing:
            return -1
        else:
            return 1
    elif checkDraw():
        return 0

    if isMaximizing:
        bestScore = -800
        for key in board.keys():
            if board[key] == ' ':
                board[key] = computer
                score = minimax(board, False)
                board[key] = ' '
                bestScore = max(score, bestScore)
        return bestScore
    else:
        bestScore = 800
        for key in board.keys():
            if board[key] == ' ':
                board[key] = player
                score = minimax(board, True)
                board[key] = ' '
                bestScore = min(score, bestScore)
        return bestScore

def executeRobotMove(position, letter):
    """Move the Dobot Magician to the specified position."""
    if letter == computer:
        start_coords = computer_cubes[position]
        end_coords = robot_coordinates[position]
        print(f"Robot moving 'X' from {start_coords} to {end_coords}")
        if device:
            sx, sy, sz, sr = start_coords
            ex, ey, ez, er = end_coords
            device.move_to(sx, sy, sz + 50, sr, wait=True)  # Move above the cube
            device.move_to(sx, sy, sz, sr, wait=True)       # Pick up cube
            device.move_to(sx, sy, sz + 50, sr, wait=True)  # Move back up
            device.move_to(ex, ey, ez + 50, er, wait=True)  # Move above target
            device.move_to(ex, ey, ez, er, wait=True)       # Place cube
            device.move_to(ex, ey, ez + 50, er, wait=True)  # Move back up
    elif letter == player:
        start_coords = player_cubes[position]
        end_coords = robot_coordinates[position]
        print(f"Robot moving 'O' from {start_coords} to {end_coords}")
        if device:
            sx, sy, sz, sr = start_coords
            ex, ey, ez, er = end_coords
            device.move_to(sx, sy, sz + 50, sr, wait=True)  # Move above the cube
            device.move_to(sx, sy, sz, sr, wait=True)       # Pick up cube
            device.move_to(sx, sy, sz + 50, sr, wait=True)  # Move back up
            device.move_to(ex, ey, ez + 50, er, wait=True)  # Move above target
            device.move_to(ex, ey, ez, er, wait=True)       # Place cube
            device.move_to(ex, ey, ez + 50, er, wait=True)  # Move back up

def readIRSensorData():
    """Simulate reading IR sensor data to determine the player's move."""
    print("Reading IR sensor data...")
    # Simulate sensor data for demonstration purposes
    sensor_data = [0] * 9  # Replace with actual sensor reading logic

    if device:
        # Read sensor data (dummy example, replace with actual implementation)
        # Assume sensor_data[i] == 1 indicates an input at position i + 1
        for i in range(9):
            if sensor_data[i] == 1 and spaceIsFree(i + 1):
                insertLetter(player, i + 1)
                executeRobotMove(i + 1, player)
                break

# Game Loop
try:
    while not checkWin():
        compMove()  # Robot plays first
        readIRSensorData()  # Wait for user's move
except KeyboardInterrupt:
    print("Game interrupted.")
finally:
    if device:
        device.close()
