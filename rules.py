# rules.py
import random
from config import (CellState, INCUBATION_TIME, COMPOST_TIME, INFECTION_PROBABILITY, 
                    ZOMBIE_INFECTION_RANGE, ZOMBIE_DEATH_THRESHOLD)
from config import BASE_HUMAN_SPEED, BASE_ZOMBIE_SPEED, MOVEMENT_MODIFIERS, WIND_VECTOR, WIND_STRENGTH
def apply_infection_and_time_rules(current_cell, neighbors):
    """
    Oblicza nowy stan dla komórki na podstawie stanu własnego i sąsiadów
    (reguły infekcji, śmierci, inkubacji i kompostowania).
    """
    new_state = current_cell.state
    new_local_vars = current_cell.local_vars.copy()
    
    # 1. Liczenie sąsiadów Zombie
    zombie_neighbors_count = sum(1 for cell in neighbors if cell.state == CellState.ZOMBIE)

    # --- Reguły dla CZŁOWIEKA (HUMAN) ---
    if current_cell.state == CellState.HUMAN:
        
        # Reguła 2: Człowiek staje się martwy (3 lub więcej sąsiadów Zombie)
        if zombie_neighbors_count >= ZOMBIE_DEATH_THRESHOLD:
            new_state = CellState.DEAD
            new_local_vars = {'compost_counter': 0}
            
        # Reguła 1: Człowiek staje się zarażony (1 lub 2 sąsiadów Zombie)
        elif zombie_neighbors_count in ZOMBIE_INFECTION_RANGE:
            if random.random() < INFECTION_PROBABILITY:
                new_state = CellState.INFECTED
                new_local_vars = {'incubation_counter': INCUBATION_TIME}

    # --- Reguły dla ZARAŻONEGO (INFECTED) ---
    elif current_cell.state == CellState.INFECTED:
        # Reguła 3: Po upłynięciu ustalonego czasu inkubacji
        counter = new_local_vars.get('incubation_counter', INCUBATION_TIME)
        counter -= 1
        new_local_vars['incubation_counter'] = counter
        
        if counter <= 0:
            new_state = CellState.ZOMBIE
            new_local_vars = {}

    # --- Reguły dla MARTWEGO (DEAD) ---
    elif current_cell.state == CellState.DEAD:
        # Reguła 4: Po upłynięciu kompostu
        counter = new_local_vars.get('compost_counter', 0)
        counter += 1
        new_local_vars['compost_counter'] = counter
        
        if counter >= COMPOST_TIME:
            new_state = CellState.GROUND
            # Komórka Dead musi stać się Ground TERENEM! (zmienimy to w kroku symulacji)
            new_local_vars = {}
            
    # UWAGA: Logikę ruchu dodamy później, na razie agenci nie zmieniają pozycji
    return new_state, new_local_vars

def calculate_movement(grid, r, c):
    """
    Oblicza optymalny ruch agenta (Człowiek lub Zombie) na podstawie terenu, celu i wiatru.
    Zwraca (new_r, new_c).
    """
    cell = grid.cells[r][c]
    
    if cell.state == CellState.ZOMBIE:
        base_speed = BASE_ZOMBIE_SPEED
        # Cel Zombie: Najbliższy Człowiek/Zarażony (POŚCIG)
        target_r, target_c = grid.find_nearest_agent(r, c, [CellState.HUMAN, CellState.INFECTED])
        is_fleeing = False
    elif cell.state == CellState.HUMAN:
        base_speed = BASE_HUMAN_SPEED
        # Cel Człowieka: Najbliższy Zombie (UCIECZKA)
        target_r, target_c = grid.find_nearest_agent(r, c, [CellState.ZOMBIE])
        is_fleeing = True
    else:
        return r, c # Inne stany (Martwy, Zarażony) się nie ruszają

    best_move = (r, c)
    # Dla ucieczki szukamy maksymalnego wyniku, dla pościgu minimalnego
    best_score = -float('inf') if is_fleeing else float('inf') 

    # Iterujemy przez potencjalne ruchy w oknie prędkości
    for dr in range(-base_speed, base_speed + 1):
        for dc in range(-base_speed, base_speed + 1):
            if dr == 0 and dc == 0:
                continue # Nie ruszamy się, chyba że to najlepszy wybór

            new_r, new_c = r + dr, c + dc

            # Sprawdzenie granic mapy
            if not (0 <= new_r < grid.height and 0 <= new_c < grid.width):
                continue
            
            target_cell = grid.cells[new_r][new_c]

            # Agenci nie mogą wchodzić na pola zajęte przez INNYCH agentów
            if target_cell.state != CellState.GROUND:
                continue 

            # 1. Modyfikator terenu
            modifier = MOVEMENT_MODIFIERS.get(target_cell.terrain_type.value, 1.0)
            
            # 2. Heurystyka celu (pościg vs. ucieczka)
            old_dist = abs(r - target_r) + abs(c - target_c)
            new_dist = abs(new_r - target_r) + abs(new_c - target_c)
            
            distance_change = old_dist - new_dist # > 0: zbliża, < 0: oddala

            # 3. Wpływ wiatru (tylko na Zombie)
            wind_influence = 0
            if cell.state == CellState.ZOMBIE:
                # Obliczanie zgodności wektora ruchu (dr, dc) z wektorem wiatru
                wind_influence = WIND_STRENGTH * (dr * WIND_VECTOR[0] + dc * WIND_VECTOR[1])

            # 4. Ocena ruchu (im niższy wynik, tym bliżej celu)
            score = distance_change * modifier + wind_influence
            
            if is_fleeing:
                # Ucieczka: chcemy zmaksymalizować dystans (najwyższy score)
                if score > best_score:
                    best_score = score
                    best_move = (new_r, new_c)
            else:
                # Pościg: chcemy zminimalizować dystans (najniższy score)
                if score < best_score or best_score == float('inf'): # Dodatkowe dla pierwszej iteracji
                    best_score = score
                    best_move = (new_r, new_c)
                    
    return best_move