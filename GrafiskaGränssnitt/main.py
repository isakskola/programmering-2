import pygame
import random

pygame.init()

width, height = 1280, 700
window = pygame.display.set_mode((width, height))
pygame.display.set_caption("Pong")

WHITE = (255, 255, 255)
RED = (171, 58, 66)
LIGHTRED = (173, 71, 78)
REDFIRE = [(250, 192, 0), (255, 117, 0), (252, 100, 0), (215, 53, 2), (182, 34, 3), (128, 17, 0)]
BLUEFIRE = [(48, 154, 241), (102, 190, 249), (183, 232, 235), (156, 222, 235), (17, 101, 193), (4, 63, 152)]

font = pygame.font.Font(r'GrafiskaGränssnitt\Font\slkscre.ttf', 74)

class Paddle:
    def __init__(self, x, y, color):
        self.x = x
        self.y = y
        self.width = 20
        self.height = 100
        self.vy = 0
        self.c = color

    def update(self):
        self.y += self.vy
        if self.y < 0: # Håller Paddle inom spel ramarna
            self.y = 0
        elif self.y + self.height > height:
            self.y = height - self.height

    def draw(self, surface):
        self.update()
        pygame.draw.rect(surface, self.c, (self.x, self.y, self.width, self.height))

class Ball:
    def __init__(self, x, y, velX, velY):
        self.x = x
        self.y = y
        self.r = 10
        self.vx = velX
        self.vy = velY
        self.c = WHITE

    def update(self):
        self.x += self.vx
        self.y += self.vy
        if self.y - self.r <= 0 or self.y + self.r >= height:
            self.vy = -self.vy

    def draw(self, surface):
        self.update()
        pygame.draw.circle(surface, self.c, (self.x, self.y), self.r)

    def reset(self):
        self.x = width // 2
        self.y = height // 2
        self.vx = random.choice([-8, 8])
        self.vy = random.choice([-8, 8])

class Particle:
    def __init__(self, x, y, velX, velY, radius, color):
        self.x = x
        self.y = y
        self.r = radius
        self.vx = velX
        self.vy = velY
        self.c = color

    def update(self):
        self.x += self.vx
        self.y += self.vy
        if self.r > 0.1: # Minskar partiklarnas radius varje frame
            self.r -= 0.2

    def draw(self, surface):
        self.update()
        if self.r > 0.1: # Ritar endast partiklar som har en radius > 0.1
            pygame.draw.circle(surface, self.c, (self.x, self.y), int(self.r))

class Explosion:
    def __init__(self, x, y, color):
        self.x = x
        self.y = y
        self.c = color
        self.particles = []
        self.create()

    def create(self): # Skapar alla partikel object i en explosion
        for i in range(75):
            if self.c == 'red':
                self.particles.append(Particle(
                    self.x,
                    self.y,
                    random.randint(1, 7),
                    random.randint(-8, 8),
                    random.randint(3, 6),
                    random.choice(REDFIRE)))
            elif self.c == 'blue':
                self.particles.append(Particle(
                    self.x,
                    self.y,
                    random.randint(-7, -1),
                    random.randint(-8, 8),
                    random.randint(3, 6),
                    random.choice(BLUEFIRE)))
            elif self.c == 'bottom':
                self.particles.append(Particle(
                    self.x,
                    self.y,
                    random.randint(-5, 5),
                    random.randint(-4, -1),
                    random.randint(2, 4),
                    WHITE))
            elif self.c == 'top':
                self.particles.append(Particle(
                    self.x,
                    self.y,
                    random.randint(-5, 5),
                    random.randint(1, 4),
                    random.randint(2, 4),
                    WHITE))

    def update(self):
        self.particles = [p for p in self.particles if p.r > 0.1] # Tömmer listan på partiklar som är mindre än radius = 0.1
        
    def draw(self, surface):
        self.update()
        for particle in self.particles:
            particle.draw(surface)

