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

font = pygame.font.Font('GrafiskaGränssnitt\Font\slkscre.ttf', 74)

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
        if self.y < 0:
            self.y = 0
        if self.y + self.height > height:
            self.y = height - self.height

    def draw(self, surface):
        self.update()
        pygame.draw.rect(surface, self.c, (self.x, self.y, self.width, self.height))

class Ball:
    def __init__(self, x, y, velX, velY, r=10, color=RED):
        self.x = x
        self.y = y
        self.r = r
        self.vx = velX
        self.vy = velY
        self.c = color

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

class Explosion:
    def __init__(self, x, y, winnerColor):
        self.x = x
        self.y = y
        self.winner = winnerColor
        self.particles = []

    def create(self):
        for i in range(10):
            if self.winner == 'red':
                self.particles.append(Ball(
                    self.x,
                    self.y,
                    random.randint(5, 1),
                    random.randint(-8, 8),
                    random.randint(1, 3),
                    random.choice(REDFIRE)))
            elif self.winner == 'blue':
                self.particles.append(Ball(
                    self.x,
                    self.y,
                    random.randint(-5, -1),
                    random.randint(-8, 8),
                    random.randint(1, 3),
                    random.choice(BLUEFIRE)))

    def draw(self, surface):
        for particle in self.particles:
            particle.draw(surface)


def main():
    clock = pygame.time.Clock()
    ball = Ball(width // 2, height // 2, random.choice([-8, 8]), random.choice([-8, 8]))
    paddle1 = Paddle(30, height // 2 - 50, (68,126,190))
    paddle2 = Paddle(width - 50, height // 2 - 50, (211,71,62))

    score1 = 0
    score2 = 0

    trailPositions = []
    explosion = []

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

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

        if (paddle1.x < ball.x - ball.r < paddle1.x + paddle1.width and
            paddle1.y < ball.y < paddle1.y + paddle1.height):
            ball.vx = -ball.vx
            ball.x = paddle1.x + paddle1.width + ball.r

        if (paddle2.x < ball.x + ball.r < paddle2.x + paddle2.width and
            paddle2.y < ball.y < paddle2.y + paddle2.height):
            ball.vx = -ball.vx
            ball.x = paddle2.x - ball.r

        if ball.x - ball.r <= 0:
            explosion.append([Explosion(ball.x, ball.y, 'red'), score1 + score2])
            explosion[-1].create()
            score2 += 1
            ball.reset()
            trailPositions.clear()
        elif ball.x + ball.r >= width:
            explosion.append([Explosion(ball.x, ball.y, 'blue'), score1 + score2])
            explosion[-1].create()
            score1 += 1
            ball.reset()
            trailPositions.clear()

        window.fill((40, 40, 41))

        trailPositions.append((ball.x, ball.y))
        if len(trailPositions) > 10:
            trailPositions.pop(0)

        for i, pos in enumerate(trailPositions):
            alpha = int(255 * (i + 1) / len(trailPositions))
            trail_color = (*LIGHTRED, alpha)
            trail_surface = pygame.Surface((ball.r * 2, ball.r * 2), pygame.SRCALPHA)
            pygame.draw.circle(trail_surface, trail_color, (ball.r, ball.r), ball.r)
            window.blit(trail_surface, (pos[0] - ball.r, pos[1] - ball.r))

        for expl in explosion:
            expl[0].draw(window)
        ball.draw(window)
        paddle1.draw(window)
        paddle2.draw(window)

        score_text = font.render(f"{score1} - {score2}", True, WHITE)
        window.blit(score_text, (width // 2 - score_text.get_width() // 2, 10))

        pygame.display.flip()
        clock.tick(60)

    pygame.quit()

if __name__ == "__main__":
    main()