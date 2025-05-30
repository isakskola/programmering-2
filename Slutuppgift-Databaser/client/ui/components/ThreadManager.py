import tkinter as tk
from tkinter import ttk
import requests
from ui.components.BaseComponent import BaseComponent

# Klass för skärmen som visas när man skapar en tråd, ärver från BaseComponent som är en grundklass för komponenter
class CreateThreadOverlay(BaseComponent):
    def __init__(self, parent, user_id):
        self.user_id = user_id
        super().__init__(parent)
    
    def setup_ui(self):
        self.overlay = tk.Frame(self.parent, bg='gray')
        self.overlay.place(relx=0, rely=0, relwidth=1, relheight=1)
        
        self.dialog_frame = tk.Frame(self.overlay, bg='white', width=400, height=200)
        self.dialog_frame.place(relx=0.5, rely=0.5, anchor='center')

        title_label = tk.Label(self.dialog_frame, text="Skapa tråd", font=('Helvetica', 16, 'bold'), bg='white')
        title_label.pack(pady=10)

        title_entry_label = tk.Label(self.dialog_frame, text="Titel:", font=('Helvetica', 12), bg='white')
        title_entry_label.pack(pady=5)

        self.title_entry = tk.Entry(self.dialog_frame, width=40)
        self.title_entry.pack(pady=5)

        button_frame = tk.Frame(self.dialog_frame, bg='white')
        button_frame.pack(pady=20)

        create_button = tk.Button(button_frame, text="Skapa", command=self.create_thread, bg='#4CAF50', fg='white', width=15)
        create_button.pack(side=tk.LEFT, padx=5)
        
        cancel_button = tk.Button(button_frame, text="Avbryt", command=self.close, bg='#f44336', fg='white', width=15)
        cancel_button.pack(side=tk.LEFT, padx=5)
    
    def create_thread(self):
        title = self.title_entry.get().strip()
        if not title:
            self.parent.show_dialog("Fel", "Titel krävs")
            return

        try:
            response = requests.post('http://localhost:5000/api/threads', json={'title': title, 'user_id': self.user_id})
            if response.status_code == 200:
                self.close()
                self.parent.show_dialog("Info", "Tråd skapad!")
            else:
                response_data = response.json()
                self.parent.show_dialog("Fel", response_data.get('message', 'Ett fel uppstod'))
        except Exception as e:
            self.parent.show_dialog("Fel", f"Ett fel uppstod: {str(e)}")
    
    def close(self):
        self.overlay.destroy()

