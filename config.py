# config.py
from enum import Enum

# 
class CellState(Enum):
    # Stany dynamiczne 
    GROUND = 0      # wolne pole
    HUMAN = 1       # Człowiek
    INFECTED = 2    # Zarażony
    ZOMBIE = 3      # Zombie
    DEAD = 4        # Martwy 

    # Stany statyczne 
    WATER = 11
    BUILDING = 12
    GREEN_AREA = 13
    STREET = 14
    HILL = 15

# Parametry Symulacji 
GRID_W = 50
GRID_H = 50
CELL_SIZE = 8 # Rozmiar komórki w GUI 

# Reguły czasowe
INCUBATION_TIME = 5     # Kroki dla Infected - Zombie
COMPOST_TIME = 10       # Kroki dla Dead - Ground

# Reguły infekcji
INFECTION_PROBABILITY = 0.5 
ZOMBIE_INFECTION_RANGE = [1, 2] # Człowiek staje się zarażony przy 1 lub 2 sąsiadach Zombie
ZOMBIE_DEATH_THRESHOLD = 3      # Człowiek umiera przy 3 lub więcej sąsiadach Zombie

# Reguły ruchu
BASE_HUMAN_SPEED = 1 
BASE_ZOMBIE_SPEED = 1 
WIND_VECTOR = (0, 0) # Brak wiatru (r, c)
WIND_STRENGTH = 0.0

MOVEMENT_MODIFIERS = {
    CellState.GROUND.value: 1.0, 
    CellState.WATER.value: 0.1,    
    CellState.BUILDING.value: 0.2, 
    CellState.GREEN_AREA.value: 0.8, 
    CellState.STREET.value: 1.5,   
    CellState.HILL.value: 0.5      
}

#Kolory dla Wizualizacji 
COLORS = {
    CellState.HUMAN: "#00AA00",     # Ciemna zieleń
    CellState.ZOMBIE: "#AA0000",    # Ciemna czerwień
    CellState.INFECTED: "#FFA500",  # Pomarańczowy
    CellState.DEAD: "#404040",      # Ciemny szary (Martwy)
    CellState.GROUND: "#734F20",    # Brązowy (Ziemia)
    CellState.WATER: "#0000FF",     # Niebieski
    CellState.BUILDING: "#909090",  # Jasny szary (Budynek)
    CellState.GREEN_AREA: "#00FF00",# Jasna zieleń (Teren zielony)
    CellState.STREET: "#101010",    # Czarny (Ulica)
    CellState.HILL: "#663300"       # Kasztanowy (Wzniesienie)
}