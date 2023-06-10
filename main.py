import tkinter as tk
from tkinter import messagebox
import numpy as np


class MainMenu:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Game of Life - Main Menu")

        self.play_button = tk.Button(self.root, text="Play", command=self.play_game)
        self.play_button.pack()

        self.host_button = tk.Button(self.root, text="Host", command=self.host_game)
        self.host_button.pack()

        self.exit_button = tk.Button(self.root, text="Exit", command=self.root.quit)
        self.exit_button.pack()

    def run(self):
        self.root.mainloop()

    def play_game(self):
        self.root.destroy()  # Close the main menu window
        gui = GameOfLifeGUI(100, 70, 10)
        gui.run()

    def host_game(self):
        print("Host")


class GameOfLifeGUI:
    def __init__(self, width, height, cell_size):
        self.width = width
        self.height = height
        self.cell_size = cell_size
        self.field = np.zeros((height, width), dtype=bool)
        self.generations = 0
        self.is_running = False

        self.zoom_scale = 1.0  # Initial zoom scale
        self.zoom_delta = 0.1  # Zoom increment/decrement per scroll step
        self.pan_distance = 10  # Distance to pan with each arrow key press

        self.view_x = 0  # X coordinate of top-left corner of the view
        self.view_y = 0  # Y coordinate of top-left corner of the view

        self.ruler_active = False  # Flag indicating if ruler is active
        self.ruler_start_x = -1  # X coordinate of the ruler start point
        self.ruler_start_y = -1  # Y coordinate of the ruler start point

        self.show_borders = False  # Flag indicating if cell borders should be displayed

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

        self.control_frame = tk.Frame(self.root)
        self.control_frame.pack()

        self.play_button = tk.Button(self.control_frame, text="Play", command=self.toggle_game)
        self.play_button.pack(side="left")

        self.step_button = tk.Button(self.control_frame, text="Step", command=self.step_generation)
        self.step_button.pack(side="left")

        self.reset_button = tk.Button(self.control_frame, text="Reset", command=self.reset_game)
        self.reset_button.pack(side="left")

        self.ruler_button = tk.Button(self.control_frame, text="Ruler", command=self.toggle_ruler)
        self.ruler_button.pack(side="left")

        self.border_button = tk.Button(self.control_frame, text="Toggle Borders", command=self.toggle_borders)
        self.border_button.pack(side="left")

        self.draw_field()

    def run(self):
        self.root.after(0, self.update_field)
        self.root.mainloop()

    def toggle_game(self):
        if self.is_running:
            self.pause_game()
            self.play_button.config(text="Play")
            self.ruler_button.config(state=tk.NORMAL)
        else:
            self.play_game()
            self.play_button.config(text="Stop")
            self.ruler_button.config(state=tk.DISABLED)

    def toggle_cell(self, event):
        if not self.is_running and not self.ruler_active:
            x = int((event.x + self.view_x * self.cell_size * self.zoom_scale) // (self.zoom_scale * self.cell_size))
            y = int((event.y + self.view_y * self.cell_size * self.zoom_scale) // (self.zoom_scale * self.cell_size))
            if 0 <= x < self.width and 0 <= y < self.height:
                self.field[y][x] = not self.field[y][x]
                self.draw_field()

    def update_field(self):
        if self.is_running:
            self.root.title(f"Game of Life - Generation {self.generations}")
            self.field = self.next_generation(self.field)
            self.draw_field()
            self.generations += 1
        self.root.after(100, self.update_field)

    def draw_field(self):
        self.canvas.delete(tk.ALL)

        # Draw field outline
        x1 = -self.view_x * self.cell_size * self.zoom_scale
        y1 = -self.view_y * self.cell_size * self.zoom_scale
        x2 = x1 + self.width * self.cell_size * self.zoom_scale
        y2 = y1 + self.height * self.cell_size * self.zoom_scale
        self.canvas.create_rectangle(x1, y1, x2, y2, outline="black")

        if self.show_borders:
            # Draw horizontal cell borders
            for i in range(self.height + 1):
                y = (i - self.view_y) * self.cell_size * self.zoom_scale
                self.canvas.create_line(
                    -self.view_x * self.cell_size * self.zoom_scale,
                    y,
                    (-self.view_x + self.width) * self.cell_size * self.zoom_scale,
                    y,
                    fill="black"
                )

            # Draw vertical cell borders
            for j in range(self.width + 1):
                x = (j - self.view_x) * self.cell_size * self.zoom_scale
                self.canvas.create_line(
                    x,
                    -self.view_y * self.cell_size * self.zoom_scale,
                    x,
                    (-self.view_y + self.height) * self.cell_size * self.zoom_scale,
                    fill="black"
                )

        # Draw filled-in squares
        for i in range(self.height):
            for j in range(self.width):
                if self.field[i, j]:
                    x1 = (j - self.view_x) * self.cell_size * self.zoom_scale
                    y1 = (i - self.view_y) * self.cell_size * self.zoom_scale
                    x2 = x1 + self.cell_size * self.zoom_scale
                    y2 = y1 + self.cell_size * self.zoom_scale
                    self.canvas.create_rectangle(x1, y1, x2, y2, fill="black")

        if self.ruler_active and self.ruler_start_x >= 0 and self.ruler_start_y >= 0:
            x1 = (self.ruler_start_x - self.view_x) * self.cell_size * self.zoom_scale
            y1 = (self.ruler_start_y - self.view_y) * self.cell_size * self.zoom_scale
            x2 = x1 + self.cell_size * self.zoom_scale
            y2 = y1 + self.cell_size * self.zoom_scale
            self.canvas.create_rectangle(x1, y1, x2, y2, fill="blue")

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
        self.field = np.zeros((self.height, self.width), dtype=bool)
        self.generations = 0
        self.root.title("Game of Life")
        self.play_button.config(text="Play")
        self.draw_field()

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


    def toggle_ruler(self):
        self.ruler_start_x = -1
        self.ruler_start_y = -1
        self.ruler_active = not self.ruler_active
        self.draw_field()
        if self.ruler_active:
            self.ruler_button.config(text='Cancel')
            self.canvas.bind("<Button-1>", self.ruler_click)
            self.play_button.config(state=tk.DISABLED)
        else:
            self.ruler_button.config(text='Ruler')
            self.canvas.bind("<Button-1>", self.toggle_cell)
            self.play_button.config(state=tk.NORMAL)
        self.draw_field()

    def ruler_click(self, event):
        x = int((event.x + self.view_x * self.cell_size * self.zoom_scale) // (self.zoom_scale * self.cell_size))
        y = int((event.y + self.view_y * self.cell_size * self.zoom_scale) // (self.zoom_scale * self.cell_size))
        if 0 <= x < self.width and 0 <= y < self.height:
            if self.ruler_start_x == -1 and self.ruler_start_y == -1:
                self.ruler_start_x = x
                self.ruler_start_y = y
            else:
                distance = abs(x - self.ruler_start_x) + abs(y - self.ruler_start_y)
                messagebox.showinfo("Ruler", f"The distance in cells is: {distance}")
                self.toggle_ruler()
        self.draw_field()

    def toggle_borders(self):
        self.show_borders = not self.show_borders
        self.draw_field()

    def count_neighbors(self, field, x, y):
        return np.sum(field[max(0, y - 1):min(y + 2, self.height), max(0, x - 1):min(x + 2, self.width)]) - field[y, x]

    def next_generation(self, field):
        new_field = np.zeros((self.height, self.width), dtype=bool)
        for y in range(self.height):
            for x in range(self.width):
                neighbors = self.count_neighbors(field, x, y)
                if field[y, x]:
                    if neighbors == 2 or neighbors == 3:
                        new_field[y, x] = True
                else:
                    if neighbors == 3:
                        new_field[y, x] = True
        return new_field


if __name__ == "__main__":
    menu = MainMenu()
    menu.run()