# Klass för att hantera trådar, ärver från BaseComponent som är en grundklass för komponenter
class ThreadManager(BaseComponent):
    def __init__(self, parent, current_user, ws_manager, on_open_thread):
        self.current_user = current_user
        self.threads = []
        self.ws_manager = ws_manager
        self.on_open_thread = on_open_thread
        super().__init__(parent)
        
        self.load_threads() # Kallar på load_threads för att ladda trådarna när direkt komponenten skapas
    
    # Skapar layouten för trådkomponenten
    def setup_ui(self):
        self.container = tk.Frame(self, bg='#f0f0f0')
        self.container.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        content_header_frame = tk.Frame(self.container, bg='#f0f0f0')
        content_header_frame.pack(fill=tk.X, padx=5, pady=5)

        # Skapar en frame för att hålla i canvasen och scrollbaren
        self.scroll_container = tk.Frame(self.container, bg='#f0f0f0')
        self.scroll_container.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Skapar en canvas med scrollbar
        self.canvas = tk.Canvas(self.scroll_container, bg='#f0f0f0', highlightthickness=0)
        self.scrollbar = ttk.Scrollbar(self.scroll_container, orient="vertical", command=self.canvas.yview)
        
        # Skapar en frame för att hålla i trådarna i canvasen
        self.content_threads_frame = tk.Frame(self.canvas, bg='#f0f0f0')
        
        # Konfigurerar canvasen för att scrolla
        self.canvas.configure(yscrollcommand=self.scrollbar.set)
        
        # Packar scrollbaren och canvasen
        self.scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        # Skapar ett fönster i canvasen för att hålla i trådarna
        self.canvas_frame = self.canvas.create_window((0, 0), window=self.content_threads_frame, anchor="nw", width=self.canvas.winfo_reqwidth())
        
        # Konfigurerar canvasen för att expandera med fönstret
        self.content_threads_frame.bind("<Configure>", self.on_frame_configure)
        self.canvas.bind("<Configure>", self.on_canvas_configure)
        
        # Bindar skroll hjulet till scrollning
        self.canvas.bind_all("<MouseWheel>", self.on_mousewheel)

        tk.Label(content_header_frame, text="Trådar", fg='black', bg='#f0f0f0', font=('Helvetica', 20, 'bold')).pack(side=tk.LEFT)
        tk.Button(content_header_frame, text="Skapa tråd", command=self.create_thread, bg='#2196F3', fg='white').pack(side=tk.RIGHT)
    
    # Event hanterare
    def on_frame_configure(self, event=None):
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))
    
    def on_canvas_configure(self, event): # När canvasen ändrar bredd så uppdateras bredden på trådarna
        width = event.width
        self.canvas.itemconfig(self.canvas_frame, width=width)
    
    def on_mousewheel(self, event):
        self.canvas.yview_scroll(int(-1*(event.delta/120)), "units")

    # Ladda trådarna
    def load_threads(self):
        try:
            response = requests.get('http://localhost:5000/api/threads')
            response_data = response.json()
            if response.status_code == 200:
                self.threads = response_data['threads']
                self.update_threads_list()
            else:
                self.show_dialog("Fel", response_data.get('message', 'Kunde inte ladda trådar'))
        except Exception as e:
            self.show_dialog("Fel", f"Ett fel uppstod: {str(e)}")

    # Callback-funktioner för socket-hantering - kallas när en ny tråd skapas eller tas bort
    def handle_new_thread(self, thread):
        self.threads.append(thread) # Lägger till tråden i listan
        self.update_threads_list() # Uppdaterar trådlistan

    def handle_thread_deleted(self, thread_id):
        self.threads = [t for t in self.threads if t['id'] != thread_id] # Tar bort tråden från listan
        self.update_threads_list() # Uppdaterar trådlistan

    # Uppdatera trådlistan
    def update_threads_list(self):
        self.clear_widgets(self.content_threads_frame)
        
        # Sortera trådarna efter senast aktiv i fallande ordning
        sorted_threads = sorted(self.threads, key=lambda x: x['last_activity'], reverse=True)
        
        # Går igenom alla trådar och ritar ut dem på skärmen
        for thread in sorted_threads:
            thread_frame = tk.Frame(self.content_threads_frame, bg='white', relief=tk.RAISED, borderwidth=1)
            thread_frame.pack(fill=tk.X, padx=5, pady=5)
            
            title_label = tk.Label(thread_frame, text=thread['title'], bg='white', font=('Helvetica', 12, 'bold'))
            title_label.pack(side=tk.LEFT, padx=10, pady=5)
            
            creator_label = tk.Label(thread_frame, text=f"Skapad av: {thread['creator']}", fg='gray', bg='white')
            creator_label.pack(side=tk.LEFT, padx=10, pady=5)
            
            date_label = tk.Label(thread_frame, text=f"Senast aktiv: {thread['last_activity']}", fg='gray', bg='white')
            date_label.pack(side=tk.RIGHT, padx=10, pady=5)
            
            # "Visa" knapp för att öppna tråden
            view_button = tk.Button(thread_frame, text="Visa", command=lambda t=thread: self.open_thread_view(t), 
                                   bg='#2196F3', fg='white')
            view_button.pack(side=tk.RIGHT, padx=10, pady=5)
            
            # Om användaren är skapare av tråden eller är admin eller moderator så kan den ta bort tråden
            if (thread['creator'] == self.current_user['username']) or (self.current_user['role'] == 'admin') or (self.current_user['role'] == 'moderator'):
                delete_button = tk.Button(thread_frame, text="Ta bort", command=lambda t=thread: self.delete_thread(t), bg='#f44336', fg='white')
                delete_button.pack(side=tk.RIGHT, padx=10, pady=5)
    
    # Skapa en tråd
    def create_thread(self):
        CreateThreadOverlay(self, self.current_user['id'])

    def open_thread_view(self, thread):
        if self.on_open_thread:
            self.on_open_thread(thread['id'], thread['title'])
    
    # Ta bort en tråd
    def delete_thread(self, thread):
        try:
            response = requests.delete(f'http://localhost:5000/api/threads/{thread["id"]}', json={'user_id': self.current_user['id'], 'role': self.current_user['role']})
            if response.status_code == 200:
                self.show_dialog("Info", "Tråd borttagen!")
            else:
                response_data = response.json()
                self.show_dialog("Fel", response_data.get('message', 'Ett fel uppstod'))
        except Exception as e:
            self.show_dialog("Fel", f"Ett fel uppstod: {str(e)}") 