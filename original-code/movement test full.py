import tkinter as tk
from tkinter import messagebox, simpledialog
import heapq
import json
import os

# Define grid size and initialize
grid_size = 20
grid = [[0 for _ in range(grid_size)] for _ in range(grid_size)]

# Global variables
waypoints = {}
robot_arrow = None
current_position = None
start_position = None
orientation = "Up"
obstacles = set()
waypoints_file = "waypoints.json"
set_obstacle_mode = False

# Load saved waypoints if they exist
if os.path.exists(waypoints_file):
    with open(waypoints_file, "r") as file:
        waypoints = json.load(file)

# A* algorithm
def a_star(grid, start, target):
    rows, cols = len(grid), len(grid[0])
    open_set = []
    heapq.heappush(open_set, (0, start))
    came_from = {}
    g_score = {start: 0}
    f_score = {start: heuristic(start, target)}

    while open_set:
        _, current = heapq.heappop(open_set)
        if current == target:
            return reconstruct_path(came_from, current)

        x, y = current
        for dx, dy in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
            neighbor = (x + dx, y + dy)
            if 0 <= neighbor[0] < rows and 0 <= neighbor[1] < cols:
                if grid[neighbor[0]][neighbor[1]] == 1:  # Obstacle
                    continue

                tentative_g_score = g_score[current] + 1
                if neighbor not in g_score or tentative_g_score < g_score[neighbor]:
                    came_from[neighbor] = current
                    g_score[neighbor] = tentative_g_score
                    f_score[neighbor] = tentative_g_score + heuristic(neighbor, target)
                    if neighbor not in [n[1] for n in open_set]:
                        heapq.heappush(open_set, (f_score[neighbor], neighbor))

    return None

def heuristic(a, b):
    return abs(a[0] - b[0]) + abs(a[1] - b[1])

def reconstruct_path(came_from, current):
    path = [current]
    while current in came_from:
        current = came_from[current]
        path.append(current)
    return path[::-1]

# GUI Functions
def on_cell_click(event):
    global current_position, start_position, set_obstacle_mode

    col = event.x // cell_size
    row = event.y // cell_size

    if set_obstacle_mode:
        # Set an obstacle
        obstacles.add((row, col))
        grid[row][col] = 1
        draw_grid()
    else:
        # Set the robot's start position or a waypoint
        if current_position is None:
            current_position = (row, col)
            start_position = current_position
            grid[row][col] = 2
            draw_grid()
            messagebox.showinfo("Robot Start", f"Robot starting position set at {current_position}")
        else:
            name = simpledialog.askstring("Waypoint Name", "Enter a name for this waypoint:")
            if name:
                waypoints[name] = (row, col)
                grid[row][col] = 3
                draw_grid()
                save_waypoints()
                messagebox.showinfo("Waypoint Saved", f"Waypoint '{name}' saved at {row, col}")

def toggle_obstacle_mode():
    global set_obstacle_mode
    set_obstacle_mode = not set_obstacle_mode
    mode_label.config(text="Mode: Obstacle" if set_obstacle_mode else "Mode: Waypoint")

def draw_grid():
    canvas.delete("all")
    for row in range(grid_size):
        for col in range(grid_size):
            x1 = col * cell_size
            y1 = row * cell_size
            x2 = x1 + cell_size
            y2 = y1 + cell_size

            if grid[row][col] == 1:  # Obstacle
                canvas.create_rectangle(x1, y1, x2, y2, fill="black")
            elif grid[row][col] == 2:  # Start
                canvas.create_rectangle(x1, y1, x2, y2, fill="green")
            elif grid[row][col] == 3:  # Waypoint
                canvas.create_rectangle(x1, y1, x2, y2, fill="blue")
            else:  # Empty cell
                canvas.create_rectangle(x1, y1, x2, y2, fill="white", outline="gray")

def execute_path():
    global current_position
    if current_position is None:
        messagebox.showerror("Error", "Set the robot's starting position first!")
        return

    target_name = simpledialog.askstring("Select Waypoint", f"Available waypoints: {', '.join(waypoints.keys())}\nEnter waypoint name:")
    if target_name not in waypoints:
        messagebox.showerror("Error", "Invalid waypoint name!")
        return

    target_position = waypoints[target_name]
    path = a_star(grid, current_position, target_position)

    if path:
        animate_robot(path)
        current_position = target_position
        messagebox.showinfo("Path Found", f"Path to '{target_name}' completed!")
    else:
        messagebox.showerror("Error", "No path found to the selected waypoint!")

