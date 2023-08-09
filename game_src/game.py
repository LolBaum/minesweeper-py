import pygame
import sys
import numpy as np
from itertools import product


def basic_surf(size, color):
    if isinstance(size, int):
        size = (size, size)
    surf = pygame.surface.Surface(size)
    surf.fill(color)
    return surf


MINE = basic_surf(30, (255, 0, 0))
NUMBER = basic_surf(30, (100, 100, 200))
EMPTY_FIELD = basic_surf(30, (180, 180, 180))
HIDDEN = basic_surf(30, (144, 144, 144))

NEIGBOUR_INDICES = [x for x in product((-1, 0, 1), (-1, 0, 1))]
NEIGBOUR_INDICES.remove((0, 0))

class Field:
    def __init__(self, rect: pygame.rect.Rect, value: int = 0):
        self.value = value
        self.hidden = True
        self.is_mine = False
        self.rect = rect

    def on_click(self, display: pygame.surface.Surface):
        self.hidden = False
        self.draw(display)
        print(f"clicked {self.value}")

    def draw(self, display: pygame.surface.Surface):
        pos = self.rect.topleft
        if self.hidden:
            display.blit(HIDDEN, pos)
        elif self.is_mine:
            display.blit(MINE, pos)
        elif self.value > 0:
            display.blit(NUMBER, pos)
        else:
            display.blit(EMPTY_FIELD, pos)


class Board:
    def __init__(self, shape: [int, int] = (15, 15), num_mines: int = 35, pos=(0,0)):
        self.num_mines = num_mines
        self.shape = shape
        self.padding = 3
        self.filed_size = 30
        self.image_size = (self.shape[0] * self.filed_size + (self.shape[0] - 1) * self.padding,
                           self.shape[1] * self.filed_size + (self.shape[1] - 1) * self.padding)
        self.rect = pygame.rect.Rect(pos, self.image_size)
        self.image = pygame.surface.Surface(size=self.image_size)
        self.b = self.setup()
        self.place_mines()
        self.count_mine_neighbours()
        self.has_changed = True

    def is_mine(self, x: int, y: int) -> bool:
        if x < 0 or x >= self.shape[0] or y < 0 or y >= self.shape[1]:
            return False
        else:
            return self.b[x][y].is_mine

    def setup(self):
        b = []
        for i in range(self.shape[0]):
            row = []
            for j in range(self.shape[1]):
                row.append(Field(pygame.rect.Rect(
                    (self.filed_size + self.padding) * i, (self.filed_size + self.padding) * j,
                    self.filed_size, self.filed_size)))
            b.append(row)
        return b

    def count_mine_neighbours(self):
        for i in range(self.shape[0]):
            for j in range(self.shape[1]):
                count = 0
                for n, m in NEIGBOUR_INDICES:
                    if self.is_mine(i+n, j+m):
                        count += 1
                self.b[i][j].value = count

    def place_mines(self):
        g = np.random.default_rng(seed=None)
        mines = g.choice(self.shape[0] * self.shape[1], self.num_mines, replace=False)
        # use modulo and int div to calculate row and column
        rows = [int(m/self.shape[0]) for m in mines]
        cols = [m % self.shape[1] for m in mines]
        for x, y in zip(rows, cols):
            self.b[x][y].is_mine = True

    def draw(self, display):
        for row in self.b:
            for f in row:
                f.draw(display)

    def find_index(self, x, y) -> list[int, int] | None:
        for i in range(self.shape[0]):
            for j in range(self.shape[1]):
                if self.b[i][j].rect.collidepoint(x, y):
                    return i, j

    def click_field(self, x, y, display: pygame.surface.Surface):
        idx = self.find_index(x, y)
        if idx:
            i, j = idx
            self.b[i][j].on_click(display)




if __name__ == "__main__":
    print("running python Minesweeper")
    pygame.init()
    w, h = 700, 940
    screen = pygame.display.set_mode((w, h))
    clock = pygame.time.Clock()
    selection_active = False

    board = Board()
    print("drawing Board")
    board_pos = ((w - board.image_size[0])/2, 150)
    board.draw(screen)

    print("Starting main loop")
    while True:
        pygame.display.flip()
        clock.tick(30)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                print('Shutting down the game')
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    pygame.quit()
                    sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == pygame.BUTTON_LEFT:
                    x, y = pygame.mouse.get_pos()
                    if board.rect.collidepoint(x, y):
                        print("clicked Board")
                        board.click_field(x, y, screen)

            # TODO: mouse botten down
            #if pygame.mouse.get_pressed(num_buttons=3)[0]:  # left mouse button




