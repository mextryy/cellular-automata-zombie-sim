# main.py
import tkinter as tk
from zombie_ca_gui import ZombieCA_GUI

if __name__ == "__main__":
    # Upewnij się, że masz zainstalowany NumPy: pip install numpy
    # (Choć w tej wersji nie jest jeszcze ściśle wymagany,
    # będzie potrzebny do logiki ruchu!)
    
    root = tk.Tk()
    app = ZombieCA_GUI(root)
    root.mainloop()