def main():
    clock = pygame.time.Clock()
    # Skapar alla objekt för att spelet ska kunna köras
    ball = Ball(width // 2, height // 2, random.choice([-8, 8]), random.choice([-8, 8]))
    paddle1 = Paddle(30, height // 2 - 50, (68,126,190))
    paddle2 = Paddle(width - 50, height // 2 - 50, (211,71,62))

    # Skapar de variabler som kommer behövas under spelets gång
    score1 = 0
    score2 = 0

    trailPositions = []
    explosions = []

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        # Hanterar tangent-tryck för att kunna flytta sin Paddle
        keys = pygame.key.get_pressed()
        if keys[pygame.K_w]:
            paddle1.vy = -8
        elif keys[pygame.K_s]:
            paddle1.vy = 8
        else:
            paddle1.vy = 0

        if keys[pygame.K_UP]:
            paddle2.vy = -8
        elif keys[pygame.K_DOWN]:
            paddle2.vy = 8
        else:
            paddle2.vy = 0

        # Kollision check med bollen
        if (paddle1.x < ball.x - ball.r < paddle1.x + paddle1.width and
            paddle1.y < ball.y < paddle1.y + paddle1.height):
            ball.vx = -ball.vx
            ball.x = paddle1.x + paddle1.width + ball.r

        if (paddle2.x < ball.x + ball.r < paddle2.x + paddle2.width and
            paddle2.y < ball.y < paddle2.y + paddle2.height):
            ball.vx = -ball.vx
            ball.x = paddle2.x - ball.r

        # Kollision check för "mål"
        if ball.x - ball.r <= 0:
            explosions.append(Explosion(ball.x - ball.r, ball.y, 'red'))
            score2 += 1
            ball.reset()
            trailPositions.clear()
        elif ball.x + ball.r >= width:
            explosions.append(Explosion(ball.x + ball.r, ball.y, 'blue'))
            score1 += 1
            ball.reset()
            trailPositions.clear()

        window.fill((40, 40, 41))
         
        # Hanterar bollens trail och ser till at den bara går 5 iterationer bak
        trailPositions.append((ball.x, ball.y))
        if len(trailPositions) > 5:
            trailPositions.pop(0)

        for i, pos in enumerate(trailPositions):
            alpha = int(128 * (i + 1) / len(trailPositions))
            trail_color = (*WHITE, alpha)
            trail_surface = pygame.Surface((ball.r * 2, ball.r * 2), pygame.SRCALPHA)
            pygame.draw.circle(trail_surface, trail_color, (ball.r, ball.r), ball.r)
            window.blit(trail_surface, (pos[0] - ball.r, pos[1] - ball.r))

        # Explosion effekten för toppen och botten av spel ramarna
        if ball.y + ball.r >= height:
            explosions.append(Explosion(ball.x, ball.y + ball.r, 'bottom'))
        elif ball.y - ball.r <= 0:
            explosions.append(Explosion(ball.x, ball.y - ball.r, 'top'))

        # Kör objekt.draw som uppdaterar och ritar alla objekt för framen
        for explosion in explosions:
            explosion.draw(window)
        ball.draw(window)
        paddle1.draw(window)
        paddle2.draw(window)

        explosions = [explosion for explosion in explosions if explosion.particles] # Tar bort de explosioner som inte har några partiklar kvar

        # Hanterar scoreboarden
        score_text1 = font.render(f"{score1}", True, (68,126,190))
        score_text2 = font.render(f"{score2}", True, (211,71,62))
        dash_text = font.render("-", True, WHITE)
        
        window.blit(score_text1, (width // 2 - score_text1.get_width() - 60, 10))
        window.blit(dash_text, (width // 2 - dash_text.get_width() // 2, 10))
        window.blit(score_text2, (width // 2 + 60, 10))

        pygame.display.flip()
        clock.tick(60)

    pygame.quit()

if __name__ == "__main__":
    main()