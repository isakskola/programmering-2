import socket
import threading
import pygame
import random
import json
import sys
import math
import time

# Globala Variables
SERVER_ADDRESS = 'localhost'
SERVER_PORT = 12345
PLAYER_SIZE = 25
CANVAS_SIZE_X = 500
CANVAS_SIZE_Y = 500
MOVEMENT_SPEED = 3
SHOOT_COOLDOWN = 0.5

# Klass för den lokala spelaren
class Player:
    def __init__(self):
        self.color = self.random_color()
        self.position = [random.randint(0, CANVAS_SIZE_X - PLAYER_SIZE), 
                         random.randint(0, CANVAS_SIZE_Y - PLAYER_SIZE)]
        self.rotation = 0
        self.keys_pressed = {"up": False, "down": False, "left": False, "right": False}
        self.last_shot = time.time()
        self.projectiles = []
        self.last_position = self.position.copy()
        self.score = 0
        self.hit_cooldown = 0

    # Slumpar en färg för spelaren
    def random_color(self):
        return "#{:06x}".format(random.randint(0, 0xFFFFFF))

    # Uppdaterar spelarens position, rotation och projektiler samt returnerar om tillståndet har ändrats
    def update_movement(self, mouse_pos):
        moved = False
        
        mouse_x, mouse_y = mouse_pos
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
        
        self.update_projectiles()
        
        state_changed = ((moved and (abs(self.last_position[0] - self.position[0]) > 1 or 
                        abs(self.last_position[1] - self.position[1]) > 1)) or 
                        rotation_changed or self.projectiles)
        
        if state_changed:
            self.last_position = self.position.copy()

        return state_changed
    
    # Uppdaterar spelarens skott
    def update_projectiles(self):
        for proj in self.projectiles[:]:
            proj['position'][0] += proj['velocity'][0]
            proj['position'][1] += proj['velocity'][1]
            
            if (proj['position'][0] < 0 or proj['position'][0] > CANVAS_SIZE_X or
                proj['position'][1] < 0 or proj['position'][1] > CANVAS_SIZE_Y):
                self.projectiles.remove(proj)
    
    # Skapar ett nytt skott
    def shoot(self):
        if time.time() - self.last_shot < SHOOT_COOLDOWN:
            return False
        
        center = (self.position[0] + PLAYER_SIZE/2, self.position[1] + PLAYER_SIZE/2)
        x, y = center
        barrel_offset = PLAYER_SIZE
        x += barrel_offset * math.cos(self.rotation)
        y += barrel_offset * math.sin(self.rotation)
        
        projectile = {
            'position': [x, y],
            'velocity': [math.cos(self.rotation) * 5, math.sin(self.rotation) * 5],
            'size': PLAYER_SIZE / 4
        }
        self.projectiles.append(projectile)
        self.last_shot = time.time()
        return True
    
    # Kollar om spelaren har kolliderat med något skott
    def collision_detection(self, projectiles):
        player_radius = PLAYER_SIZE / 2
        player_center = (self.position[0] + player_radius, self.position[1] + player_radius)
        
        for proj in projectiles:
            proj_pos = proj['position']
            proj_radius = proj['size'] / 2
            distance = math.sqrt((proj_pos[0] - player_center[0]) ** 2 + (proj_pos[1] - player_center[1]) ** 2)
            
            if distance < player_radius + proj_radius:
                return True
        return False
    
    # Returnerar spelarens data
    def get_data(self):
        return {
            'color': self.color,
            'position': self.position,
            'rotation': self.rotation,
            'projectiles': self.projectiles,
            'score': self.score
        }


