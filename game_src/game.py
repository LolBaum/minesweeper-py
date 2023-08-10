import pygame
import sys
import numpy as np

def basic_surf(size, color):
    if isinstance(size, int):
        size = (size, size)
    surf = pygame.surface.Surface(size)
    surf.fill(color)
    return surf



g_size = 30

def number_field(n, font):
    surf = pygame.surface.Surface((g_size, g_size))
    surf.fill((180, 180, 180))
    surf.blit(font.render(" " + str(n), True, (0, 0, 0)), pygame.rect.Rect(0,0,0,0))
    return surf


MINE = basic_surf(g_size, (255, 0, 0))
NUMBER = basic_surf(g_size, (100, 100, 200))
EMPTY_FIELD = basic_surf(g_size, (180, 180, 180))
HIDDEN = basic_surf(g_size, (144, 144, 144))

NEIGBOUR_INDICES_AXIS = [(-1, 0), (1, 0), (0, -1), (0, 1)]
NEIGBOUR_INDICES_DIAGONAL = [(-1, -1), (1, 1), (1, -1), (-1, 1)]
NEIGBOUR_INDICES = NEIGBOUR_INDICES_AXIS + NEIGBOUR_INDICES_DIAGONAL

# Todo: free connected empy fields when clicked
# todo: display Neigbour Mines number
# todo: display num Mines
# todo: add restart button
# todo: function to mark mines
# todo: display number of marked mines
# todo: check if game is won
# todo: Game Over if mine is clicked
# todo: display GAME WON
# todo: display GAME OVER


class Field:
    def __init__(self, rect: pygame.rect.Rect, value: int = 0):
        self.value = value
        self.hidden = True
        self.is_mine = False
        self.rect = rect
        self.changed = True

    def _set_hidden(self, hidden):
        self.hidden = hidden
        self.changed = True

    def on_click(self):
        self._set_hidden(False)
        print(f"freed {self.value}")

    def draw(self, display: pygame.surface.Surface):
        if not self.changed:
            return
        pos = self.rect.topleft
        if self.hidden:
            display.blit(HIDDEN, pos)
        elif self.is_mine:
            display.blit(MINE, pos)
        elif self.value > 0:
            display.blit(NUMBERS[self.value], pos)
        else:
            display.blit(EMPTY_FIELD, pos)


class Board:
    def __init__(self, shape: [int, int] = (15, 15), num_mines: int = 70, pos=(0, 0), field_size=30):
        self.num_mines = num_mines
        self.shape = shape
        self.padding = 3
        self.filed_size = field_size
        self.image_size = (self.shape[0] * self.filed_size + (self.shape[0] - 1) * self.padding,
                           self.shape[1] * self.filed_size + (self.shape[1] - 1) * self.padding)
        self.rect = pygame.rect.Rect(pos, self.image_size)
        self.image = pygame.surface.Surface(size=self.image_size)
        self.b = self.setup()
        self.place_mines()
        self.count_mine_neighbours()
        self.changed = True

    def is_mine(self, x: int, y: int) -> bool:
        if x < 0 or x >= self.shape[0] or y < 0 or y >= self.shape[1]:
            return False
        else:
            return self.b[x][y].is_mine

    def has_neighbour_mines(self, x: int, y: int) -> bool:
        if x < 0 or x >= self.shape[0] or y < 0 or y >= self.shape[1]:
            return False
        else:
            return self.b[x][y].value > 0

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
        if self.changed:
            for row in self.b:
                for f in row:
                    f.draw(display)
            self.changed = False

    def find_index(self, x, y) -> list[int, int] | None:
        for i in range(self.shape[0]):
            for j in range(self.shape[1]):
                if self.b[i][j].rect.collidepoint(x, y):
                    return i, j

    def click_field(self, x, y):
        idx = self.find_index(x, y)
        if idx:
            i, j = idx
            self.b[i][j].on_click()
            self.discover(i, j)
            self.changed = True

    def discover(self, i, j, disc=True):
        if self.has_neighbour_mines(i, j):
            self.b[i][j].on_click()
        else:
            if disc:
                self.b[i][j].on_click()
                for n, m in NEIGBOUR_INDICES_AXIS:
                    x = n+i
                    y = m+j
                    if self.shape[0] > x >= 0 and self.shape[1] > y >= 0 and self.b[x][y].hidden:
                        self.discover(x, y, disc=True)
                for n, m in NEIGBOUR_INDICES_DIAGONAL:
                    x = n+i
                    y = m+j
                    if self.shape[0] > x >= 0 and self.shape[1] > y >= 0 and self.b[x][y].hidden:
                        self.discover(x, y, disc=False)





if __name__ == "__main__":
    print("running python Minesweeper")
    pygame.init()
    pygame.font.init()
    w, h = 940, 940
    screen = pygame.display.set_mode((w, h))
    clock = pygame.time.Clock()
    font = pygame.font.Font( size=30)
    NUMBERS = [number_field(x, font) for x in range(9)]

    selection_active = False

    board = Board(shape=(20, 20), field_size=g_size)
    print("drawing Board")
    board_pos = ((w - board.image_size[0])/2, 150)
    board.draw(screen)

    print("Starting main loop")
    while True:
        pygame.display.flip()
        clock.tick(30)
        board.draw(screen)
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
                        board.click_field(x, y)

            # TODO: mouse botten down
            #if pygame.mouse.get_pressed(num_buttons=3)[0]:  # left mouse button




