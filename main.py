import tkinter as tk

class GameOfLifeGUI:
    def __init__(self, width, height, cell_size):
        self.width = width
        self.height = height
        self.cell_size = cell_size
        self.field = [[False] * width for _ in range(height)]
        self.generations = 0
        self.is_running = False

        self.zoom_scale = 1.0  # Initial zoom scale
        self.zoom_delta = 0.1  # Zoom increment/decrement per scroll step
        self.pan_distance = 10  # Distance to pan with each arrow key press

        self.view_x = 0  # X coordinate of top-left corner of the view
        self.view_y = 0  # Y coordinate of top-left corner of the view

        self.root = tk.Tk()
        self.root.title("Game of Life")

        self.canvas = tk.Canvas(
            self.root,
            width=self.width * self.cell_size,
            height=self.height * self.cell_size,
            bg="white"
        )
        self.canvas.bind("<Button-1>", self.toggle_cell)
        self.canvas.bind("<Key>", self.pan_with_arrow_keys)
        self.canvas.bind("<MouseWheel>", self.zoom)
        self.canvas.focus_set()
        self.canvas.pack()

        self.menu_bar = tk.Menu(self.root)
        self.root.config(menu=self.menu_bar)

        self.file_menu = tk.Menu(self.menu_bar, tearoff=0)
        self.file_menu.add_command(label="Open")
        self.file_menu.add_command(label="Save")
        self.file_menu.add_separator()
        self.file_menu.add_command(label="Exit", command=self.root.quit)

        self.edit_menu = tk.Menu(self.menu_bar, tearoff=0)
        self.edit_menu.add_command(label="Clear Field", command=self.clear_field)
        self.edit_menu.add_command(label="Set Cell Alive", command=self.set_cell_alive)
        self.edit_menu.add_command(label="Set Cell Dead", command=self.set_cell_dead)

        self.menu_bar.add_cascade(label="File", menu=self.file_menu)
        self.menu_bar.add_cascade(label="Edit", menu=self.edit_menu)

        self.control_frame = tk.Frame(self.root)
        self.control_frame.pack()

        self.pause_button = tk.Button(self.control_frame, text="Pause", command=self.pause_game)
        self.pause_button.pack(side="left")

        self.play_button = tk.Button(self.control_frame, text="Play", command=self.play_game)
        self.play_button.pack(side="left")

        self.step_button = tk.Button(self.control_frame, text="Step", command=self.step_generation)
        self.step_button.pack(side="left")

        self.reset_button = tk.Button(self.control_frame, text="Reset", command=self.reset_game)
        self.reset_button.pack(side="left")

    def run(self):
        self.root.after(0, self.update_field)
        self.root.mainloop()

    def update_field(self):
        if self.is_running:
            self.root.title(f"Game of Life - Generation {self.generations}")
            self.field = self.next_generation(self.field)
            self.draw_field()
            self.generations += 1
        self.root.after(100, self.update_field)

    def draw_field(self):
        self.canvas.delete(tk.ALL)
        for i in range(self.height):
            for j in range(self.width):
                x1 = (j - self.view_x) * self.cell_size * self.zoom_scale
                y1 = (i - self.view_y) * self.cell_size * self.zoom_scale
                x2 = x1 + self.cell_size * self.zoom_scale
                y2 = y1 + self.cell_size * self.zoom_scale

                if self.field[i][j]:
                    self.canvas.create_rectangle(x1, y1, x2, y2, fill="black")
                else:
                    self.canvas.create_rectangle(x1, y1, x2, y2, fill="white")

    def toggle_cell(self, event):
        if not self.is_running:
            x = int((event.x + self.view_x * self.cell_size * self.zoom_scale) / (self.zoom_scale * self.cell_size))
            y = int((event.y + self.view_y * self.cell_size * self.zoom_scale) / (self.zoom_scale * self.cell_size))
            if 0 <= x < self.width and 0 <= y < self.height:
                self.field[y][x] = not self.field[y][x]
                self.draw_field()

    def clear_field(self):
        if not self.is_running:
            self.field = [[False] * self.width for _ in range(self.height)]
            self.draw_field()

    def set_cell_alive(self):
        if not self.is_running:
            x = int(input("Enter the x-coordinate of the cell: "))
            y = int(input("Enter the y-coordinate of the cell: "))
            if 0 <= x < self.width and 0 <= y < self.height:
                self.field[y][x] = True
                self.draw_field()

    def set_cell_dead(self):
        if not self.is_running:
            x = int(input("Enter the x-coordinate of the cell: "))
            y = int(input("Enter the y-coordinate of the cell: "))
            if 0 <= x < self.width and 0 <= y < self.height:
                self.field[y][x] = False
                self.draw_field()

    def pause_game(self):
        self.is_running = False

    def play_game(self):
        self.is_running = True

    def step_generation(self):
        if not self.is_running:
            self.root.title(f"Game of Life - Generation {self.generations}")
            self.field = self.next_generation(self.field)
            self.draw_field()
            self.generations += 1

    def reset_game(self):
        self.pause_game()
        self.clear_field()
        self.generations = 0
        self.root.title("Game of Life")

    def zoom(self, event):
        if event.delta > 0:
            # Scroll Up - Zoom In
            self.zoom_scale += self.zoom_delta
        elif event.delta < 0:
            # Scroll Down - Zoom Out
            self.zoom_scale -= self.zoom_delta

        # Set a lower bound for zoom scale
        self.zoom_scale = max(self.zoom_scale, 0.1)

        # Redraw the field with the new zoom scale
        self.draw_field()

    def pan_with_arrow_keys(self, event):
        if event.keysym == "Up":
            self.view_y -= self.pan_distance / (self.cell_size * self.zoom_scale)
        elif event.keysym == "Down":
            self.view_y += self.pan_distance / (self.cell_size * self.zoom_scale)
        elif event.keysym == "Left":
            self.view_x -= self.pan_distance / (self.cell_size * self.zoom_scale)
        elif event.keysym == "Right":
            self.view_x += self.pan_distance / (self.cell_size * self.zoom_scale)

        # Redraw the field with the updated view position
        self.draw_field()


    def count_neighbors(self, field, x, y):
        count = 0
        for i in range(-1, 2):
            for j in range(-1, 2):
                if i == 0 and j == 0:
                    continue
                if 0 <= x + i < self.width and 0 <= y + j < self.height:
                    if field[y + j][x + i]:
                        count += 1
        return count

    def next_generation(self, field):
        new_field = [[False] * self.width for _ in range(self.height)]
        for y in range(self.height):
            for x in range(self.width):
                neighbors = self.count_neighbors(field, x, y)
                if field[y][x]:
                    if neighbors == 2 or neighbors == 3:
                        new_field[y][x] = True
                else:
                    if neighbors == 3:
                        new_field[y][x] = True
        return new_field

if __name__ == "__main__":
    gui = GameOfLifeGUI(50, 50, 10)
    gui.run()
