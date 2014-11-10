import pygame
from pygame.locals import *  # for keypress constants
import random
from colors import *  # for color constants

"""
Cell states:
unknown /  revealed
"""

class Cell:
    def __init__(self, row, col):
        self.revealed = False
        self.is_mine = False
        self.rect = None  # used by pygame for click collisions
        self.neighbors = 0
        self.row = row
        self.col = col

    def __str__(self):
        return "Cell[%d][%d]" % (self.row, self.col)



class Minesweeper:
    def __init__(self, filename=None, width=600, height=600, rows=8, cols=8):

        # pygame setup
        self._running = True # used in game loop
        self.size = self.width, self.height = width, height
        self.screen = self.setup_screen()

        # scorekeeping
        self.score = 0

        # gameboard setup
        self.rows = rows
        self.cols = cols
        self.cell_margin = 1
        self.board = self.create_game_board(rows=self.rows, cols=self.cols, mines=10, cell_margin=self.cell_margin)

        # draw the starting board
        self.draw_board()

        # enter event loop
        self.loop()



    """
    Gameboard drawing functions
    """
    def create_game_board(self, rows, cols, mines, cell_margin=0):

        # create empty board
        board = [[None for i in xrange(cols)] for i in xrange(rows)]

        # calculate positions of cells
        cell_size_w = int((self.width - (self.cols * cell_margin)) / self.cols)
        cell_size_h = int((self.height - (self.rows * cell_margin)) / self.rows)
        cell_size = min(cell_size_h, cell_size_w)

        # populate board with cells
        for i in xrange(rows):
            for j in xrange(cols):
                cell = Cell(i, j)
                # cell.revealed = True
                ypos = (cell_size * i) + (cell_margin * i)
                xpos = (cell_size * j) + (cell_margin * j)
                rect = Rect(xpos, ypos, cell_size, cell_size)
                cell.rect = rect
                board[i][j] = cell

        # add mines to random cells
        for m in xrange(mines):
            rand_row = random.randint(0, rows-1)
            rand_col = random.randint(0, cols-1)
            board[rand_row][rand_col].is_mine = True

        # calculate neighbor values for each cell
        for i in xrange(rows):
            for j in xrange(cols):
                neighbor_offsets = range(-1,2,1)
                for ni in neighbor_offsets:
                    for nj in neighbor_offsets:
                        # do not count this (center) cell
                        if not ((ni == 0) and (nj == 0)):
                            # do not wrap around the board with pythons -1 indices:
                            if (i + ni < 0) or (i + ni > rows) or (j + nj < 0) or (j + nj > cols):
                                pass
                            else:
                                try:
                                    if board[i+ni][j+nj].is_mine: board[i][j].neighbors += 1
                                except IndexError:
                                    # if there are no neighbors on this side, continue
                                    pass

        return board


    def draw_board(self):
        """
        Draws self.board in its current state
        """
        for i in xrange(self.rows):
            for j in xrange(self.cols):
                color = white
                if (self.board[i][j].revealed == False):
                    # if not revealed, cell is black
                    color = black
                elif (self.board[i][j].revealed == True) and (self.board[i][j].is_mine == True):
                    # revealed and a mine, cell is red
                    color = red
                elif (self.board[i][j].revealed == True) and (self.board[i][j].is_mine == False):
                    # revealed and empty, gray
                    color = gray
                print i, j
                pygame.draw.rect(self.screen, color, self.board[i][j].rect, 0)

                # if the cell is not a mine, revealed and has neighbors, show the neighbor count
                if  (self.board[i][j].is_mine == False) and (self.board[i][j].revealed == True) and (self.board[i][j].neighbors > 0):
                    # if (self.board[i][j].is_mine == False) and (self.board[i][j].neighbors > 0):
                    font_size = 20
                    # label_text = "(%d, %d): %d" % (i, j, self.board[i][j].neighbors)
                    label_text = "%d" % (self.board[i][j].neighbors)
                    label_font = pygame.font.SysFont('Arial', font_size)
                    label = label_font.render(label_text, 1, green)
                    self.screen.blit(label, (self.board[i][j].rect.x, self.board[i][j].rect.y))

        pygame.display.flip()


    def reveal_cell(self, row, col):
        print "Revealing cell", row, col
        cell = self.board[row][col]
        print cell.is_mine

        if cell.is_mine == True:
            print "You lose! Final Score: ", self.score
            cell.revealed = True
        elif cell.neighbors > 0:
            # cell has a neighbor # value, show it
            cell.revealed = True
            self.score += 1
        else:
            # cell is empty, reveal all empty neighbors
            cell.revealed = True
            self.score += 1
            self.reveal_neighbors(row, col)

        # draw updated board
        self.draw_board()


    def reveal_neighbors(self, row, col):
        # calculate neighbor values for each cell
        neighbor_offsets = range(-1,2,1)
        for ni in neighbor_offsets:
            for nj in neighbor_offsets:
                # do not count this (center) cell
                if not ((ni == 0) and (nj == 0)):
                    # do not wrap around the board with pythons -1 indices:
                    if (row + ni < 0) or (row + ni > self.rows) or (col + nj < 0) or (col + nj > self.cols):
                        pass
                    else:
                        try:
                            # if not revealed yet, reveal it and reveal its neighbors
                            cell = self.board[row+ni][col+nj]
                            if cell.revealed == False:
                                cell.revealed = True
                                if cell.neighbors == 0 and cell.is_mine == False:
                                    self.reveal_neighbors(row+ni, col+nj)
                        except IndexError:
                            # if there are no neighbors on this side of the cell, continue
                            pass


    """
    Pygame Setup and Event Functions
    """

    def setup_screen(self):
        """
        :return: pygame screen object
        """
        pygame.init()
        screen = pygame.display.set_mode(self.size, pygame.HWSURFACE | pygame.DOUBLEBUF)
        screen.fill((60, 60, 60))
        pygame.display.flip()
        return screen


    def loop(self):
        """
        Game loop that responds to user events
        """
        self._running = True
        while (self._running):
            for event in pygame.event.get():
                self.on_event(event)


    def on_event(self, event):
        """
        Handle individual events
        :param event: pygame event
        """
        if event.type == pygame.QUIT:
            print "App quitting"
            self._running = False

        # keypresses
        elif event.type == KEYDOWN:
            if event.key == K_ESCAPE:
                self._running = False

        # mouse events
        elif event.type == MOUSEBUTTONUP and event.button == 1:
            x,y = event.pos
            print "You clicked", x, y
            for i in xrange(self.rows):
                for j in xrange(self.cols):
                    cell_rect = self.board[i][j].rect
                    if cell_rect.collidepoint(x,y):
                        self.reveal_cell(i, j)


if __name__ == "__main__":
    # run graph application
    app = Minesweeper()

