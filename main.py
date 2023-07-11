import json
import tkinter as tk
from tkinter import filedialog, messagebox
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
        gui = GameOfLifeGUI(100, 70, 10, 0.1, 1, 'C:/Users/avary/Desktop/folder')
        gui.run()

    def host_game(self):
        print("Host")


class SettingsWindow:
    def __init__(self, parent, main_menu):
        self.parent = parent
        self.main_menu = main_menu
        self.settings_window = tk.Toplevel(parent)
        self.settings_window.title("Settings")

        self.folder_path = main_menu.get_schematics_folder()

        self.zoom_sensitivity_label = tk.Label(self.settings_window, text="Zoom Sensitivity:")
        self.zoom_sensitivity_label.pack()

        self.zoom_sensitivity_scale = tk.Scale(
            self.settings_window,
            from_=0.1,
            to=1.0,
            resolution=0.1,
            orient=tk.HORIZONTAL,
            length=200,
            showvalue=main_menu.get_zoom_sensitivity()
        )

        self.zoom_sensitivity_scale.set(self.main_menu.get_zoom_sensitivity())
        self.zoom_sensitivity_scale.pack()

        self.pan_distance_label = tk.Label(self.settings_window, text="Pan Distance:")
        self.pan_distance_label.pack()

        self.pan_distance_scale = tk.Scale(
            self.settings_window,
            from_=1,
            to=20,
            resolution=1,
            orient=tk.HORIZONTAL,
            length=200,
            showvalue=main_menu.get_pan_distance()
        )

        self.pan_distance_scale.set(self.main_menu.get_pan_distance())
        self.pan_distance_scale.pack()

        self.schematics_folder_label = tk.Label(self.settings_window, text="Schematics Folder:")
        self.schematics_folder_label.pack()

        self.schematics_folder_name_label = tk.Label(self.settings_window, text=f"{self.folder_path}")
        self.schematics_folder_name_label.pack()

        self.schematics_folder_button = tk.Button(
            self.settings_window,
            text="Select Folder",
            command=self.select_schematics_folder
        )
        self.schematics_folder_button.pack()

        self.save_button = tk.Button(self.settings_window, text="Save", command=lambda: self.save(float(self.zoom_sensitivity_scale.get()), float(self.pan_distance_scale.get()), self.folder_path))
        self.save_button.pack()

    def save(self, zoom_sensitivity, pan_distance, schematics_folder):
        self.main_menu.update_settings(zoom_sensitivity, pan_distance, schematics_folder)
        self.close_window()



    def run(self):
        self.settings_window.mainloop()

    def close_window(self):
        self.settings_window.destroy()
        self.main_menu.settings_window = None

    def select_schematics_folder(self):
        folder_path = filedialog.askdirectory(parent=self.settings_window)
        if folder_path:
            self.folder_path = folder_path
            self.schematics_folder_name_label.config(text=self.folder_path)