class Canvas:
    def __init__(self):
        pygame.init()
        pygame.display.set_caption("Socket Spel Klient")
        self.screen = pygame.display.set_mode((CANVAS_SIZE_X, CANVAS_SIZE_Y))
        self.clock = pygame.time.Clock()
        self.font = pygame.font.SysFont('Arial', 16)
    
    # Konverterar hexadecimalfärg till RGB
    def hex_to_rgb(self, hex_color):
        hex_color = hex_color.lstrip('#')
        return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))
    
    # Ritar en spelare
    def draw_player(self, color, center, size, rotation):
        color_rgb = self.hex_to_rgb(color) if isinstance(color, str) else color
        x, y = center
        
        pygame.draw.circle(self.screen, color_rgb, (int(x), int(y)), int(size/2))
        
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
        
        pygame.draw.polygon(self.screen, color_rgb, [front_left, front_right, back_right, back_left])

    # Ritar ett skott
    def draw_projectile(self, position, size, color):
        color_rgb = self.hex_to_rgb(color) if isinstance(color, str) else color
        pygame.draw.circle(self.screen, color_rgb, (int(position[0]), int(position[1])), int(size))

    # Ritar allt på spelplanen
    def render(self, player, other_clients, other_projectiles):
        self.screen.fill((255, 255, 255))

        # Lokala spelaren
        self.draw_player(
            player.color,
            (player.position[0] + PLAYER_SIZE/2, player.position[1] + PLAYER_SIZE/2),
            PLAYER_SIZE,
            player.rotation
        )

        for proj in player.projectiles:
            self.draw_projectile(proj['position'], proj['size'], player.color)

        # Andra spelare
        for color, data in other_clients.items():
            position = data['position']
            rotation = data['rotation']
            self.draw_player(
                color,
                (position[0] + PLAYER_SIZE/2, position[1] + PLAYER_SIZE/2),
                PLAYER_SIZE,
                rotation
            )
        
        for proj in other_projectiles:
            self.draw_projectile(proj['position'], proj['size'], proj['color'])
        
        self.draw_leaderboard(player, other_clients)
        
        pygame.display.flip()
    
    # Ritar leaderboard
    def draw_leaderboard(self, player, other_clients):
        leaderboard = [(player.color, player.score)]
        for color, data in other_clients.items():
            if 'score' in data:
                leaderboard.append((color, data['score']))
        
        leaderboard.sort(key=lambda x: x[1], reverse=True)
        
        pygame.draw.rect(self.screen, (240, 240, 240), (10, 10, 150, 30 + 20 * len(leaderboard)))
        pygame.draw.rect(self.screen, (200, 200, 200), (10, 10, 150, 30 + 20 * len(leaderboard)), 2)
        
        title = self.font.render("Leaderboard", True, (0, 0, 0))
        self.screen.blit(title, (15, 15))
        
        for i, (color, score) in enumerate(leaderboard):
            color_rgb = self.hex_to_rgb(color) if isinstance(color, str) else color
            pygame.draw.rect(self.screen, color_rgb, (15, 40 + i * 20, 15, 15))
            
            text_color = (0, 0, 0)
            if color == player.color:
                text_color = (0, 100, 0)
                
            score_text = self.font.render(f": {score} pts", True, text_color)
            self.screen.blit(score_text, (35, 40 + i * 20))
    
    def tick(self, fps):
        return self.clock.tick(fps)

# Klass för klienten
class Client:
    def __init__(self):
        self.player = Player()
        self.canvas = Canvas()
        self.other_clients = {}
        self.other_projectiles = []
        self.running = True
        self.hit_players = set()
        
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.connect((SERVER_ADDRESS, SERVER_PORT))
        
        self.send_updates()
        
        threading.Thread(target=self.receive_updates, daemon=True).start()

    # Hanterar händelser tangentbordstryck och quit
    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
                self.socket.close()
                pygame.quit()
                sys.exit()

            elif event.type == pygame.KEYDOWN:
                if event.key in (pygame.K_UP, pygame.K_w):
                    self.player.keys_pressed["up"] = True
                elif event.key in (pygame.K_DOWN, pygame.K_s):
                    self.player.keys_pressed["down"] = True
                elif event.key == pygame.K_SPACE:
                    if self.player.shoot():
                        self.send_updates()

            elif event.type == pygame.KEYUP:
                if event.key in (pygame.K_UP, pygame.K_w):
                    self.player.keys_pressed["up"] = False
                elif event.key in (pygame.K_DOWN, pygame.K_s):
                    self.player.keys_pressed["down"] = False

    # Skickar uppdateringar till servern
    def send_updates(self):
        try:
            player_data = self.player.get_data()
            self.socket.sendall(json.dumps(player_data).encode('utf-8'))
        except Exception as e:
            print(f"Kunde inte skicka spelardata: {e}")
            self.running = False

    # Tar emot uppdateringar från servern
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

    # Uppdaterar de andra spelarna
    def update_other_clients(self, data):
        self.other_clients = {}
        self.other_projectiles = []
        
        for client in data:
            client_color = client['color']
            if client_color != self.player.color:
                position = client['position']
                rotation = client.get('rotation', 0)
                score = client.get('score', 0)
                self.other_clients[client_color] = {
                    'position': position, 
                    'rotation': rotation,
                    'score': score
                }
                
                if 'projectiles' in client:
                    for proj in client['projectiles']:
                        proj['color'] = client_color
                        self.other_projectiles.append(proj)

    # Uppdaterar spelaren och hanterar kollisioner med skott
    def update(self):
        state_changed = self.player.update_movement(pygame.mouse.get_pos())
        
        for client_color, client_data in self.other_clients.items():
            client_pos = client_data['position']
            client_center = (client_pos[0] + PLAYER_SIZE/2, client_pos[1] + PLAYER_SIZE/2)
            
            for proj in self.player.projectiles[:]:
                proj_pos = proj['position']
                proj_radius = proj['size'] / 2
                distance = math.sqrt((proj_pos[0] - client_center[0])**2 + (proj_pos[1] - client_center[1])**2)
                
                if distance < (PLAYER_SIZE/2 + proj_radius):
                    self.player.score += 1
                    self.player.projectiles.remove(proj)
                    state_changed = True
                    break
            
        if state_changed:
            self.send_updates()

    # Main loopen
    def run(self):
        while self.running:
            self.handle_events()
            self.update()
            self.canvas.render(self.player, self.other_clients, self.other_projectiles)
            self.canvas.tick(60)


if __name__ == "__main__":
    client = Client()
    client.run()