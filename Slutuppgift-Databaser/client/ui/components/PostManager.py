import tkinter as tk
from tkinter import ttk, scrolledtext
import requests
from ui.components.BaseComponent import BaseComponent

class PostManager(BaseComponent):
    def __init__(self, parent, current_user, thread_data, on_back_callback):
        self.current_user = current_user
        self.thread_data = thread_data
        self.on_back_callback = on_back_callback
        self.posts = []
        super().__init__(parent)
        self.load_posts()

    def setup_ui(self):
        self.container = tk.Frame(self, bg='#e0e0e0')
        self.container.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        header_frame = tk.Frame(self.container, bg='#e0e0e0')
        header_frame.pack(fill=tk.X, pady=(0, 10))

        back_button = tk.Button(header_frame, text="< Tillbaka till trådar", command=self.on_back_callback, bg='#6c757d', fg='white')
        back_button.pack(side=tk.LEFT)

        thread_title_label = tk.Label(header_frame, text=f"Tråd: {self.thread_data['title']}", font=('Helvetica', 16, 'bold'), bg='#e0e0e0')
        thread_title_label.pack(side=tk.LEFT, padx=10)

        # Delen som visar inlägg
        self.posts_scroll_container = tk.Frame(self.container, bg='#e0e0e0')
        self.posts_scroll_container.pack(fill=tk.BOTH, expand=True, pady=(0, 10))

        self.posts_canvas = tk.Canvas(self.posts_scroll_container, bg='#f0f0f0', highlightthickness=0)
        self.posts_scrollbar = ttk.Scrollbar(self.posts_scroll_container, orient="vertical", command=self.posts_canvas.yview)
        self.posts_content_frame = tk.Frame(self.posts_canvas, bg='#f0f0f0')

        self.posts_canvas.configure(yscrollcommand=self.posts_scrollbar.set)
        self.posts_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.posts_canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.canvas_posts_frame = self.posts_canvas.create_window((0, 0), window=self.posts_content_frame, anchor="nw")

        self.posts_content_frame.bind("<Configure>", lambda e: self.posts_canvas.configure(scrollregion=self.posts_canvas.bbox("all")))
        self.posts_canvas.bind("<Configure>", lambda e: self.posts_canvas.itemconfig(self.canvas_posts_frame, width=e.width))
        
        # Bindar skrollhjulet till scrollning i posts_canvas
        self.posts_canvas.bind_all("<MouseWheel>", self._on_mousewheel_posts)


        # Nytt inläggsdel
        new_post_frame = tk.Frame(self.container, bg='#e0e0e0')
        new_post_frame.pack(fill=tk.X, pady=(5,0))

        self.post_content_entry = scrolledtext.ScrolledText(new_post_frame, height=4, font=('Helvetica', 10))
        self.post_content_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 10))

        post_button = tk.Button(new_post_frame, text="Skicka inlägg", command=self.create_post, bg='#007bff', fg='white', height=2)
        post_button.pack(side=tk.RIGHT, fill=tk.Y)

    def _on_mousewheel_posts(self, event):
        widget_under_mouse = self.winfo_containing(event.x_root, event.y_root)
        if widget_under_mouse is None:
            return
            
        ancestor = widget_under_mouse
        while ancestor is not None and ancestor != self.posts_canvas:
            ancestor = ancestor.master
        
        if ancestor == self.posts_canvas:
            self.posts_canvas.yview_scroll(int(-1*(event.delta/120)), "units")

    def load_posts(self):
        try:
            response = requests.get(f"http://localhost:5000/api/threads/{self.thread_data['id']}/posts")
            if response.status_code == 200:
                self.posts = response.json().get('posts', [])
                self.update_posts_list()
            else:
                self.show_dialog("Fel", f"Kunde inte ladda inlägg: {response.json().get('message', 'Okänt fel')}")
        except Exception as e:
            self.show_dialog("Fel", f"Ett fel uppstod vid laddning av inlägg: {str(e)}")

    def update_posts_list(self):
        self.clear_widgets(self.posts_content_frame)
        for post in self.posts:
            post_frame = tk.Frame(self.posts_content_frame, bg='white', relief=tk.RAISED, borderwidth=1)
            post_frame.pack(fill=tk.X, padx=5, pady=3)

            header_info_frame = tk.Frame(post_frame, bg='white')
            header_info_frame.pack(fill=tk.X, padx=5, pady=(5,0))

            creator_label = tk.Label(header_info_frame, text=f"{post['creator']}", font=('Helvetica', 10, 'bold'), bg='white')
            creator_label.pack(side=tk.LEFT)

            created_at_label = tk.Label(header_info_frame, text=f"{post['created_at']}", font=('Helvetica', 8, 'italic'), fg='gray', bg='white')
            created_at_label.pack(side=tk.RIGHT)
            
            self.posts_content_frame.update_idletasks()
            wrap_length = self.posts_content_frame.winfo_width() - 40 # Padding/margins
            if wrap_length < 1:
                wrap_length = 500 

            content_label = tk.Label(post_frame, text=post['content'], wraplength=wrap_length, justify=tk.LEFT, bg='white', anchor='w', font=('Helvetica', 10))
            content_label.pack(fill=tk.X, padx=10, pady=(0,10))
        
        self.posts_canvas.update_idletasks()
        self.posts_canvas.yview_moveto(1.0)


    def create_post(self):
        content = self.post_content_entry.get("1.0", tk.END).strip()
        if not content:
            self.show_dialog("Fel", "Inlägget får inte vara tomt.")
            return

        try:
            payload = {
                'content': content,
                'user_id': self.current_user['id']
            }
            response = requests.post(f"http://localhost:5000/api/threads/{self.thread_data['id']}/posts", json=payload)
            if response.status_code == 200:
                self.post_content_entry.delete("1.0", tk.END)
            else:
                self.show_dialog("Fel", f"Kunde inte skapa inlägg: {response.json().get('message', 'Okänt fel')}")
        except Exception as e:
            self.show_dialog("Fel", f"Ett fel uppstod vid skapande av inlägg: {str(e)}")

    def add_post_from_websocket(self, post_data):
        if post_data['thread_id'] == self.thread_data['id']:
            is_duplicate = any(p['id'] == post_data['id'] for p in self.posts)
            if not is_duplicate:
                self.posts.append(post_data)
                self.update_posts_list()
    
    def destroy(self):
        self.posts_canvas.unbind_all("<MouseWheel>")
        super().destroy()