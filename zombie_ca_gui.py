import tkinter as tk
from tkinter import ttk
import time
import numpy as np 

# Importujemy config, by móc modyfikować INFECTION_PROBABILITY w czasie rzeczywistym
import config
from config import CellState, GRID_H, GRID_W, CELL_SIZE, COLORS
from grid import Grid
from simulation import run_simulation_step
from config import MAPA_TERENU_PLIK, MOVEMENT_MODIFIERS, INFECTION_PROBABILITY 
from map_loader import load_map_from_image

CANVAS_W = GRID_W * CELL_SIZE
CANVAS_H = GRID_H * CELL_SIZE
INFO_BG = "#F0F0F0"
INFO_FG = "#000000"

class ZombieCA_GUI:
    def __init__(self, root):
        self.root = root
        root.title("Apokalipsa Zombie - Automat Komórkowy")
        
        self.grid_model = self._initialize_grid()
        
        # DEFINICJA LEGENDY KOLORÓW
        self.legend_items = [
            (CellState.HUMAN, "Człowiek"),
            (CellState.ZOMBIE, "Zombie"),
            (CellState.INFECTED, "Zarażony"),
            (CellState.DEAD, "Martwy (zaniknie)"),
            
            # Tereny statyczne z opisem modyfikatora ruchu
            (CellState.STREET, f"Ulica (x{MOVEMENT_MODIFIERS.get(CellState.STREET.value, '1.5')} szybciej)"),
            (CellState.GROUND, f"Ziemia (Neutralnie x{MOVEMENT_MODIFIERS.get(CellState.GROUND.value, '1.0')})"),
            (CellState.GREEN_AREA, f"Teren Zielony (x{MOVEMENT_MODIFIERS.get(CellState.GREEN_AREA.value, '0.8')} wolniej)"),
            (CellState.BUILDING, f"Budynek (x{MOVEMENT_MODIFIERS.get(CellState.BUILDING.value, '0.2')} wolniej)"),
            (CellState.WATER, f"Woda (x{MOVEMENT_MODIFIERS.get(CellState.WATER.value, '0.1')} wolniej)"),
            (CellState.HILL, "Wzniesienie (wolniej)"), 
        ]
        
        self.running = False
        self.step_ms = 150
        self.last_time = 0
        self.step_count = 0
        
        # NARZĘDZIA: Domyślny tryb
        self.current_tool = 'BUILD' 
        self._tool_state_map = {}
        self.tool_var = None

        # PŁÓTNO (MAPA) - Zajmuje kolumny 0-4 w wierszu 0
        self.canvas = tk.Canvas(root, width=CANVAS_W, height=CANVAS_H, bg="#FFFFFF", highlightthickness=0)
        self.canvas.grid(row=0, column=0, columnspan=5, sticky="nsw") 

        # =========================================================
        # ZMIANA UKŁADU: JEDNA RAMA DLA CAŁEGO PANELU PO PRAWEJ STRONIE
        # =========================================================
        self.right_panel_frame = tk.Frame(root)
        self.right_panel_frame.grid(row=0, column=5, columnspan=1, sticky="nsw", padx=10) 
        
        # 1. RAMA LEGENDY (używa pack())
        self.legend_frame = tk.Frame(self.right_panel_frame)
        self.legend_frame.pack(fill='x', pady=(0, 5))
        self._draw_legend(self.legend_frame)

        # 2. RAMA DLA NARZĘDZI (używa pack(), pod legendą)
        self.tool_frame = tk.Frame(self.right_panel_frame)
        self.tool_frame.pack(fill='x', pady=(5, 5)) 
        self._draw_tools(self.tool_frame) 

        # 3. RAMA DLA PARAMETRÓW (używa pack(), pod narzędziami)
        self.param_frame = tk.Frame(self.right_panel_frame)
        self.param_frame.pack(fill='x', pady=(5, 0))
        self._draw_parameters(self.param_frame)
        # =========================================================

        # WIĄZANIE KLIKNIĘCIA Z FUNKCJĄ OBSŁUGUJĄCĄ ZMIANĘ TERENU
        self.canvas.bind("<Button-1>", self._handle_click)
        
        # RAMA INFORMACYJNA - Zajmuje całą szerokość pod mapą i prawym panelem
        self.info = tk.Label(root, text="", bg=INFO_BG, fg=INFO_FG, anchor="w", font=("Consolas", 11))
        self.info.grid(row=1, column=0, columnspan=6, sticky="we") 
        
        # Przyciski sterujące (wiersz 2, kolumny 0-2)
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
    
    # ----------------------------------------------------
    # METODY RYSOWANIA GUI
    # ----------------------------------------------------

    def _draw_legend(self, parent_frame):
        """Rysuje mapę kolorów w ramie legendy."""
        legend_row = 0
        
        tk.Label(parent_frame, text="Legenda stanów i terenu:", font=("Consolas", 9, "bold")).grid(row=legend_row, column=0, columnspan=2, sticky="w", pady=(0, 5))
        legend_row += 1
        
        for state, label_text in self.legend_items:
            color = COLORS[state]
            
            color_swatch = tk.Canvas(parent_frame, width=10, height=10, bg=color, highlightthickness=1, highlightbackground="black")
            color_swatch.grid(row=legend_row, column=0, sticky="w", padx=(0, 5))
            
            tk.Label(parent_frame, text=label_text, font=("Consolas", 8), anchor="w").grid(row=legend_row, column=1, sticky="w")
            
            legend_row += 1

    def _draw_tools(self, parent_frame):
        """Rysuje panel z interaktywnymi narzędziami do zmiany terenu."""
        tk.Label(parent_frame, text="Narzędzia zmiany terenu:", font=("Consolas", 9, "bold")).grid(row=0, column=0, columnspan=2, sticky="w", pady=(0, 5))
        
        tools = [
            ('BUILD', "🧱 Stawiaj budynki (BUILDING)", CellState.BUILDING), 
            ('WATER', "🌊 Zrzut wody (WATER)", CellState.WATER),         
            ('GREEN', "🌿 Sadź zieleń (GREEN)", CellState.GREEN_AREA), 
        ]

        self.tool_var = tk.StringVar(value=self.current_tool)
        
        row = 1
        for tool_name, label, cell_state in tools:
            rb = ttk.Radiobutton(
                parent_frame,
                text=label,
                variable=self.tool_var,
                value=tool_name,
                command=lambda name=tool_name: self._set_current_tool(name)
            )
            rb.grid(row=row, column=0, sticky="w", pady=1)
            row += 1
            
        self._tool_state_map = {
            'BUILD': CellState.BUILDING,
            'WATER': CellState.WATER,
            'GREEN': CellState.GREEN_AREA,
        }

    def _draw_parameters(self, parent_frame):
        """Rysuje suwak do kontroli parametrów symulacji (INFECTION_PROBABILITY)."""
        tk.Label(parent_frame, text="Kontrola parametrów:", font=("Consolas", 9, "bold")).grid(row=0, column=0, columnspan=2, sticky="w", pady=(0, 5))
        
        # 1. Etykieta wyświetlająca aktualną wartość
        self.prob_label = tk.Label(parent_frame, text=f"Prawdopodobieństwo Infekcji (x): {config.INFECTION_PROBABILITY:.2f}", font=("Consolas", 8))
        self.prob_label.grid(row=1, column=0, sticky="w", pady=(0, 2))
        
        # 2. Suwak (Scale)
        self.prob_scale = tk.Scale(
            parent_frame,
            from_=0.0,
            to=1.0,
            resolution=0.05,
            orient=tk.HORIZONTAL,
            length=200,
            command=self._update_infection_prob
        )
        self.prob_scale.set(config.INFECTION_PROBABILITY)
        self.prob_scale.grid(row=2, column=0, sticky="we")

    # ----------------------------------------------------
    # METODY INTERAKCJI
    # ----------------------------------------------------

    def _set_current_tool(self, tool_name):
        """Ustawia aktualnie wybrane narzędzie do modyfikacji terenu."""
        self.current_tool = tool_name
        self.info.config(text=f"Wybrano narzędzie do modyfikacji terenu: {tool_name}")

    def _update_infection_prob(self, value):
        """Aktualizuje globalne prawdopodobieństwo infekcji w config.py."""
        prob = float(value)
        config.INFECTION_PROBABILITY = prob 
        self.prob_label.config(text=f"Prawdopodobieństwo Infekcji (x): {prob:.2f}")

    def _handle_click(self, event):
        """Obsługuje kliknięcie na płótnie i modyfikuje teren."""
        
        grid_x = event.x // CELL_SIZE
        grid_y = event.y // CELL_SIZE
        
        if 0 <= grid_y < GRID_H and 0 <= grid_x < GRID_W:
            
            tool_state = self._tool_state_map.get(self.current_tool)
            
            if tool_state is not None:
                cell_to_change = self.grid_model.cells[grid_y][grid_x]
                
                # Zezwalamy na zmianę terenu tylko jeśli komórka nie jest zajęta przez aktywnego agenta
                if cell_to_change.state == CellState.GROUND:
                    
                    cell_to_change.terrain_type = tool_state
                    
                    self.info.config(text=f"Zmieniono teren w ({grid_y}, {grid_x}) na {tool_state.name}")
                    self.draw() 
                else:
                    self.info.config(text=f"Błąd: Nie można zmieniać terenu pod aktywnym agentem ({cell_to_change.state.name}).")
            else:
                self.info.config(text=f"Brak aktywnego narzędzia do modyfikacji terenu.")
                
    # ----------------------------------------------------
    # METODY RYSOWANIA SIATKI I PĘTLI SYMULACJI
    # ----------------------------------------------------

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