class GameOfLifeGUI:
    def __init__(self, width, height, cell_size, zoom_sensitivity, pan_distance, schematics_folder):
        self.width = width
        self.height = height
        self.cell_size = cell_size
        self.field = np.zeros((height, width), dtype=bool)
        self.generations = 0
        self.is_running = False

        self.zoom_scale = 1.0  # Initial zoom scale
        self.zoom_delta = zoom_sensitivity  # Zoom increment/decrement per scroll step
        self.pan_distance = pan_distance  # Distance to pan with each arrow key press

        self.view_x = 0  # X coordinate of top-left corner of the view
        self.view_y = 0  # Y coordinate of top-left corner of the view

        self.ruler_active = False  # Flag indicating if ruler is active
        self.ruler_start_x = -1  # X coordinate of the ruler start point
        self.ruler_start_y = -1  # Y coordinate of the ruler start point

        self.selection_start_x = -1  # X coordinate of the selection start point
        self.selection_start_y = -1  # Y coordinate of the selection start point
        self.selection_end_x = -1  # X coordinate of the selection end point
        self.selection_end_y = -1   # Y coordinate of the selection end point

        self.show_borders = False  # Flag indicating if cell borders should be displayed

        self.schematics_folder = schematics_folder

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

        self.settings_menu = tk.Menu(self.root, tearoff=False)
        self.settings_menu.add_command(label="Toggle Borders", command=self.toggle_borders)
        self.settings_menu.add_command(label="Settings", command=self.open_settings)

        self.schematics_menu = tk.Menu(self.root, tearoff=False)
        #self.schematics_menu.add_command(label="Load Schematic", command=self.load_schematic_menu)
        self.schematics_menu.add_command(label="Save Schematic", command=self.save_schematic)

        self.menu_bar = tk.Menu(self.root)
        self.menu_bar.add_command(label="Exit", command=self.return_to_main_menu)
        self.menu_bar.add_cascade(label="Settings", menu=self.settings_menu)
        self.menu_bar.add_cascade(label="Schematics", menu=self.schematics_menu)
        self.root.config(menu=self.menu_bar)

        self.draw_field()

    def save_schematic(self):
        self.canvas.bind("<Button-1>", self.start_selection)
        self.canvas.bind("<B1-Motion>", self.update_selection)
        self.canvas.bind("<ButtonRelease-1>", self.end_selection)
        self.play_button.config(state=tk.DISABLED)
        self.reset_button.config(state=tk.DISABLED)

    def start_selection(self, event):
        self.selection_start_x = int((event.x) // (self.zoom_scale * self.cell_size))
        self.selection_start_y = int((event.y) // (self.zoom_scale * self.cell_size))
        self.draw_field()

    def update_selection(self, event):
        self.selection_end_x = int((event.x) // (self.zoom_scale * self.cell_size))+1
        self.selection_end_y = int((event.y) // (self.zoom_scale * self.cell_size))+1
        self.draw_field()

    def end_selection(self, event):
        self.update_selection(event)
        self.canvas.unbind("<B1-Motion>")
        self.canvas.unbind("<ButtonRelease-1>")
        self.canvas.bind("<Button-1>", self.toggle_cell)
        self.save_schematic_dialog()

    def save_schematic_dialog(self):
        dialog = tk.Toplevel(self.root)
        dialog.title("Save Schematic")

        filename_label = tk.Label(dialog, text="Name of the schematic:")
        filename_label.pack()

        filename_entry = tk.Entry(dialog)
        filename_entry.pack()

        save_button = tk.Button(
            dialog,
            text="Save",
            command=lambda: self.save_and_close_schematic(dialog, filename_entry.get())
        )
        save_button.pack()

        cancel_button = tk.Button(dialog, text="Cancel", command=lambda: self.save_schematic_reset(dialog))
        cancel_button.pack()

        dialog.protocol("WM_DELETE_WINDOW", lambda: self.save_schematic_reset(dialog))

    def save_and_close_schematic(self,dialog=None,filename_entry=None):
        self.save_selection_as_schematic(filename_entry)
        self.save_schematic_reset(dialog)

    def save_schematic_reset(self,dialog=None):
        try:
            dialog.destroy()
        except AttributeError:
            print("cry abt it")
        self.selection_start_x = -1
        self.selection_start_y = -1
        self.selection_end_x = -1
        self.selection_end_y = -1
        self.play_button.config(state=tk.NORMAL)
        self.reset_button.config(state=tk.NORMAL)
        self.draw_field()

    def save_selection_as_schematic(self, filename):
        selected_cells = self.get_selected_cells()
        if selected_cells.any():
            schematic_data = {
                "field": selected_cells.tolist(),  # Convert the selection to a nested list
                # Add any other necessary data you want to save in the schematic
            }
            try:
                with open(self.schematics_folder + '/' + filename, "w") as file:
                    json.dump(schematic_data, file)
                messagebox.showinfo("Save Schematic", "Schematic saved successfully.")
                self.save_schematic_reset()
            except PermissionError:
                messagebox.showerror("Save Schematic", "Could not save the schematic.")
        else:
            messagebox.showwarning("Save Schematic", "No cells selected.")
            self.save_schematic_reset()

    def get_selected_cells(self):
        # Calculate the selection boundaries
        min_cell_x = min(self.selection_start_x, self.selection_end_x)
        max_cell_x = max(self.selection_start_x, self.selection_end_x)
        min_cell_y = min(self.selection_start_y, self.selection_end_y)
        max_cell_y = max(self.selection_start_y, self.selection_end_y)

        # Create a subarray of the selected cells from the game field
        selected_cells = self.field[min_cell_y: max_cell_y, min_cell_x: max_cell_x]

        return selected_cells

    def update_settings(self, zoom_sensitivity, pan_distance, schematics_folder):
        self.zoom_delta = zoom_sensitivity
        self.pan_distance = pan_distance
        self.schematics_folder = schematics_folder

    def open_settings(self):
        settings_window = SettingsWindow(self.root, self)
        settings_window.run()

    def get_zoom_sensitivity(self):
        return self.zoom_delta

    def get_pan_distance(self):
        return self.pan_distance

    def get_schematics_folder(self):
        return self.schematics_folder

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

        # Draw selection rectangle
        if self.selection_start_x >= 0 and self.selection_start_y >= 0 and self.selection_end_x >= 0 and self.selection_end_y >= 0:
            self.canvas.create_rectangle(self.selection_start_x * self.zoom_scale * self.cell_size, self.selection_start_y * self.zoom_scale * self.cell_size, self.selection_end_x * self.zoom_scale * self.cell_size, self.selection_end_y * self.zoom_scale * self.cell_size, outline="red")

        if self.ruler_active and self.ruler_start_x >= 0 and self.ruler_start_y >= 0:
            x1 = (self.ruler_start_x - self.view_x) * self.cell_size * self.zoom_scale
            y1 = (self.ruler_start_y - self.view_y) * self.cell_size * self.zoom_scale
            x2 = x1 + self.cell_size * self.zoom_scale
            y2 = y1 + self.cell_size * self.zoom_scale
            self.canvas.create_rectangle(x1, y1, x2, y2, fill="blue")

        self.canvas.pack()

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
            self.view_y -= self.pan_distance
        elif event.keysym == "Down":
            self.view_y += self.pan_distance
        elif event.keysym == "Left":
            self.view_x -= self.pan_distance
        elif event.keysym == "Right":
            self.view_x += self.pan_distance

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

    def return_to_main_menu(self):
        self.root.destroy()
        menu = MainMenu()
        menu.run()


if __name__ == "__main__":
    menu = MainMenu()
    menu.run()
