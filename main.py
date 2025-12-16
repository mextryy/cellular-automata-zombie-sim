# main.py
import tkinter as tk
from zombie_ca_gui import ZombieCA_GUI

if __name__ == "__main__":
    
    root = tk.Tk()
    app = ZombieCA_GUI(root)
    root.mainloop()