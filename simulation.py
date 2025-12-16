# simulation.py
from grid import Grid, Cell
from rules import apply_infection_and_time_rules, calculate_movement
from config import GRID_W, GRID_H, CellState

def run_simulation_step(current_grid):
    """Wykonuje jeden synchroniczny krok Automatu Komorkowego (Reguly + Ruch)."""
    
    # Inicjalizacja statystyk dla tego kroku
    deaths_in_this_step = 0
    
    # Krok 1: Kopiowanie siatki na potrzeby obliczen
    next_grid_states = Grid(current_grid.width, current_grid.height, 0, 0)
    for r in range(current_grid.height):
        for c in range(current_grid.width):
            original_cell = current_grid.cells[r][c]
            new_cell = Cell(original_cell.terrain_type)
            new_cell.state = original_cell.state
            new_cell.local_vars = original_cell.local_vars.copy()
            next_grid_states.cells[r][c] = new_cell

    # ETAP A: ZASTOSOWANIE REGUL (Infekcja, Inkubacja, Kompost)
    for r in range(current_grid.height):
        for c in range(current_grid.width):
            cell = current_grid.cells[r][c]  # Stan przed regulami
            if cell.state != CellState.GROUND:
                neighbors = current_grid.get_neighbors(r, c)
                new_state, new_local_vars = apply_infection_and_time_rules(cell, neighbors)
                
                # Zliczenie zgonów
                if cell.state == CellState.HUMAN and new_state == CellState.DEAD:
                    deaths_in_this_step += 1
                
                cell_to_update = next_grid_states.cells[r][c]
                cell_to_update.state = new_state
                cell_to_update.local_vars = new_local_vars
                
                # Kompost -> Ziemia
                if new_state == CellState.GROUND and cell.state == CellState.DEAD:
                    cell_to_update.terrain_type = CellState.GROUND

    # Krok 2: Przygotowanie siatki na ruch (usuniecie agentow ruchomych)
    next_grid_final = Grid(current_grid.width, current_grid.height, 0, 0)
    for r in range(current_grid.height):
        for c in range(current_grid.width):
            cell_copy = next_grid_states.cells[r][c]
            new_cell = Cell(cell_copy.terrain_type)
            new_cell.state = cell_copy.state
            new_cell.local_vars = cell_copy.local_vars.copy()
            
            if new_cell.state in [CellState.HUMAN, CellState.ZOMBIE]:
                # Pole startowe staje się GROUND
                new_cell.state = CellState.GROUND
                new_cell.local_vars = {}
            
            next_grid_final.cells[r][c] = new_cell

    # ETAP B: RUCH AGENTOW
    moves = {}
    for r in range(current_grid.height):
        for c in range(current_grid.width):
            cell = next_grid_states.cells[r][c]
            if cell.state in [CellState.HUMAN, CellState.ZOMBIE]:
                new_r, new_c = calculate_movement(next_grid_states, r, c)
                
                # Rozwiazanie kolizji
                if (new_r, new_c) not in moves:
                    moves[(new_r, new_c)] = cell
                else:
                    if (r, c) not in moves:
                        moves[(r, c)] = cell

    # Zastosowanie ruchu
    for (r, c), cell_data in moves.items():
        next_grid_final.cells[r][c].state = cell_data.state
        next_grid_final.cells[r][c].local_vars = cell_data.local_vars
        
    return next_grid_final, deaths_in_this_step
