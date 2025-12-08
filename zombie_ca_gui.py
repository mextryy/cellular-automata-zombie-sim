import tkinter as tk
from tkinter import ttk
import time
import numpy as np 

# Importujemy nasze moduły
from config import CellState, GRID_H, GRID_W, CELL_SIZE, COLORS
from grid import Grid
from simulation import run_simulation_step
from config import MAPA_TERENU_PLIK
from map_loader import load_map_from_image

CANVAS_W = GRID_W * CELL_SIZE
CANVAS_H = GRID_H * CELL_SIZE
INFO_BG = "#F0F0F0"
INFO_FG = "#000000"

class ZombieCA_GUI:
    def __init__(self, root):
        self.root = root
        root.title("Apokalipsa Zombie - Automat Komórkowy")
        
        # Inicjalizacja siatki, która automatycznie wczyta mapę
        self.grid_model = self._initialize_grid()
        
        self.running = False
        self.step_ms = 150
        self.last_time = 0
        self.step_count = 0

        self.canvas = tk.Canvas(root, width=CANVAS_W, height=CANVAS_H, bg="#FFFFFF", highlightthickness=0)
        self.canvas.grid(row=0, column=0, columnspan=6)

        self.info = tk.Label(root, text="", bg=INFO_BG, fg=INFO_FG, anchor="w", font=("Consolas", 11))
        self.info.grid(row=1, column=0, columnspan=6, sticky="we")

        # Przyciski (Uproszczone)
        btns = [
            ("Start/Pause (SPACE)", self.toggle_running),
            ("Step (N)", self.step_once),
            ("Restart Sim", self.load_new_sim),
        ]
        for i,(t,cmd) in enumerate(btns):
            ttk.Button(root, text=t, command=cmd).grid(row=2, column=i, sticky="we")

        root.bind("<space>", lambda e: self.toggle_running())
        root.bind("n", lambda e: self.step_once())

        self.draw()
        self.update_info()
        self.root.after(10, self.loop)

    def _initialize_grid(self):
     terrain_map = load_map_from_image(
        MAPA_TERENU_PLIK,
        GRID_W,
        GRID_H
    )
     return Grid(
        GRID_W,
        GRID_H,
        initial_humans=100,
        initial_zombies=5,
        terrain_map=terrain_map
    )

    def draw(self):
        self.canvas.delete("all")
        cell_size = CELL_SIZE
        
        for y in range(GRID_H):
            for x in range(GRID_W):
                cell = self.grid_model.cells[y][x]
                x1 = x * cell_size; y1 = y * cell_size
                x2 = x1 + cell_size; y2 = y1 + cell_size
                
                # Określenie koloru: Najpierw agenci, potem teren
                if cell.state != CellState.GROUND:
                    fill_color = COLORS.get(cell.state, COLORS[CellState.DEAD]) 
                else:
                    fill_color = COLORS.get(cell.terrain_type, COLORS[CellState.GROUND])
                
                self.canvas.create_rectangle(x1, y1, x2, y2, 
                                             fill=fill_color, 
                                             outline=fill_color, 
                                             tags="cell")


    def update_info(self):
        # Zliczanie populacji
        human_count = 0
        zombie_count = 0
        infected_count = 0
        for r in range(GRID_H):
            for c in range(GRID_W):
                state = self.grid_model.cells[r][c].state
                if state == CellState.HUMAN:
                    human_count += 1
                elif state == CellState.ZOMBIE:
                    zombie_count += 1
                elif state == CellState.INFECTED:
                    infected_count += 1

        s = (f"Krok: {self.step_count} | Ludzie: {human_count} | Zombie: {zombie_count} | Zarażeni: {infected_count} | "
             f"Opóźnienie: {self.step_ms}ms")
        self.info.config(text=s)

    def toggle_running(self):
        self.running = not self.running
        self.update_info()

    def step_once(self):
        """Wykonuje jeden krok symulacji logicznej i odświeża GUI."""
        self.grid_model = run_simulation_step(self.grid_model) 
        self.step_count += 1
        self.update_info()
        self.draw()

    def loop(self):
        if self.running:
            now = time.time() * 1000.0
            if now - self.last_time >= self.step_ms:
                self.step_once()
                self.last_time = now
        self.root.after(10, self.loop)

    def load_new_sim(self):
        """Ładuje nową symulację (automatycznie wczytując mapę z pliku)."""
        self.grid_model = self._initialize_grid()
        self.step_count = 0
        self.running = False
        self.update_info()
        self.draw()