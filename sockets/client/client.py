import socket
import threading
import pygame
import random
import json
import sys
import math
import time

SERVER_ADDRESS = 'localhost'
SERVER_PORT = 12345
PLAYER_SIZE = 25
CANVAS_SIZE_X = 500
CANVAS_SIZE_Y = 500
MOVEMENT_SPEED = 3
SHOOT_COOLDOWN = 0.5

class Client:
    def __init__(self):
        pygame.init()
        pygame.display.set_caption("Socket Spel Klient")
        self.screen = pygame.display.set_mode((CANVAS_SIZE_X, CANVAS_SIZE_Y))
        self.clock = pygame.time.Clock()
        
        self.color = self.random_color()
        self.position = [random.randint(0, CANVAS_SIZE_X - PLAYER_SIZE), 
                            random.randint(0, CANVAS_SIZE_Y - PLAYER_SIZE)]
        self.rotation = 0
        self.other_clients = {}
        self.keys_pressed = {"up": False, "down": False, "left": False, "right": False}
        self.last_shot = time.time()
        self.projectiles = []
        self.other_projectiles = []
        self.running = True
        
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.connect((SERVER_ADDRESS, SERVER_PORT))
    
        self.send_updates()
        self.last_position = self.position.copy()
        self.last_rotation = self.rotation
        
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
                elif event.key == pygame.K_SPACE:
                    center = (self.position[0] + PLAYER_SIZE/2, self.position[1] + PLAYER_SIZE/2)
                    self.shoot(center, PLAYER_SIZE, self.rotation)

            elif event.type == pygame.KEYUP:
                if event.key in (pygame.K_UP, pygame.K_w):
                    self.keys_pressed["up"] = False
                elif event.key in (pygame.K_DOWN, pygame.K_s):
                    self.keys_pressed["down"] = False

    def update_movement(self):
        moved = False
        
        mouse_x, mouse_y = pygame.mouse.get_pos()
        center_x = self.position[0] + PLAYER_SIZE/2
        center_y = self.position[1] + PLAYER_SIZE/2
        dx = mouse_x - center_x
        dy = mouse_y - center_y
        new_rotation = math.atan2(dy, dx)
        rotation_changed = abs(new_rotation - self.rotation) > 0.05
        self.rotation = new_rotation
        
        forward_x = math.cos(self.rotation) * MOVEMENT_SPEED
        forward_y = math.sin(self.rotation) * MOVEMENT_SPEED
        
        velocity_x = 0
        velocity_y = 0
        
        if self.keys_pressed["up"]:
            velocity_x += forward_x
            velocity_y += forward_y
            moved = True
        if self.keys_pressed["down"]:
            velocity_x -= forward_x
            velocity_y -= forward_y
            moved = True

        new_x = self.position[0] + velocity_x
        new_y = self.position[1] + velocity_y
        
        self.position[0] = max(0, min(CANVAS_SIZE_X - PLAYER_SIZE, new_x))
        self.position[1] = max(0, min(CANVAS_SIZE_Y - PLAYER_SIZE, new_y))
        
        for proj in self.projectiles[:]:
            proj['position'][0] += proj['velocity'][0]
            proj['position'][1] += proj['velocity'][1]
            
            if (proj['position'][0] < 0 or proj['position'][0] > CANVAS_SIZE_X or
                proj['position'][1] < 0 or proj['position'][1] > CANVAS_SIZE_Y):
                self.projectiles.remove(proj)
        
        if (moved and (abs(self.last_position[0] - self.position[0]) > 1 or 
                    abs(self.last_position[1] - self.position[1]) > 1)) or rotation_changed or self.projectiles:
            self.send_updates()
            self.last_position = self.position.copy()
            self.last_rotation = self.rotation

    def send_updates(self):
        player_data = {
            'color': self.color,
            'position': self.position,
            'rotation': self.rotation,
            'projectiles': self.projectiles
        }
        try:
            self.socket.sendall(json.dumps(player_data).encode('utf-8'))
        except Exception as e:
            print(f"Kunde inte skicka spelardata: {e}")
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
        self.other_clients = {}
        self.other_projectiles = []
        
        for client in data:
            client_color = client['color']
            if client_color != self.color:
                position = client['position']
                rotation = client.get('rotation', 0)
                self.other_clients[client_color] = {'position': position, 'rotation': rotation}
                
                if 'projectiles' in client:
                    for proj in client['projectiles']:
                        proj['color'] = client_color
                        self.other_projectiles.append(proj)

    def draw_player(self, color, center, size, rotation):
        x, y = center
        
        pygame.draw.circle(self.screen, color, (int(x), int(y)), int(size/2))
        
        rect_width = (size / 3) + 0.5
        rect_length = size/2
        
        front_left = (x + (size/2 + rect_length) * math.cos(rotation) - (rect_width/2) * math.sin(rotation),
                      y + (size/2 + rect_length) * math.sin(rotation) + (rect_width/2) * math.cos(rotation))
        front_right = (x + (size/2 + rect_length) * math.cos(rotation) + (rect_width/2) * math.sin(rotation),
                       y + (size/2 + rect_length) * math.sin(rotation) - (rect_width/2) * math.cos(rotation))
        back_left = (x + (size/2 - rect_length) * math.cos(rotation) - (rect_width/2) * math.sin(rotation),
                     y + (size/2 - rect_length) * math.sin(rotation) + (rect_width/2) * math.cos(rotation))
        back_right = (x + (size/2 - rect_length) * math.cos(rotation) + (rect_width/2) * math.sin(rotation),
                      y + (size/2 - rect_length) * math.sin(rotation) - (rect_width/2) * math.cos(rotation))
        
        pygame.draw.polygon(self.screen, color, [front_left, front_right, back_right, back_left])

    def shoot(self, center, size, rotation):
        if time.time() - self.last_shot < SHOOT_COOLDOWN:
            return
        
        x, y = center
        barrel_length = size
        x += barrel_length * math.cos(rotation)
        y += barrel_length * math.sin(rotation)
        projectile = {
            'position': [x, y],
            'velocity': [math.cos(rotation) * 5, math.sin(rotation) * 5],
            'size': size / 4
        }
        self.projectiles.append(projectile)
        self.last_shot = time.time()
        self.send_updates()

    def draw_projectile(self, position, size, color):
        pygame.draw.circle(self.screen, color, (int(position[0]), int(position[1])), int(size))

    def render(self):
        self.screen.fill((255, 255, 255))

        # Rita lokala spelaren
        self.draw_player(
            self.hex_to_rgb(self.color),
            (self.position[0] + PLAYER_SIZE/2, self.position[1] + PLAYER_SIZE/2),
            PLAYER_SIZE,
            self.rotation
        )

        for proj in self.projectiles:
            self.draw_projectile(proj['position'], proj['size'], self.hex_to_rgb(self.color))


        # Rita de andra spelarna
        for color, data in self.other_clients.items():
            position = data['position']
            rotation = data['rotation']
            self.draw_player(
                self.hex_to_rgb(color),
                (position[0] + PLAYER_SIZE/2, position[1] + PLAYER_SIZE/2),
                PLAYER_SIZE,
                rotation
            )
        
        for proj in self.other_projectiles:
            self.draw_projectile(proj['position'], proj['size'], self.hex_to_rgb(proj['color']))
        
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