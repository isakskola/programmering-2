import tkinter as tk
from tkinter import ttk, messagebox

# Grundklass för alla komponenter, ärver från ttk.Frame
class BaseComponent(ttk.Frame):
    def __init__(self, parent):
        super().__init__(parent)
        self.parent = parent
        self.setup_ui() # Anropar setup_ui vid skapandet av komponenten
    
    # Tom funktion för att den blir överskriven i subklasser för att skapa unika komponenter med samma struktur
    def setup_ui(self):
        pass
    
    # Skapa en dialogruta
    def show_dialog(self, title, message):
        dialog = tk.Toplevel(self)
        self.center_window(dialog)
        dialog.title(title)
        dialog.geometry("300x150")
        dialog.resizable(False, False)
        dialog.transient(self)
        dialog.grab_set()
        dialog.focus_set()
        dialog.attributes('-topmost', True)
        
        tk.Label(dialog, text=message, wraplength=250).pack(pady=20)
        
        tk.Button(dialog, text="OK", command=dialog.destroy).pack(pady=10)
    
    # Centrera dialogrutan över skärmen
    def center_window(self, window):
        window.update_idletasks()
        width = window.winfo_width()
        height = window.winfo_height()
        x = (window.winfo_screenwidth() // 2) - (width // 2)
        y = (window.winfo_screenheight() // 2) - (height // 2)
        window.geometry(f'{width}x{height}+{x}+{y}')
    
    # Rensa alla widgets i en container
    def clear_widgets(self, container):
        for widget in container.winfo_children():
            widget.destroy() 