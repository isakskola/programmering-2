import pygame
import random

pygame.init()

# Konstanter
GAMEWIDTH, GAMEHEIGHT = 1280, 700
WHITE = (255, 255, 255)
RED = (171, 58, 66)
LIGHTRED = (173, 71, 78)
REDFIRE = [(250, 192, 0), (255, 117, 0), (252, 100, 0), (215, 53, 2), (182, 34, 3), (128, 17, 0)]
BLUEFIRE = [(48, 154, 241), (102, 190, 249), (183, 232, 235), (156, 222, 235), (17, 101, 193), (4, 63, 152)]

# Skapa fönster och font
window = pygame.display.set_mode((GAMEWIDTH, GAMEHEIGHT))
pygame.display.set_caption("Pong")
font = pygame.font.Font(r'GrafiskaGränssnitt\Font\slkscre.ttf', 74)

class Paddle:
    def __init__(self, x, y, color):
        self.x = x
        self.y = y
        self.width = 20
        self.height = 100
        self.vy = 0
        self.color = color

    def update(self):
        self.y += self.vy
        # Håller Paddle inom spel ramarna
        if self.y < 0:
            self.y = 0
        elif self.y + self.height > GAMEHEIGHT:
            self.y = GAMEHEIGHT - self.height

    def draw(self, surface):
        self.update()
        pygame.draw.rect(surface, self.color, (self.x, self.y, self.width, self.height))

class Ball:
    def __init__(self, x, y, velX, velY):
        self.x = x
        self.y = y
        self.radius = 10
        self.vx = velX
        self.vy = velY
        self.color = WHITE
        self.trail_positions = []

    def update(self, paddles):
        self.x += self.vx
        self.y += self.vy
        # Kollision med topp och botten
        if self.y - self.radius <= 0 or self.y + self.radius >= GAMEHEIGHT:
            self.vy = -self.vy
        self.collision_check(paddles)

    def draw(self, surface, paddles):
        self.update(paddles)
        self.trail()
        pygame.draw.circle(surface, self.color, (self.x, self.y), self.radius)

    def reset(self):
        self.x = GAMEWIDTH // 2
        self.y = GAMEHEIGHT // 2
        self.vx = random.choice([-8, 8])
        self.vy = random.choice([-8, 8])
        self.trail_positions.clear()

    def trail(self):
        self.trail_positions.append((self.x, self.y))
        if len(self.trail_positions) > 5:
            self.trail_positions.pop(0)

        for i, pos in enumerate(self.trail_positions):
            alpha = int(128 * (i + 1) / len(self.trail_positions))
            trail_color = (*WHITE, alpha)
            trail_surface = pygame.Surface((self.radius * 2, self.radius * 2), pygame.SRCALPHA)
            pygame.draw.circle(trail_surface, trail_color, (self.radius, self.radius), self.radius)
            window.blit(trail_surface, (pos[0] - self.radius, pos[1] - self.radius))

    def collision_check(self, paddles):
        # Kollision med paddles
        if (paddles[0].x < self.x - self.radius < paddles[0].x + paddles[0].width and
            paddles[0].y < self.y < paddles[0].y + paddles[0].height):
            self.vx = -self.vx
            self.x = paddles[0].x + paddles[0].width + self.radius

        if (paddles[1].x < self.x + self.radius < paddles[1].x + paddles[1].width and
            paddles[1].y < self.y < paddles[1].y + paddles[1].height):
            self.vx = -self.vx
            self.x = paddles[1].x - self.radius

class Particle:
    def __init__(self, x, y, velX, velY, radius, color):
        self.x = x
        self.y = y
        self.radius = radius
        self.vx = velX
        self.vy = velY
        self.color = color

    def update(self):
        self.x += self.vx
        self.y += self.vy
        if self.radius > 0.1: # Minskar partiklarnas radius varje frame
            self.radius -= 0.2

    def draw(self, surface):
        self.update()
        if self.radius > 0.1: # Ritar endast partiklar som har en radius > 0.1
            pygame.draw.circle(surface, self.color, (self.x, self.y), int(self.radius))

