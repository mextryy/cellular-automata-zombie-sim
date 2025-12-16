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

def calculate_torus_dist_1d(val1, val2, size):
    """Oblicza torusową odległość (minimum z bezpośredniej lub zawijanej)."""
    diff = abs(val1 - val2)
    return min(diff, size - diff)

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
        neighbors = []
        for dr in [-1, 0, 1]:
            for dc in [-1, 0, 1]:
                if dr == 0 and dc == 0:
                    continue
                    
                nr = r + dr
                nc = c + dc
                
                nr = nr % self.height
                nc = nc % self.width
                
                neighbors.append(self.cells[nr][nc])
        return neighbors

    def find_nearest_agent(self, r, c, target_states):
        """Znajduje najbliższego agenta o danym stanie, używając torusowej odległości Manhattan."""
        
        # SEARCH_RANGE może pozostać, jeśli chcesz zoptymalizować prędkość.
        # W przeciwnym razie usuń ograniczenie, aby szukać na całej mapie (bezpieczniej dla logiki, ale wolniej).
        SEARCH_RANGE = 20 
        
        min_dist = float('inf')
        nearest_coords = (r, c)
        
        # Przy wyszukiwaniu torusowym, start/end pętli musi być ograniczony,
        # lub po prostu przeszukujemy całą mapę, by nie komplikować pętli z modulo.
        
        # Wracamy do przeszukiwania całej mapy, aby mieć pewność, że znajdziemy cel.
        for tr in range(self.height):
            for tc in range(self.width):
                if self.cells[tr][tc].state in target_states:
                    
                    # ⚠️ KLUCZOWA ZMIANA: Torusowa odległość Manhattan
                    dist_r = calculate_torus_dist_1d(r, tr, self.height)
                    dist_c = calculate_torus_dist_1d(c, tc, self.width)
                    
                    # Odległość Torusowa Manhattan
                    dist = dist_r + dist_c
                    
                    if dist < min_dist:
                        min_dist = dist
                        nearest_coords = (tr, tc)
                        
        # Jeśli nie znaleziono celu, agent pozostaje w miejscu
        if min_dist == float('inf'):
            return r, c
            
        return nearest_coords