import pygame
import random

pygame.init()

width, height = 1280, 700
window = pygame.display.set_mode((width, height))
pygame.display.set_caption("Spel")

RED = (255, 0, 0)

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
        if self.x - self.r <= 0 or self.x + self.r >= width:
            self.vx = -self.vx
        if self.y - self.r <= 0 or self.y + self.r >= height:
            self.vy = -self.vy

    def draw(self, surface):
        pygame.draw.circle(surface, RED, (self.x, self.y), self.r)

def main():
    clock = pygame.time.Clock()
    ball = Ball(width // 2, height // 2, random.randint(4, 10), random.randint(4, 10))

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        ball.move()

        window.fill((40, 40, 40))
        ball.draw(window)
        pygame.display.flip()

        clock.tick(60)

    pygame.quit()

if __name__ == "__main__":
    main()