def move_forward(current_pos, orientation):
    row, col = current_pos
    if orientation == "Up":
        return (row - 1, col)
    elif orientation == "Down":
        return (row + 1, col)
    elif orientation == "Left":
        return (row, col - 1)
    elif orientation == "Right":
        return (row, col + 1)
    return current_pos

def rotate_left(orientation):
    orientations = ["Up", "Left", "Down", "Right"]
    return orientations[(orientations.index(orientation) + 1) % 4]

def rotate_right(orientation):
    orientations = ["Up", "Right", "Down", "Left"]
    return orientations[(orientations.index(orientation) + 1) % 4]

def animate_robot(path):
    global robot_arrow, orientation, current_position

    for i in range(1, len(path)):
        previous = path[i - 1]
        current = path[i]

        # Determine movement direction
        if current[0] < previous[0]:
            new_orientation = "Up"
        elif current[0] > previous[0]:
            new_orientation = "Down"
        elif current[1] < previous[1]:
            new_orientation = "Left"
        elif current[1] > previous[1]:
            new_orientation = "Right"
        else:
            new_orientation = orientation

        # Rotate if necessary
        if new_orientation != orientation:
            if (orientation, new_orientation) in [("Up", "Right"), ("Right", "Down"), ("Down", "Left"), ("Left", "Up")]:
                print("Rotating right")
            else:
                print("Rotating left")
            orientation = new_orientation

        # Move forward
        print("Moving forward")

        # Update robot arrow
        x = current[1] * cell_size + cell_size // 2
        y = current[0] * cell_size + cell_size // 2
        if robot_arrow:
            canvas.delete(robot_arrow)
        if orientation == "Up":
            robot_arrow = canvas.create_polygon(
                [(x, y - 10), (x - 5, y + 5), (x + 5, y + 5)], fill="blue"
            )
        elif orientation == "Down":
            robot_arrow = canvas.create_polygon(
                [(x, y + 10), (x - 5, y - 5), (x + 5, y - 5)], fill="blue"
            )
        elif orientation == "Left":
            robot_arrow = canvas.create_polygon(
                [(x - 10, y), (x + 5, y - 5), (x + 5, y + 5)], fill="blue"
            )
        elif orientation == "Right":
            robot_arrow = canvas.create_polygon(
                [(x + 10, y), (x - 5, y - 5), (x - 5, y + 5)], fill="blue"
            )
        canvas.update()
        canvas.after(300)

    current_position = path[-1]  # Update final position

def save_waypoints():
    with open(waypoints_file, "w") as file:
        json.dump(waypoints, file)

def reset_grid():
    global grid, current_position, waypoints, robot_arrow, obstacles, start_position
    current_position = None
    start_position = None
    waypoints = {}
    obstacles = set()
    robot_arrow = None
    grid = [[0 for _ in range(grid_size)] for _ in range(grid_size)]
    save_waypoints()
    draw_grid()

# Initialize Tkinter
root = tk.Tk()
root.title("Waypoint Navigation with Obstacles")
canvas = tk.Canvas(root, width=1920, height=1080, bg="white")
canvas.pack()

# Define cell size
cell_size = canvas.winfo_reqwidth() // grid_size

# Bind mouse click
canvas.bind("<Button-1>", on_cell_click)

# Control Panel
frame = tk.Frame(root)
def go_back_to_start():
    global current_position, start_position
    if start_position is None or current_position is None:
        messagebox.showerror("Error", "Starting position is not set!")
        return

    path = a_star(grid, current_position, start_position)
    if path:
        animate_robot(path)
        current_position = start_position
        messagebox.showinfo("Path Completed", "Returned to the starting position!")
    else:
        messagebox.showerror("Error", "No path found to return to the start!")
frame.pack()
tk.Button(frame, text="Go Back to Start", command=go_back_to_start).pack(side=tk.LEFT)
mode_label = tk.Label(frame, text="Mode: Waypoint")
mode_label.pack(side=tk.LEFT)
tk.Button(frame, text="Toggle Obstacle Mode", command=toggle_obstacle_mode).pack(side=tk.LEFT)
tk.Button(frame, text="Navigate to Waypoint", command=execute_path).pack(side=tk.LEFT)
tk.Button(frame, text="Reset Grid", command=reset_grid).pack(side=tk.LEFT)

# Draw initial grid
draw_grid()

# Start Tkinter loop
root.mainloop()
