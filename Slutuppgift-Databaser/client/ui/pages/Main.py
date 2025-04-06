import tkinter as tk
from tkinter import ttk
from ui.components.BaseComponent import BaseComponent
from ui.components.ThreadManager import ThreadManager

# Huvudskärmen för inloggade användare på forumet, ärver från BaseComponent som är en grundklass för komponenter
class MainFrame(BaseComponent):
    def __init__(self, parent, current_user):
        self.current_user = current_user
        super().__init__(parent) # Anropar init-metoden för BaseComponent
    
    def setup_ui(self):
        main_frame = tk.Frame(self, bg='#f0f0f0')
        main_frame.pack(fill=tk.BOTH, expand=True)

        # Header_frame för att förenkla strukturen
        header_frame = tk.Frame(main_frame, bg='#f0f0f0')
        header_frame.pack(fill=tk.X, padx=10, pady=10)

        # Skapar en label för att visa användarens namn och en knapp för att logga ut
        tk.Label(header_frame, text=f"Välkommen, {self.current_user['username']}!", 
                fg='black', bg='#f0f0f0', font=('Helvetica', 12, 'bold')).pack(side=tk.LEFT)
        tk.Button(header_frame, text="Logga ut", command=self.master.logout, 
                 bg='#f44336', fg='white').pack(side=tk.RIGHT)

        # Skapar en instans av ThreadManager och packar den i main_frame
        self.thread_manager = ThreadManager(main_frame, self.current_user)
        self.thread_manager.pack(fill=tk.BOTH, expand=True, padx=10, pady=10) 