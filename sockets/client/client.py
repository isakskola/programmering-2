import socket
import threading
import tkinter as tk
import random
import json

SERVER_ADDRESS = 'localhost'
SERVER_PORT = 12345
DOT_SIZE = 20
CANVAS_SIZE_X = 500
CANVAS_SIZE_Y = 500

class Client:
    def __init__(self, master):
        self.master = master
        self.master.title("Socket Spel Klient")
        self.canvas = tk.Canvas(master, width=CANVAS_SIZE_X, height=CANVAS_SIZE_Y, bg='white')
        self.canvas.pack()

        self.dot_color = self.random_color()
        self.dot_position = [random.randint(0, CANVAS_SIZE_X - DOT_SIZE), random.randint(0, CANVAS_SIZE_Y - DOT_SIZE)]
        self.dot = self.canvas.create_oval(self.dot_position[0], self.dot_position[1], 
                                            self.dot_position[0] + DOT_SIZE, 
                                            self.dot_position[1] + DOT_SIZE, 
                                            fill=self.dot_color)
        
        self.other_client_dots = {}

        self.master.bind("<KeyPress>", self.move_dot)
        self.master.protocol("WM_DELETE_WINDOW", self.on_closing)

        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.connect((SERVER_ADDRESS, SERVER_PORT))
        self.running = True

        self.send_position()

        threading.Thread(target=self.receive_updates, daemon=True).start()

    def random_color(self):
        return "#{:06x}".format(random.randint(0, 0xFFFFFF))

    def move_dot(self, event):
        if event.keysym in ('Up', 'w', 'W'):
            self.dot_position[1] -= 5
        elif event.keysym in ('Down', 's', 'S'):
            self.dot_position[1] += 5
        elif event.keysym in ('Left', 'a', 'A'):
            self.dot_position[0] -= 5
        elif event.keysym in ('Right', 'd', 'D'):
            self.dot_position[0] += 5

        self.update_dot_position()
        self.send_position()

    def update_dot_position(self):
        self.canvas.coords(self.dot, self.dot_position[0], self.dot_position[1], 
                           self.dot_position[0] + DOT_SIZE, 
                           self.dot_position[1] + DOT_SIZE)

    def send_position(self):
        position_data = {
            'color': self.dot_color,
            'position': self.dot_position
        }
        self.socket.sendall(json.dumps(position_data).encode('utf-8'))

    def receive_updates(self):
        while self.running:
            try:
                data = self.socket.recv(1024)
                if not data:
                    break
                self.update_other_clients(json.loads(data.decode('utf-8')))
            except Exception as e:
                print(f"Kunde inte hämta uppdatering: {e}")
                break

    def update_other_clients(self, data):
        seen_colors = set()
        
        for client in data:
            client_color = client['color']
            if client_color != self.dot_color:
                seen_colors.add(client_color)
                x, y = client['position'][0], client['position'][1]
                
                if client_color in self.other_client_dots:
                    self.canvas.coords(
                        self.other_client_dots[client_color],
                        x, y, x + DOT_SIZE, y + DOT_SIZE
                    )
                else:
                    self.other_client_dots[client_color] = self.canvas.create_oval(
                        x, y, x + DOT_SIZE, y + DOT_SIZE,
                        fill=client_color
                    )
        
        for color in list(self.other_client_dots.keys()):
            if color not in seen_colors:
                self.canvas.delete(self.other_client_dots[color])
                del self.other_client_dots[color]

    def on_closing(self):
        self.running = False
        self.socket.close()
        self.master.destroy()

if __name__ == "__main__":
    root = tk.Tk()
    client = Client(root)
    root.mainloop()