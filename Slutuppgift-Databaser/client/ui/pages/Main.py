import tkinter as tk
from tkinter import ttk, messagebox
import requests

class MainFrame(ttk.Frame):
    def __init__(self, parent, current_user):
        super().__init__(parent)
        self.current_user = current_user
        self.setup_ui()
    
    def setup_ui(self):
        main_frame = tk.Frame(self, bg='gray')
        main_frame.pack(fill=tk.BOTH, expand=True)

        header_frame = tk.Frame(main_frame)
        header_frame.pack(fill=tk.X, padx=5, pady=5)

        tk.Label(header_frame, text=f"Välkomen, {self.current_user['username']}!", fg='black').pack(side=tk.LEFT)
        tk.Button(header_frame, text="Logga ut", command=self.master.logout(), fg='black').pack(side=tk.RIGHT)

        content_frame = tk.Frame(main_frame)
        content_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        tk.Label(content_frame, text="test", fg='black').pack()

        