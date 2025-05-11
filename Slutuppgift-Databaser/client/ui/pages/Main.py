import tkinter as tk
from tkinter import ttk, StringVar
from ui.components.BaseComponent import BaseComponent
from ui.components.ThreadManager import ThreadManager
from ui.components.WebSocketManager import WebSocketManager
from ui.components.ThreadView import ThreadView

# Huvudskärmen för inloggade användare på forumet, ärver från BaseComponent som är en grundklass för komponenter
class MainFrame(BaseComponent):
    def __init__(self, parent, current_user):
        self.current_user = current_user
        self.online_users_var = StringVar()
        self.online_users_var.set("")
        self.active_thread_id = None
        self.thread_view = None

        # Initierar WebSocketManager
        self.ws_manager = WebSocketManager(
            on_new_thread=self.handle_new_thread,
            on_thread_deleted=self.handle_thread_deleted,
            on_online_users=self.handle_online_users,
            on_new_post=self.handle_new_post
        )
        self.ws_manager.connect(current_user)
        
        super().__init__(parent) # Anropar init-metoden för BaseComponent
    
    def setup_ui(self):
        self.main_container = tk.Frame(self, bg='#f0f0f0')
        self.main_container.pack(fill=tk.BOTH, expand=True)

        # Header_frame för att förenkla strukturen
        header_frame = tk.Frame(self.main_container, bg='#f0f0f0')
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

        self.content_area = tk.Frame(self.main_container, bg='#f0f0f0')
        self.content_area.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        self.show_thread_manager()
    
    def show_thread_manager(self):
        self.clear_widgets(self.content_area)
        self.active_thread_id = None
        if self.thread_view:
            self.thread_view.destroy()
            self.thread_view = None
        self.thread_manager = ThreadManager(self.content_area, self.current_user, self.ws_manager, on_open_thread=self.open_thread_view)
        self.thread_manager.pack(fill=tk.BOTH, expand=True)

    def open_thread_view(self, thread_id, thread_title):
        self.clear_widgets(self.content_area)
        self.active_thread_id = thread_id
        if self.thread_manager:
            self.thread_manager.destroy()
            self.thread_manager = None
        self.thread_view = ThreadView(self.content_area, self.current_user, thread_id, thread_title, self.ws_manager, on_back=self.show_thread_manager)
        self.thread_view.pack(fill=tk.BOTH, expand=True)

    # WebSocket event hanterare
    def handle_new_thread(self, thread):
        if hasattr(self, 'thread_manager') and self.thread_manager:
            self.thread_manager.handle_new_thread(thread)
    
    def handle_thread_deleted(self, thread_id):
        if hasattr(self, 'thread_manager') and self.thread_manager:
            self.thread_manager.handle_thread_deleted(thread_id)
    
    def handle_online_users(self, users):
        self.online_users_var.set(', '.join(users))

    def handle_new_post(self, data):
        if self.thread_view and data.get('thread_id') == self.active_thread_id:
            self.thread_view.handle_new_post(data)
        elif hasattr(self, 'thread_manager') and self.thread_manager:
            self.thread_manager.load_threads() 

    def destroy(self):
        # Kopplar från WebSocket när skärmen stängs
        if hasattr(self, 'ws_manager'):
            self.ws_manager.disconnect()
        super().destroy() 