import pygame
import math
from queue import PriorityQueue

WIDTH = 800
WIN = pygame.display.set_mode((WIDTH, WIDTH))
pygame.display.set_caption("A* Path Finding Algorithm")

RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 255, 0)
YELLOW = (255, 255, 0)
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
PURPLE = (128, 0, 128)
ORANGE = (255, 165, 0)
GREY = (128, 128, 128)
TURQUOISE = (64, 224, 208)

class Spot:
    def __init__(self, row, col, width, totalRows):
        self.row = row
        self.col = col

        # x, y are the starting position. Multi with width: eg: size of the console is 800, we want a 50x50 grid,
        # the starting x, y would be 800/50 = 16 as the width of each grid is 16
        self.x = row * width
        self.y = col * width
        self.color = WHITE
        self.neighbors = []
        self.width = width
        self.totalRows = totalRows

    def get_pos(self):
        return self.row, self.col

    def is_closed(self):
        return self.color == RED

    def is_open(self):
        return self.color == GREEN

    def is_barrier(self):
        return self.color == BLACK

    def is_start(self):
        return self.color == ORANGE

    def is_end(self):
        return self.color == PURPLE

    def reset(self):
        self.color = WHITE

    def make_start(self):
        self.color = ORANGE

    def make_close(self):
        self.color = RED

    def make_open(self):
        self.color = GREEN

    def make_barrier(self):
        self.color = BLACK

    def make_end(self):
        self.color = TURQUOISE

    def make_path(self):
        self.color = PURPLE

    def draw(self, win):
        pygame.draw.rect(win, self.color, (self.x, self.y, self.width, self.width))

    def update_neighbors(self, grid):
        self.neighbors = []
        if self.row < self.totalRows - 1 and not grid[self.row + 1][self.col].is_barrier(): # down neighbor
            self.neighbors.append(grid[self.row + 1][self.col])

        if self.row > 0 and not grid[self.row - 1][self.col].is_barrier(): # up neighbor
            self.neighbors.append(grid[self.row - 1][self.col])

        if self.col > 0 and not grid[self.row][self.col - 1].is_barrier(): # left neighbor
            self.neighbors.append(grid[self.row][self.col - 1])

        if self.col < self.totalRows - 1 and not grid[self.row][self.col + 1].is_barrier(): # right neighbor
            self.neighbors.append(grid[self.row][self.col + 1])

        # if self.row < self.totalRows - 1 and self.col > 0 and not grid[self.row + 1][self.col - 1].is_barrier(): # left down neighbor
        #     self.neighbors.append(grid[self.row + 1][self.col - 1])
        #
        # if self.row < self.totalRows - 1 and self.col < self.totalRows - 1 and not grid[self.row + 1][self.col + 1].is_barrier(): # right down neighbor
        #     self.neighbors.append(grid[self.row + 1][self.col + 1])
        #
        # if self.row > 0 and self.col > 0 and not grid[self.row - 1][self.col - 1].is_barrier(): # left up neighbor
        #     self.neighbors.append(grid[self.row - 1][self.col - 1])
        #
        # if self.row > 0 and self.col < self.totalRows - 1 and not grid[self.row - 1][self.col + 1].is_barrier(): # right up neighbor
        #     self.neighbors.append( grid[self.row - 1][self.col + 1])

    def __lt__(self, other): # less than, compare other spots
        return False


# heuristic function, manhattan distance -- distance = abs(row - destination.row) + abs(col - destination.col)
def h(p1, p2):
    x1, y1 = p1
    x2, y2 = p2
    return abs(x1 - x2) + abs(y1 - y2)

# A faster function that uses the Pythagorean theorem to calculate the distance, which allows users to customize.
def h2(p1, p2):
    x1, y1 = p1
    x2, y2 = p2
    return (x1 - x2) ** 2 + (y1 - y2) ** 2

