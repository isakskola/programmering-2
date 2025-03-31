import tkinter as tk
from tkinter import ttk, messagebox
from .pages.Authentication import AuthenticationFrame
from .pages.Main import MainFrame
class App(tk.Tk):
    def __init__(self):
        super().__init__()
        
        self.title("Forum")
        self.geometry("1200x800")
        
        self.current_user = None
        self.setup_ui()


    def setup_ui(self):
        self.show_login()

    def show_login(self):
        for widget in self.winfo_children():
            widget.destroy()
        
        AuthenticationFrame(self, self.on_login_success).pack(expand=True, fill=tk.BOTH)

    def on_login_success(self, user_data):
        self.current_user = user_data
        self.show_main_screen()

    def show_main_screen(self):
        for widget in self.winfo_children():
            widget.destroy()

        MainFrame(self, self.current_user).pack(expand=True, fill=tk.BOTH)

    def logout(self):
        self.current_user = None
        self.show_login()
