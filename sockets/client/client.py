import socket
import threading
import pygame
import random
import json
import sys

SERVER_ADDRESS = 'localhost'
SERVER_PORT = 12345
DOT_SIZE = 20
CANVAS_SIZE_X = 500
CANVAS_SIZE_Y = 500
MOVEMENT_SPEED = 3

class Client:
    def __init__(self):
        pygame.init()
        pygame.display.set_caption("Socket Spel Klient")
        self.screen = pygame.display.set_mode((CANVAS_SIZE_X, CANVAS_SIZE_Y))
        self.clock = pygame.time.Clock()
        
        self.dot_color = self.random_color()
        self.dot_position = [random.randint(0, CANVAS_SIZE_X - DOT_SIZE), 
                            random.randint(0, CANVAS_SIZE_Y - DOT_SIZE)]
        self.other_client_dots = {}
        self.keys_pressed = {"up": False, "down": False, "left": False, "right": False}
        self.running = True
        
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.connect((SERVER_ADDRESS, SERVER_PORT))
    
        self.send_position()
        self.last_position = self.dot_position.copy()
        
        # Ny tråd för att ta emot uppdateringar från servern samtidigt som spelet körs
        threading.Thread(target=self.receive_updates, daemon=True).start()

    def random_color(self):
        return "#{:06x}".format(random.randint(0, 0xFFFFFF))
    
    def hex_to_rgb(self, hex_color):
        hex_color = hex_color.lstrip('#')
        return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
                self.socket.close()
                pygame.quit()
                sys.exit()
            elif event.type == pygame.KEYDOWN:
                if event.key in (pygame.K_UP, pygame.K_w):
                    self.keys_pressed["up"] = True
                elif event.key in (pygame.K_DOWN, pygame.K_s):
                    self.keys_pressed["down"] = True
                elif event.key in (pygame.K_LEFT, pygame.K_a):
                    self.keys_pressed["left"] = True
                elif event.key in (pygame.K_RIGHT, pygame.K_d):
                    self.keys_pressed["right"] = True
            elif event.type == pygame.KEYUP:
                if event.key in (pygame.K_UP, pygame.K_w):
                    self.keys_pressed["up"] = False
                elif event.key in (pygame.K_DOWN, pygame.K_s):
                    self.keys_pressed["down"] = False
                elif event.key in (pygame.K_LEFT, pygame.K_a):
                    self.keys_pressed["left"] = False
                elif event.key in (pygame.K_RIGHT, pygame.K_d):
                    self.keys_pressed["right"] = False

    def update_movement(self):
        moved = False
        
        if self.keys_pressed["up"]:
            self.dot_position[1] = max(0, self.dot_position[1] - MOVEMENT_SPEED)
            moved = True
        if self.keys_pressed["down"]:
            self.dot_position[1] = min(CANVAS_SIZE_Y - DOT_SIZE, self.dot_position[1] + MOVEMENT_SPEED)
            moved = True
        if self.keys_pressed["left"]:
            self.dot_position[0] = max(0, self.dot_position[0] - MOVEMENT_SPEED)
            moved = True
        if self.keys_pressed["right"]:
            self.dot_position[0] = min(CANVAS_SIZE_X - DOT_SIZE, self.dot_position[0] + MOVEMENT_SPEED)
            moved = True
            
        if moved and (abs(self.last_position[0] - self.dot_position[0]) > 1 or 
                     abs(self.last_position[1] - self.dot_position[1]) > 1):
            self.send_position()
            self.last_position = self.dot_position.copy()

    def send_position(self):
        position_data = {
            'color': self.dot_color,
            'position': self.dot_position
        }
        try:
            self.socket.sendall(json.dumps(position_data).encode('utf-8'))
        except Exception as e:
            print(f"Kunde inte skicka position: {e}")
            self.running = False

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
        self.other_client_dots = {}
        
        for client in data:
            client_color = client['color']
            if client_color != self.dot_color:
                position = client['position']
                self.other_client_dots[client_color] = position

    def render(self):
        self.screen.fill((255, 255, 255))
        
        # Rita lokala spelaren
        pygame.draw.circle(self.screen, 
                          self.hex_to_rgb(self.dot_color), 
                          (int(self.dot_position[0] + DOT_SIZE/2), 
                           int(self.dot_position[1] + DOT_SIZE/2)), 
                          DOT_SIZE//2)
        
        # Rita de andra spelarna
        for color, position in self.other_client_dots.items():
            pygame.draw.circle(self.screen,
                              self.hex_to_rgb(color),
                              (int(position[0] + DOT_SIZE/2),
                               int(position[1] + DOT_SIZE/2)),
                              DOT_SIZE//2)
        
        pygame.display.flip()

    def run(self):
        while self.running:
            self.handle_events()
            self.update_movement()
            self.render()
            self.clock.tick(60)  # 60 FPS

if __name__ == "__main__":
    client = Client()
    client.run()