# Make grid on the game board
def make_grid(rows, width):
    grid = []
    gap = width // rows  # width is the width of our entire grid, rows is the number of rows in the grid
    for i in range(rows):
        grid.append([])
        for j in range(rows): # remember we are using a square grid, so cols = rows
            spot = Spot(i, j, gap, rows)
            grid[i].append(spot)  # grid[i] is the grid we just created in line 90
    return grid

# Draw grids to create blocks on the board
def draw_grid(win, rows, width):
    gap = width // rows
    for i in range(rows):
        pygame.draw.line(win, GREY, (0, i * gap), (width, i * gap)) # draw horizontal lines
        
        for j in range(rows):
            pygame.draw.line(win, GREY, (j * gap, 0), (j * gap, width))


def draw(win, grid, rows, width):
    win.fill(WHITE)

    for row in grid:
        for spot in row:
            spot.draw(win)
    draw_grid(win, rows, width)
    pygame.display.update()


def get_clicked_pos(pos, rows, width):
    gap = width // rows
    i, j = pos

    row = i // gap
    col = j // gap
    return row, col

# Path showing function when the closest path has been found
def reconstruct_path(came_from, current, draw):
    while current in came_from:
        current = came_from[current]
        current.make_path()
        draw()


# Path finding algorithm
def algorithm(draw, grid, start, end):
    count = 0
    open_set = PriorityQueue()
    open_set.put((0, count, start))
    came_from = {}
    g_score = {spot: float("inf") for row in grid for spot in row}  # Map of the distances from where the spot is to the starting point
    g_score[start] = 0
    f_score = {spot: float("inf") for row in grid for spot in row}  # Map of the distances from where the spot is to the destination
    f_score[start] = h(start.get_pos(), end.get_pos())

    open_set_hash = {start}

    while not open_set.empty():
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()

        current = open_set.get()[2]
        open_set_hash.remove(current)  # This line is for memory release

        if current == end:
            reconstruct_path(came_from, end, draw)
            end.make_end()
            return True

        for neighbor in current.neighbors:
            temp_g_score = g_score[current] + 1

            if temp_g_score < g_score[neighbor]:
                came_from[neighbor] = current
                g_score[neighbor] = temp_g_score
                f_score[neighbor] = temp_g_score + h(neighbor.get_pos(), end.get_pos())
                if neighbor not in open_set_hash:
                    count += 1
                    open_set.put((f_score[neighbor], count, neighbor))
                    open_set_hash.add(neighbor)
                    neighbor.make_close()
        draw()

        if current != start:
            current.make_close()
    return False


def main(win, width):
    ROWS = 50
    grid = make_grid(ROWS, width)

    start = None
    end = None

    run = True
    started = False
    while run:
        draw(win, grid, ROWS, width)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:  # if we hit the exit button, it stops running
                run = False

            if started:
                continue

            if pygame.mouse.get_pressed()[0]: # left mouse button
                pos = pygame.mouse.get_pos()
                row, col = get_clicked_pos(pos, ROWS, width)
                spot = grid[row][col]
                if not start and spot != end:
                    start = spot
                    start.make_start()

                elif not end and spot != start:  # condition after the end is to avoid start and end have same positions
                    end = spot
                    end.make_end()

                elif spot != end and spot != start:
                    spot.make_barrier()

            elif pygame.mouse.get_pressed()[2]: # right mouse button
                pos = pygame.mouse.get_pos()
                row, col = get_clicked_pos(pos, ROWS, width)
                spot = grid[row][col]
                spot.reset()
                if spot == start:
                    start = None
                elif spot == end:
                    end = None

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE and start and end:
                    for row in grid:
                        for spot in row:
                            spot.update_neighbors(grid)
                    algorithm(lambda: draw(win, grid, ROWS, width), grid, start, end)

                if event.key == pygame.K_c:
                    start = None
                    end = None
                    grid = make_grid(ROWS, width)

    pygame.quit()


main(WIN, WIDTH)



