import tkinter as tk
from tkinter import ttk
import requests
import re
from ui.components.BaseComponent import BaseComponent

class AuthenticationFrame(BaseComponent):
    def __init__(self, parent, on_login_success):
        self.on_login_success = on_login_success
        self.current_frame = None
        super().__init__(parent)
    
    def validate_username(self, username):
        if not username or len(username) < 3 or len(username) > 30:
            return False, "Användarnamnet måste vara mellan 3 och 30 tecken"
        return True, None

    def validate_password(self, password):
        if not password or len(password) < 8:
            return False, "Lösenord måste vara minst 8 tecken långt"
        return True, None

    def validate_email(self, email):
        if not email:
            return False, "Email krävs"
        email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        if not re.match(email_pattern, email):
            return False, "Ogiltigt emailformat"
        return True, None

    def setup_ui(self):
        self.container = ttk.Frame(self)
        self.container.pack(expand=True)
        self.show_login()

    def show_login(self):
        self.clear_widgets(self.container)

        title_label = ttk.Label(self.container, text="Logga in", font=('Helvetica', 16, 'bold'))
        title_label.grid(row=0, column=0, columnspan=2, pady=(0, 20))

        ttk.Label(self.container, text="Användarnamn:").grid(row=1, column=0, padx=5, pady=5)
        self.username_var = tk.StringVar()
        ttk.Entry(self.container, textvariable=self.username_var).grid(row=1, column=1, padx=5, pady=5)

        ttk.Label(self.container, text="Lösenord:").grid(row=2, column=0, padx=5, pady=5)
        self.password_var = tk.StringVar()
        ttk.Entry(self.container, textvariable=self.password_var, show="*").grid(row=2, column=1, padx=5, pady=5)

        ttk.Button(self.container, text="Logga in", command=self.login).grid(row=3, column=0, columnspan=2, pady=10)
        ttk.Button(self.container, text="Registrera dig", command=self.show_register).grid(row=4, column=0, columnspan=2)

    def show_register(self):
        self.clear_widgets(self.container)

        title_label = ttk.Label(self.container, text="Registrera dig", font=('Helvetica', 16, 'bold'))
        title_label.grid(row=0, column=0, columnspan=2, pady=(0, 20))

        ttk.Label(self.container, text="Användarnamn:").grid(row=1, column=0, padx=5, pady=5)
        self.username_var = tk.StringVar()
        ttk.Entry(self.container, textvariable=self.username_var).grid(row=1, column=1, padx=5, pady=5)

        ttk.Label(self.container, text="Email:").grid(row=2, column=0, padx=5, pady=5)
        self.email_var = tk.StringVar()
        ttk.Entry(self.container, textvariable=self.email_var).grid(row=2, column=1, padx=5, pady=5)

        ttk.Label(self.container, text="Lösenord:").grid(row=3, column=0, padx=5, pady=5)
        self.password_var = tk.StringVar()
        ttk.Entry(self.container, textvariable=self.password_var, show="*").grid(row=3, column=1, padx=5, pady=5)

        ttk.Button(self.container, text="Registrera dig", command=self.register).grid(row=4, column=0, columnspan=2, pady=10)
        ttk.Button(self.container, text="Tillbaka till inloggning", command=self.show_login).grid(row=5, column=0, columnspan=2)

    def login(self):
        username = self.username_var.get()
        password = self.password_var.get()

        try:
            response = requests.post('http://localhost:5000/api/auth/login', json={'username': username, 'password': password})
            response_data = response.json()
            if response.status_code == 200:
                self.on_login_success(response_data)
            else:
                self.show_dialog("Fel", response_data.get('message', 'Inloggning misslyckades'))
        except Exception as e:
            self.show_dialog("Fel", f"Anslutningsfel: {str(e)}")

    def register(self):
        username = self.username_var.get()
        email = self.email_var.get()
        password = self.password_var.get()

        username_valid, username_error = self.validate_username(username)
        email_valid, email_error = self.validate_email(email)
        password_valid, password_error = self.validate_password(password)
        
        if not username_valid:
            self.show_dialog("Fel", username_error)
            return
        if not email_valid:
            self.show_dialog("Fel", email_error)
            return
        if not password_valid:
            self.show_dialog("Fel", password_error)
            return

        try:
            response = requests.post('http://localhost:5000/api/auth/register', json={'username': username, 'email': email, 'password': password})
            if response.status_code == 200:
                self.show_dialog("Info", "Registrering lyckades!")
                self.show_login()
            else:
                response_data = response.json()
                self.show_dialog("Fel", response_data.get('message', 'Registrering misslyckades'))
        except Exception as e:
            self.show_dialog("Fel", f"Anslutningsfel: {str(e)}")