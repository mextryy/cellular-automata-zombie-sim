# simulation.py
from grid import Grid, Cell
from rules import apply_infection_and_time_rules, calculate_movement
from config import GRID_W, GRID_H, CellState

def run_simulation_step(current_grid):
    """Wykonuje jeden synchroniczny krok Automatu Komórkowego (Reguły + Ruch)."""
    
    # Krok 1: Kopiowanie siatki na potrzeby obliczeń
    next_grid_states = Grid(current_grid.width, current_grid.height, 0, 0)
    for r in range(current_grid.height):
        for c in range(current_grid.width):
            original_cell = current_grid.cells[r][c]
            new_cell = Cell(original_cell.terrain_type)
            new_cell.state = original_cell.state
            new_cell.local_vars = original_cell.local_vars.copy()
            next_grid_states.cells[r][c] = new_cell

    # ETAP A: ZASTOSOWANIE REGUŁ (Infekcja, Inkubacja, Kompost)
    # Zmiany stanu są zapisywane do next_grid_states
    for r in range(current_grid.height):
        for c in range(current_grid.width):
            cell = current_grid.cells[r][c]
            
            if cell.state != CellState.GROUND:
                neighbors = current_grid.get_neighbors(r, c)
                new_state, new_local_vars = apply_infection_and_time_rules(cell, neighbors)
                
                cell_to_update = next_grid_states.cells[r][c]
                cell_to_update.state = new_state
                cell_to_update.local_vars = new_local_vars
                
                # Reguła 4 (Kompost -> Ziemia)
                if new_state == CellState.GROUND and cell.state == CellState.DEAD:
                    cell_to_update.terrain_type = CellState.GROUND
    
    # Krok 2: Przygotowanie siatki NA RUCH
    # Tworzymy czystą siatkę na nowy krok (teren się nie zmienia, agenci są w stanie GROUND)
    next_grid_final = Grid(current_grid.width, current_grid.height, 0, 0)
    for r in range(current_grid.height):
        for c in range(current_grid.width):
            # Kopiujemy teren, ale stan dynamiczny resetujemy do GROUND,
            # chyba że komórka nie rusza się (np. DEAD, INFECTED)
            cell_copy = next_grid_states.cells[r][c]
            
            new_cell = Cell(cell_copy.terrain_type)
            # Domyślnie nowa siatka jest pusta (GROUND)
            new_cell.state = CellState.GROUND 
            new_cell.local_vars = {}
            next_grid_final.cells[r][c] = new_cell
            
            # Stanów nieruchomych nie ruszamy
            if cell_copy.state not in [CellState.HUMAN, CellState.ZOMBIE]:
                 new_cell.state = cell_copy.state
                 new_cell.local_vars = cell_copy.local_vars
                 
    # ETAP B: RUCH AGENTÓW
    # Przechodzimy po siatce next_grid_states (stany po infekcji), 
    # ale ZAPISUJEMY do next_grid_final (z nowymi pozycjami)
    
    moves = {} # Zbieramy ruchy, by uniknąć kolizji
    
    for r in range(current_grid.height):
        for c in range(current_grid.width):
            cell = next_grid_states.cells[r][c]
            
            if cell.state in [CellState.HUMAN, CellState.ZOMBIE]:
                new_r, new_c = calculate_movement(next_grid_states, r, c) # Obliczenie celu
                
                # Rozwiązanie kolizji: Agenci, którzy chcą wejść na to samo pole, muszą zadecydować.
                # Na razie: jeśli pole jest już zarezerwowane, agent pozostaje w miejscu.
                if (new_r, new_c) not in moves:
                    moves[(new_r, new_c)] = cell # Przypisujemy całą komórkę do nowej pozycji
                # else: Agent zostaje, bo pole jest zajęte (nie ruszamy go)


    # Zastosowanie Ruchu do next_grid_final
    for (r, c), cell_data in moves.items():
        # Ustawiamy stan i zmienne w komórce docelowej
        next_grid_final.cells[r][c].state = cell_data.state
        next_grid_final.cells[r][c].local_vars = cell_data.local_vars
            
    return next_grid_final