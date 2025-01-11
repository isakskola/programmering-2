import pygame
import random

pygame.init()

width, height = 1280, 700
window = pygame.display.set_mode((width, height))
pygame.display.set_caption("Pong")

WHITE = (255, 255, 255)
RED = (255, 0, 0)
BLUE = (0, 0, 255)

class Paddle:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.width = 20
        self.height = 100
        self.vy = 0

    def move(self):
        self.y += self.vy
        if self.y < 0:
            self.y = 0
        if self.y + self.height > height:
            self.y = height - self.height

    def draw(self, surface):
        pygame.draw.rect(surface, WHITE, (self.x, self.y, self.width, self.height))

class Ball:
    def __init__(self, x, y, velX, velY):
        self.x = x
        self.y = y
        self.r = 10
        self.vx = velX
        self.vy = velY

    def move(self):
        self.x += self.vx
        self.y += self.vy
        if self.y - self.r <= 0 or self.y + self.r >= height:
            self.vy = -self.vy

    def draw(self, surface):
        pygame.draw.circle(surface, RED, (self.x, self.y), self.r)

    def reset(self):
        self.x = width // 2
        self.y = height // 2
        self.vx = random.choice([-8, 8])
        self.vy = random.choice([-8, 8])

def main():
    clock = pygame.time.Clock()
    ball = Ball(width // 2, height // 2, random.choice([-8, 8]), random.choice([-8, 8]))
    paddle1 = Paddle(30, height // 2 - 50)
    paddle2 = Paddle(width - 50, height // 2 - 50)

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

        ball.move()
        paddle1.move()
        paddle2.move()

        if (paddle1.x < ball.x - ball.r < paddle1.x + paddle1.width and
            paddle1.y < ball.y + ball.r and ball.y - ball.r < paddle1.y + paddle1.height):
            ball.vx = -ball.vx
            ball.x = paddle1.x + paddle1.width + ball.r

        if (paddle2.x < ball.x + ball.r < paddle2.x + paddle2.width and
            paddle2.y < ball.y + ball.r and ball.y - ball.r < paddle2.y + paddle2.height):
            ball.vx = -ball.vx
            ball.x = paddle2.x - ball.r

        if ball.x - ball.r <= 0 or ball.x + ball.r >= width:
            ball.reset()

        window.fill((0, 0, 0))
        ball.draw(window)
        paddle1.draw(window)
        paddle2.draw(window)
        pygame.display.flip()

        clock.tick(60)

    pygame.quit()

if __name__ == "__main__":
    main()