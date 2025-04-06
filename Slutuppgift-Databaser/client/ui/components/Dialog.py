import tkinter as tk
from tkinter import ttk

# Dialogklass för att skapa dialogrutor, ärver från Tk-klassen
class Dialog(tk.Toplevel):
    def __init__(self, parent, title, width=400, height=200):
        super().__init__(parent) # Anropar init-metoden för Tk-klassen för att kunna använda tkinters funktioner
        self.parent = parent
        self.title(title)
        self.geometry(f"{width}x{height}")
        self.resizable(False, False)
        self.setup_ui()
        self.center_window()
        
        self.transient(parent)
        self.grab_set()
        self.focus_set()
        self.attributes('-topmost', True) 
    
    # Template för att skapa dialogrutor
    def setup_ui(self):
        pass
    
    # Centrera dialogrutan över skärmen
    def center_window(self):
        self.update_idletasks()
        width = self.winfo_width()
        height = self.winfo_height()
        x = (self.winfo_screenwidth() // 2) - (width // 2)
        y = (self.winfo_screenheight() // 2) - (height // 2)
        self.geometry(f'{width}x{height}+{x}+{y}')

    # Stäng dialogrutan
    def close(self):
        self.destroy() 