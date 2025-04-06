import tkinter as tk
from tkinter import ttk, messagebox
from .pages.Authentication import AuthenticationFrame
from .pages.Main import MainFrame

# Huvudklassen för huvudprogrammet
class App(tk.Tk):
    def __init__(self):
        super().__init__() # Anropar init-metoden för Tk-klassen för att kunna använda tkinters funktioner
        
        self.title("Forum")
        self.geometry("1200x800")
        
        # Initierar current_user till None
        self.current_user = None
        self.setup_ui()

    # Visar inloggningsskärmen direkt när programmet startar
    def setup_ui(self):
        self.show_login()

    def show_login(self):
        # Tömmer skärmen (För att tömma skärmen när man tex loggar ut)
        for widget in self.winfo_children():
            widget.destroy()
        
        # Skapar en instans av AuthenticationFrame och packar den i huvudprogrammet och anropar on_login_success när användaren loggar in
        AuthenticationFrame(self, self.on_login_success).pack(expand=True, fill=tk.BOTH)

    # Anropar när användaren loggar in
    def on_login_success(self, user_data):
        self.current_user = user_data
        self.show_main_screen()

    # Visar huvudskärmen
    def show_main_screen(self):
        # Tömmer skärmen
        for widget in self.winfo_children():
            widget.destroy()

        # Skapar en instans av MainFrame och packar den i huvudprogrammet
        MainFrame(self, self.current_user).pack(expand=True, fill=tk.BOTH)

    # Loggar ut
    def logout(self):
        self.current_user = None
        self.show_login()
