import cv2
import numpy as np
from config import CellState


def load_map_from_image(image_path, target_width, target_height):
    """
    Wczytuje mapę z obrazu i konwertuje kolory na typy terenu.
    Zwraca tablicę 2D z wartościami CellState (tereny statyczne).
    """
    # Wczytaj obraz
    img = cv2.imread(image_path)
    if img is None:
        raise FileNotFoundError(f"Nie można wczytać obrazu: {image_path}")
    
    # Przeskaluj do rozmiaru siatki
    img = cv2.resize(img, (target_width, target_height), interpolation=cv2.INTER_NEAREST)
    img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    
    # Utwórz siatkę terenów
    terrain_map = np.zeros((target_height, target_width), dtype=int)
    
    # Dla każdego pixela określ typ terenu
    for i in range(target_height):
        for j in range(target_width):
            r, g, b = img_rgb[i, j]
            terrain_map[i, j] = color_to_terrain(r, g, b)
    
    return terrain_map


def color_to_terrain(r, g, b):
    """
    Mapuje kolor RGB na typ terenu (CellState).
    Dostosuj progi do kolorów na Twojej mapie!
    """
    
    # NIEBIESKI → WATER (Wisła)
    if b > 150 and r < 100 and g < 150:
        return CellState.WATER.value
    
    # CZERWONY/RÓŻOWY → BUILDING
    elif r > 150 and g < 120 and b < 120:
        return CellState.BUILDING.value
    
    # JASNA ZIELEŃ → GREEN_AREA (parki, Planty)
    elif g > 150 and r < 150 and b < 150:
        return CellState.GREEN_AREA.value
    
    # BIAŁY/JASNY SZARY → STREET (ulice)
    elif r > 180 and g > 180 and b > 180:
        return CellState.STREET.value
    
    # ŻÓŁTY/BEŻOWY → BUILDING (alternatywny kolor budynków na mapie)
    elif r > 180 and g > 140 and b < 100:
        return CellState.BUILDING.value
    
    # CIEMNY SZARY → STREET
    elif r < 100 and g < 100 and b < 100:
        return CellState.STREET.value
    
    # DOMYŚLNIE → GROUND
    else:
        return CellState.GROUND.value