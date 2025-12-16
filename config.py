# config.py
from enum import Enum




MAPA_TERENU_PLIK = "mapa.png" 
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
GRID_W = 120
GRID_H = 90
CELL_SIZE = 7 # Rozmiar komórki w GUI 

# Reguły czasowe
INCUBATION_TIME = 2     # Kroki dla Infected - Zombie
COMPOST_TIME = 5       # Kroki dla Dead - Ground

# Reguły infekcji
INFECTION_PROBABILITY = 0.6 
ZOMBIE_INFECTION_RANGE = [1] # Człowiek staje się zarażony przy 1 sąsiadach Zombie
ZOMBIE_DEATH_THRESHOLD = 2      # Człowiek umiera przy 2 lub więcej sąsiadach Zombie

# Reguły ruchu
BASE_HUMAN_SPEED = 1
BASE_ZOMBIE_SPEED = 1 
WIND_VECTOR = (0, 0) 
WIND_STRENGTH = 0.0
NOISE_STRENGTH = 0.3

MOVEMENT_MODIFIERS = {
    CellState.GROUND.value: 1.0, 
    CellState.WATER.value: 0.1,    
    CellState.BUILDING.value: 0.5, 
    CellState.GREEN_AREA.value: 1.2, 
    CellState.STREET.value: 2.0,   
    CellState.HILL.value: 0.5      
}

#Kolory dla Wizualizacji 
COLORS = {
    CellState.HUMAN: "#F71294",    
    CellState.ZOMBIE: "#AA0000",    
    CellState.INFECTED: "#FFA500",  
    CellState.DEAD:  "#F8EC45",      
    CellState.GROUND: "#734F20",    
    CellState.WATER: "#0000FF",     
    CellState.BUILDING: "#909090", 
    CellState.GREEN_AREA: "#00FF00",
    CellState.STREET: "#101010",    
    CellState.HILL: "#842626"
}