# grid.py
import random
from config import CellState, INCUBATION_TIME, MAPA_TERENU_PLIK

class Cell:
    """Reprezentuje pojedynczą komórkę na siatce z jej stanem dynamicznym, terenem i zmiennymi lokalnymi."""
    def __init__(self, terrain_type=CellState.GROUND):
        # Stan statyczny/teren
        self.terrain_type = terrain_type 
        # Stan dynamiczny (domyślnie GROUND, jeśli nie ma agenta)
        self.state = CellState.GROUND
        # Zmienne lokalne (dla agentów i specjalnych stanów)
        self.local_vars = {}

class Grid:
    """Reprezentuje całą mapę (siatkę Automatu Komórkowego)."""
    def __init__(self, width, height, initial_humans, initial_zombies, terrain_map=None):
        self.width = width
        self.height = height

        # Tworzymy pustą siatkę komórek
        self.cells = [[Cell() for _ in range(width)] for _ in range(height)]

        # Inicjalizacja terenu
        self._initialize_terrain(terrain_map)

        # Rozmieszczenie ludzi i zombie
        self._place_agents(initial_humans, initial_zombies)

    def _initialize_terrain(self, terrain_map=None):
     for r in range(self.height):
        for c in range(self.width):
            if terrain_map is None:
                self.cells[r][c].terrain_type = CellState.GROUND
            else:
                # Konwertujemy liczby z mapy na CellState
                self.cells[r][c].terrain_type = CellState(terrain_map[r][c])
    def _place_agents(self, num_humans, num_zombies):
        """Losowo rozmieszcza początkową liczbę ludzi i zombie."""
        available_cells = [(r, c) for r in range(self.height) for c in range(self.width) 
                           if self.cells[r][c].terrain_type not in [CellState.WATER, CellState.BUILDING]]
        random.shuffle(available_cells)
        
        # Umieść ludzi
        for i in range(min(num_humans, len(available_cells))):
            r, c = available_cells.pop(0)
            self.cells[r][c].state = CellState.HUMAN

        # Umieść zombie
        for i in range(min(num_zombies, len(available_cells))):
            r, c = available_cells.pop(0)
            self.cells[r][c].state = CellState.ZOMBIE


    def get_neighbors(self, r, c):
        """Zwraca listę obiektów Cell sąsiadujących z (r, c) (sąsiedztwo Moore'a - 8 pól)."""
        neighbors = []
        for dr in [-1, 0, 1]:
            for dc in [-1, 0, 1]:
                if dr == 0 and dc == 0:
                    continue
                nr, nc = r + dr, c + dc
                
                # Warunek na granice (całkowicie zamykamy mapę na krawędziach)
                if 0 <= nr < self.height and 0 <= nc < self.width:
                    neighbors.append(self.cells[nr][nc])
        return neighbors

    def find_nearest_agent(self, r, c, target_states):
        """Znajduje najbliższego agenta o danym stanie (prosta heurystyka odległości Manhattan)."""
        min_dist = float('inf')
        nearest_coords = (r, c)
        
        for tr in range(self.height):
            for tc in range(self.width):
                if self.cells[tr][tc].state in target_states:
                    # Odległość Manhattan
                    dist = abs(r - tr) + abs(c - tc)
                    
                    if dist < min_dist:
                        min_dist = dist
                        nearest_coords = (tr, tc)
                        
        # Jeśli nie znaleziono celu, agent pozostaje w miejscu
        if min_dist == float('inf'):
            return r, c
            
        return nearest_coords