class Explosion:
    def __init__(self, x, y, color):
        self.x = x
        self.y = y
        self.color = color
        self.particles = []
        self.create()

    def create(self): # Skapar alla partikel object i en explosion
        for i in range(75):
            if self.color == 'red':
                self.particles.append(Particle(self.x, self.y, random.randint(1, 7), random.randint(-8, 8), random.randint(3, 6), random.choice(REDFIRE)))
            elif self.color == 'blue':
                self.particles.append(Particle(self.x, self.y, random.randint(-7, -1), random.randint(-8, 8), random.randint(3, 6), random.choice(BLUEFIRE)))
            elif self.color == 'bottom':
                self.particles.append(Particle(self.x, self.y, random.randint(-5, 5), random.randint(-4, -1), random.randint(2, 4), WHITE))
            elif self.color == 'top':
                self.particles.append(Particle(self.x, self.y, random.randint(-5, 5), random.randint(1, 4), random.randint(2, 4), WHITE))

    def update(self):
        # Tömmer listan på partiklar som är mindre än radius = 0.1
        self.particles = [p for p in self.particles if p.radius > 0.1]

    def draw(self, surface):
        self.update()
        for particle in self.particles:
            particle.draw(surface)

def main():
    clock = pygame.time.Clock()

    # Skapar alla objekt för att spelet ska kunna köras
    ball = Ball(GAMEWIDTH // 2, GAMEHEIGHT // 2, random.choice([-8, 8]), random.choice([-8, 8]))
    paddle1 = Paddle(30, GAMEHEIGHT // 2 - 50, (68,126,190))
    paddle2 = Paddle(GAMEWIDTH - 50, GAMEHEIGHT // 2 - 50, (211,71,62))

    score1 = 0
    score2 = 0
    explosions = []

    # Spel loopen
    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        # Hanterar tangent-tryck för att kunna flytta sin Paddle
        keys = pygame.key.get_pressed()
        paddle1.vy = -8 if keys[pygame.K_w] else 8 if keys[pygame.K_s] else 0
        paddle2.vy = -8 if keys[pygame.K_UP] else 8 if keys[pygame.K_DOWN] else 0

        # Kollision check och logik för "mål"
        if ball.x - ball.radius <= 0:
            explosions.append(Explosion(ball.x - ball.radius, ball.y, 'red'))
            score2 += 1
            ball.reset()
        elif ball.x + ball.radius >= GAMEWIDTH:
            explosions.append(Explosion(ball.x + ball.radius, ball.y, 'blue'))
            score1 += 1
            ball.reset()

        window.fill((40, 40, 41))

        # Explosion effekten för toppen och botten av spel ramarna
        if ball.y + ball.radius >= GAMEHEIGHT:
            explosions.append(Explosion(ball.x, ball.y + ball.radius, 'bottom'))
        elif ball.y - ball.radius <= 0:
            explosions.append(Explosion(ball.x, ball.y - ball.radius, 'top'))

        # Kör objekt.draw som uppdaterar och ritar alla objekt för framen
        for explosion in explosions:
            explosion.draw(window)
        ball.draw(window, [paddle1, paddle2])
        paddle1.draw(window)
        paddle2.draw(window)

        # Tar bort de explosioner som inte har några partiklar kvar
        explosions = [explosion for explosion in explosions if explosion.particles]

        # Hanterar scoreboarden
        score_text1 = font.render(f"{score1}", True, (68,126,190))
        score_text2 = font.render(f"{score2}", True, (211,71,62))
        dash_text = font.render("-", True, WHITE)
        
        window.blit(score_text1, (GAMEWIDTH // 2 - score_text1.get_width() - 60, 10))
        window.blit(dash_text, (GAMEWIDTH // 2 - dash_text.get_width() // 2, 10))
        window.blit(score_text2, (GAMEWIDTH // 2 + 60, 10))

        pygame.display.flip()
        clock.tick(60)

    pygame.quit()

if __name__ == "__main__":
    main()