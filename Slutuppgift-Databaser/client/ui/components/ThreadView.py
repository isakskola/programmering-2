import tkinter as tk
from tkinter import ttk, scrolledtext
import requests
from ui.components.BaseComponent import BaseComponent

# Klass för att visa en tråd och dess inlägg, ärver från BaseComponent som är en grundklass för komponenter
class ThreadView(BaseComponent):
    def __init__(self, parent, current_user, thread_id, thread_title, ws_manager, on_back):
        self.current_user = current_user
        self.thread_id = thread_id
        self.thread_title = thread_title
        self.ws_manager = ws_manager
        self.on_back = on_back
        self.posts = []
        super().__init__(parent)
        self.load_posts()

    def setup_ui(self):
        self.main_frame = ttk.Frame(self, padding="10")
        self.main_frame.pack(fill=tk.BOTH, expand=True)

        # Header
        header_frame = ttk.Frame(self.main_frame)
        header_frame.pack(fill=tk.X, pady=(0, 10))

        back_button = ttk.Button(header_frame, text="< Tillbaka till trådar", command=self.on_back)
        back_button.pack(side=tk.LEFT)

        title_label = ttk.Label(header_frame, text=self.thread_title, font=('Helvetica', 16, 'bold'))
        title_label.pack(side=tk.LEFT, padx=10)

        self.posts_canvas = tk.Canvas(self.main_frame, borderwidth=0, background="#ffffff")
        self.posts_frame = ttk.Frame(self.posts_canvas)
        self.posts_scrollbar = ttk.Scrollbar(self.main_frame, orient="vertical", command=self.posts_canvas.yview)
        self.posts_canvas.configure(yscrollcommand=self.posts_scrollbar.set)

        self.posts_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.posts_canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.canvas_window = self.posts_canvas.create_window((0, 0), window=self.posts_frame, anchor="nw")

        self.posts_frame.bind("<Configure>", self.on_frame_configure)
        self.posts_canvas.bind("<Configure>", self.on_canvas_configure)
        self.posts_canvas.bind_all("<MouseWheel>", self.on_mousewheel)

        input_frame = ttk.Frame(self.main_frame, padding="5")
        input_frame.pack(fill=tk.X, pady=(10, 0))

        self.post_content_var = tk.StringVar()
        self.post_entry = ttk.Entry(input_frame, textvariable=self.post_content_var, width=80)
        self.post_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 10))
        self.post_entry.bind("<Return>", self.create_post_event)


        post_button = ttk.Button(input_frame, text="Skicka inlägg", command=self.create_post)
        post_button.pack(side=tk.LEFT)

    def on_frame_configure(self, event=None):
        self.posts_canvas.configure(scrollregion=self.posts_canvas.bbox("all"))

    def on_canvas_configure(self, event):
        self.posts_canvas.itemconfig(self.canvas_window, width=event.width)

    def on_mousewheel(self, event):
        self.posts_canvas.yview_scroll(int(-1*(event.delta/120)), "units")

    def load_posts(self):
        try:
            response = requests.get(f'http://localhost:5000/api/threads/{self.thread_id}/posts')
            if response.status_code == 200:
                self.posts = response.json().get('posts', [])
                self.render_posts()
            else:
                self.show_dialog("Fel", f"Kunde inte ladda inlägg: {response.json().get('message')}")
        except Exception as e:
            self.show_dialog("Fel", f"Anslutningsfel vid laddning av inlägg: {str(e)}")

    def render_posts(self):
        self.clear_widgets(self.posts_frame)
        for post in self.posts:
            post_item_frame = ttk.Frame(self.posts_frame, padding=5, relief="solid", borderwidth=1)
            post_item_frame.pack(fill=tk.X, pady=2, padx=2)

            header_text = f"{post['creator']} - {post['created_at']}"
            ttk.Label(post_item_frame, text=header_text, font=('Helvetica', 9, 'bold')).pack(anchor=tk.NW)
            
            content_label = ttk.Label(post_item_frame, text=post['content'], wraplength=self.posts_frame.winfo_width() - 20)
            content_label.pack(anchor=tk.NW, pady=(5,0))
        
        self.posts_canvas.update_idletasks()
        self.posts_canvas.config(scrollregion=self.posts_canvas.bbox("all"))
        self.posts_canvas.yview_moveto(1.0)

    def create_post_event(self, event):
        self.create_post()

    def create_post(self):
        content = self.post_content_var.get()
        if not content.strip():
            self.show_dialog("Fel", "Inlägget får inte vara tomt.")
            return

        try:
            response = requests.post(
                f'http://localhost:5000/api/threads/{self.thread_id}/posts',
                json={'content': content, 'user_id': self.current_user['id']}
            )
            if response.status_code == 200:
                self.post_content_var.set("")
            else:
                self.show_dialog("Fel", f"Kunde inte skapa inlägg: {response.json().get('message')}")
        except Exception as e:
            self.show_dialog("Fel", f"Anslutningsfel vid skapande av inlägg: {str(e)}")

    def handle_new_post(self, data):
        # Kontrollera om inlägget är för den aktuella tråden
        # Om det är det så lägg till inlägget i listan och rendera om
        if data.get('thread_id') == self.thread_id:
            new_post = data.get('post')
            if new_post:
                self.posts.append(new_post)
                self.render_posts()
