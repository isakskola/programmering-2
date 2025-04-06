import tkinter as tk
from tkinter import ttk, StringVar
from ui.components.BaseComponent import BaseComponent
from ui.components.ThreadManager import ThreadManager
from ui.components.WebSocketManager import WebSocketManager

# Huvudskärmen för inloggade användare på forumet, ärver från BaseComponent som är en grundklass för komponenter
class MainFrame(BaseComponent):
    def __init__(self, parent, current_user):
        self.current_user = current_user
        self.online_users_var = StringVar()
        self.online_users_var.set("")
        # Initierar WebSocketManager
        self.ws_manager = WebSocketManager(
            on_new_thread=self.handle_new_thread,
            on_thread_deleted=self.handle_thread_deleted,
            on_online_users=self.handle_online_users
        )
        self.ws_manager.connect(current_user)
        
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
        tk.Label(header_frame, text=f"Anslutna användare: ", 
                fg='black', bg='#f0f0f0', font=('Helvetica', 10)).pack(side=tk.LEFT, padx=(10, 0))
        tk.Label(header_frame, textvariable=self.online_users_var, 
                fg='green', bg='#f0f0f0', font=('Helvetica', 10, 'bold')).pack(side=tk.LEFT)
        tk.Button(header_frame, text="Logga ut", command=self.master.logout, 
                 bg='#f44336', fg='white').pack(side=tk.RIGHT)

        # Skapar en instans av ThreadManager och packar den i main_frame
        self.thread_manager = ThreadManager(main_frame, self.current_user, self.ws_manager)
        self.thread_manager.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
    
    # WebSocket event hanterare
    def handle_new_thread(self, thread):
        if hasattr(self, 'thread_manager'):
            self.thread_manager.handle_new_thread(thread)
    
    def handle_thread_deleted(self, thread_id):
        if hasattr(self, 'thread_manager'):
            self.thread_manager.handle_thread_deleted(thread_id)
    
    def handle_online_users(self, users):
        self.online_users_var.set(', '.join(users))
    
    def destroy(self):
        # Kopplar från WebSocket när skärmen stängs
        if hasattr(self, 'ws_manager'):
            self.ws_manager.disconnect()
        super().destroy() 