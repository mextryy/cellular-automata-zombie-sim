# rules.py
import random
from config import (
    CellState,
    INCUBATION_TIME,
    COMPOST_TIME,
    INFECTION_PROBABILITY,
    ZOMBIE_INFECTION_RANGE,
    ZOMBIE_DEATH_THRESHOLD,
    BASE_HUMAN_SPEED,
    BASE_ZOMBIE_SPEED,
    MOVEMENT_MODIFIERS,
    WIND_VECTOR,
    WIND_STRENGTH,
    NOISE_STRENGTH,
)

def apply_infection_and_time_rules(current_cell, neighbors):
    """
    Oblicza nowy stan dla komorki na podstawie stanu wlasnego i sasiadow
    (reguly infekcji, smierci, inkubacji i kompostowania).
    """
    new_state = current_cell.state
    new_local_vars = current_cell.local_vars.copy()

    zombie_neighbors_count = sum(
        1 for cell in neighbors if cell.state == CellState.ZOMBIE
    )

    # --- CZLOWIEK ---
    if current_cell.state == CellState.HUMAN:

        if zombie_neighbors_count >= ZOMBIE_DEATH_THRESHOLD:
            new_state = CellState.DEAD
            new_local_vars = {"compost_counter": 0}

        elif zombie_neighbors_count in ZOMBIE_INFECTION_RANGE:
            if random.random() < INFECTION_PROBABILITY:
                new_state = CellState.INFECTED
                new_local_vars = {"incubation_counter": INCUBATION_TIME}

    # --- ZARAZONY ---
    elif current_cell.state == CellState.INFECTED:
        counter = new_local_vars.get(
            "incubation_counter", INCUBATION_TIME
        )
        counter -= 1
        new_local_vars["incubation_counter"] = counter

        if counter <= 0:
            new_state = CellState.ZOMBIE
            new_local_vars = {}

    # --- MARTWY ---
    elif current_cell.state == CellState.DEAD:
        counter = new_local_vars.get("compost_counter", 0)
        counter += 1
        new_local_vars["compost_counter"] = counter

        if counter >= COMPOST_TIME:
            new_state = CellState.GROUND
            new_local_vars = {}

    return new_state, new_local_vars


def calculate_movement(grid, r, c):
    """
    Oblicza optymalny ruch agenta (Czlowiek lub Zombie)
    na podstawie terenu, celu, wiatru i losowego szumu,
    zastosowujac warunek brzegowy typu torus.
    """
    cell = grid.cells[r][c]

    if cell.state == CellState.ZOMBIE:
        base_speed = BASE_ZOMBIE_SPEED
        target_r, target_c = grid.find_nearest_agent(
            r, c, [CellState.HUMAN, CellState.INFECTED]
        )
        is_fleeing = False

    elif cell.state == CellState.HUMAN:
        base_speed = BASE_HUMAN_SPEED
        target_r, target_c = grid.find_nearest_agent(
            r, c, [CellState.ZOMBIE]
        )
        is_fleeing = True

    else:
        return r, c

    best_move = (r, c)
    best_score = -float("inf") if is_fleeing else float("inf")

    # Zakres ruchu od -BASE_SPEED do +BASE_SPEED
    for dr in range(-base_speed, base_speed + 1):
        for dc in range(-base_speed, base_speed + 1):
            if dr == 0 and dc == 0:
                continue

            new_r, new_c = r + dr, c + dc
            
            # ⚠️ KLUCZOWA ZMIANA (1): Wprowadzenie Warunku Torusowego (Modulo)
            new_r = new_r % grid.height
            new_c = new_c % grid.width

            # ⚠️ USUNIĘTO: Sprawdzenie granic (if not (0 <= new_r...)) jest teraz zbędne
            
            target_cell = grid.cells[new_r][new_c]

            if target_cell.state != CellState.GROUND:
                continue

            modifier = MOVEMENT_MODIFIERS.get(
                target_cell.terrain_type.value, 1.0
            )

            old_dist = abs(r - target_r) + abs(c - target_c)
            new_dist = abs(new_r - target_r) + abs(new_c - target_c)

            distance_change = old_dist - new_dist

            # Unified metric: "distance from target"
            effective_distance_metric = -distance_change

            wind_influence = 0
            if cell.state == CellState.ZOMBIE:
                wind_influence = WIND_STRENGTH * (
                    dr * WIND_VECTOR[0] + dc * WIND_VECTOR[1]
                )

            # RANDOM NOISE
            noise = random.uniform(
                -NOISE_STRENGTH, NOISE_STRENGTH
            )

            score = (
                effective_distance_metric * modifier
                + wind_influence
                + noise
            )

            if is_fleeing:
                if score > best_score:
                    best_score = score
                    best_move = (new_r, new_c)
            else:
                if score < best_score:
                    best_score = score
                    best_move = (new_r, new_c)

    return best_move