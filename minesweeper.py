import pygame
from pygame.locals import *  # for keypress constants
import random
from colors import *  # for color constants
import time
import controller


class Cell:
    """
    Cell class is used to track the cells' state, drawing info, and number of neighbors
    """
    def __init__(self, row, col, screen):
        self.revealed = False
        self.is_mine = False
        self.flagged = False # flagged = user thinks a bomb is here
        self.rect = None  # used by pygame for click collisions
        self.neighbors = 0
        self.row = row
        self.col = col
        self.flag_icon = None
        self.mine_icon = None
        self.screen = screen

    def __str__(self):
        return "Cell[%d][%d]" % (self.row, self.col)

    def draw(self):
        """
        Draw the cell. Appearance depends on stage and # neighbors
        """
        if (self.flagged):
            self.draw_flag()
        elif (self.revealed == False):
            self.draw_unrevealed_cell()
        elif (self.revealed == True) and (self.is_mine == True):
            self.draw_mine()
        elif (self.revealed == True) and (self.is_mine == False):
            # revealed and empty, gray with lighter border
            self.draw_revealed_cell()


    def draw_flag(self):
        # if flagged by user, draw flag sprite
        # cache flag sprite on first creation
        if self.flag_icon == None:
            self.flag_icon = pygame.sprite.Sprite() # create sprite
            self.flag_icon.image = pygame.image.load("images/flag_32.png").convert() # load flagimage
        # place flag in center of cell
        flag_inset = 8
        self.flag_icon.rect = self.flag_icon.image.get_rect() # use image extent values
        self.flag_icon.rect.topleft = [self.rect.x + flag_inset, self.rect.y + flag_inset] # put the ball in the top left corner
        self.screen.blit(self.flag_icon.image, self.flag_icon.rect)


    def draw_unrevealed_cell(self):
        # if not revealed, cell is gray with highlight and shadow
        pygame.draw.rect(self.screen, bg_gray, self.rect, 0)
        line_width = 2
        # horizontal bottom shadow
        pygame.draw.line(self.screen, bg_gray_dark,
                         (self.rect.x, self.rect.y + self.rect.height - line_width/2),
                         (self.rect.x + self.rect.width, self.rect.y + self.rect.height - line_width/2), line_width)
        # vertical right shadow
        pygame.draw.line(self.screen, bg_gray_dark,
                         (self.rect.x + self.rect.width - line_width/2, self.rect.y),
                         (self.rect.x + self.rect.width - line_width/2, self.rect.y + self.rect.height), line_width)
        # horizontal top highlight
        pygame.draw.line(self.screen, white,
                         (self.rect.x, self.rect.y + line_width/2 - 1),
                         (self.rect.x + self.rect.width - line_width, self.rect.y + line_width/2 - 1), line_width)
        # vertical left highlight
        pygame.draw.line(self.screen, white,
                         (self.rect.x + line_width/2 - 1, self.rect.y),
                         (self.rect.x + line_width/2 - 1, self.rect.y + self.rect.height - line_width), line_width)


    def draw_mine(self):
        if self.mine_icon == None:
            self.mine_icon = pygame.sprite.Sprite() # create sprite
            self.mine_icon.image = pygame.image.load("images/mine_32.png").convert() # load flagimage
        # place icon in center of cell
        inset = 8
        self.mine_icon.rect = self.mine_icon.image.get_rect() # use image extent values
        self.mine_icon.rect.topleft = [self.rect.x + inset, self.rect.y + inset] # put the sprite in the top left corner
        self.screen.blit(self.mine_icon.image, self.mine_icon.rect)


    def draw_revealed_cell(self):
        # all revealed cells get a solid bg rect
        pygame.draw.rect(self.screen, (170,170,170), self.rect, 0)

        # if the cell isn't flagged, is revealed and has neighbors, show the neighbor count
        if (self.is_mine == False) and (self.revealed == True) and (self.neighbors > 0) and not self.flagged:
            # font color is based on neighbor count
            font_color = black
            if self.neighbors == 1:
                font_color = blue
            if self.neighbors == 2:
                font_color = green
            if self.neighbors == 3:
                font_color = red
            if self.neighbors == 4:
                font_color = purple
            font_size = 22
            text_inset = 5
            label_text = "%d" % (self.neighbors)
            label_font = pygame.font.SysFont('Arial', font_size)
            label = label_font.render(label_text, 1, font_color)
            self.screen.blit(label, (self.rect.x + text_inset, self.rect.y + text_inset))



class Minesweeper:
    """
    Main game application
    """
    def __init__(self, filename=None, width=400, height=444, rows=8, cols=8, mines=6):

        # pygame setup
        self._running = True # used in game loop
        self.size = self.width, self.height = width, height
        self.screen = self.setup_screen()


        # scorekeeping
        self.score = 0
        self.start_time = time.time()
        self.time_elapsed = 0
        self.header_height = 44

        # check if user has won
        self.total_to_reveal = (rows * cols) - mines
        self.total_revealed = 0

        # gameboard setup
        self.rows = rows
        self.cols = cols
        self.cell_margin = 1
        self.mines = mines
        self.bomb_locs = list()
        self.board = self.create_game_board(rows=self.rows, cols=self.cols, mines=self.mines, cell_margin=self.cell_margin)


        # draw the starting board; also draws scores
        self.draw_board()

        # computer starts playing
        #controller.play_game(self, self.board, self.score, self.bomb_locs)

        # enter event loop, wait for player input
        self.loop()


    def reset_game(self):

        # reveal all cells
        for i in xrange(self.rows):
            for j in xrange(self.cols):
                self.board[i][j].revealed = True
        self.draw_board()

        # wait for user to hit enter
        paused = True
        print "Hit enter to play again"
        while paused:
            for event in pygame.event.get():
                if event.type == KEYDOWN:
                    if event.key == K_RETURN:
                        paused = False

        # reset score and draw new board
        self.score = 0
        self.start_time = time.time()
        self.time_elapsed = 0
        self.board = self.create_game_board(rows=self.rows, cols=self.cols, mines=self.mines, cell_margin=self.cell_margin)
        self.draw_board()


    def create_game_board(self, rows, cols, mines, cell_margin=0):
        """
        Create the initial game board and populate with mines.
        :return: board - list of lists of Cell objects
        """
        # empty board
        board = [[None for i in xrange(cols)] for i in xrange(rows)]

        # calculate positions of cells
        cell_size_w = int((self.width - (self.cols * cell_margin)) / self.cols)
        cell_size_h = int((self.height - self.header_height - (self.rows * cell_margin)) / self.rows)
        self.cell_size = min(cell_size_h, cell_size_w)

        # populate board with cells
        for i in xrange(rows):
            for j in xrange(cols):
                cell = Cell(i, j, self.screen)
                # cell.revealed = True
                ypos = self.header_height + (self.cell_size * i) + (cell_margin * i)
                xpos = (self.cell_size * j) + (cell_margin * j)
                rect = Rect(xpos, ypos, self.cell_size, self.cell_size)
                cell.rect = rect
                board[i][j] = cell

        # add mines to random cells
        for m in xrange(mines):
            rand_row = random.randint(0, rows-1)
            rand_col = random.randint(0, cols-1)
            self.bomb_locs.append([rand_row, rand_col])
            board[rand_row][rand_col].is_mine = True

        # calculate neighbor values for each cell
        for i in xrange(rows):
            for j in xrange(cols):
                neighbor_offsets = range(-1,2,1)
                for ni in neighbor_offsets:
                    for nj in neighbor_offsets:
                        # do not count this (center) cell
                        if not ((ni == 0) and (nj == 0)):
                            # do not wrap around the board with python's -1 indices:
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
                # draw the cell
                self.board[i][j].draw()
        self.draw_score() # update scoreboard
        pygame.display.flip() # update screen


    def draw_score(self):
        # draw bg rect
        score_rect = Rect(0, 0, self.width, self.header_height)
        pygame.draw.rect(self.screen, bg_gray, score_rect, 0)

        # draw labels
        font_color = red
        font_size = 22
        text_inset = 5
        label_font = pygame.font.SysFont('Courier', font_size, bold=True)

        # score
        score_label = label_font.render(str(self.score), 1, font_color)
        self.screen.blit(score_label, (text_inset, text_inset))

        # timer
        time_label = label_font.render(str(int(self.time_elapsed)), 1, font_color)
        self.screen.blit(time_label, (self.width - (text_inset+50), text_inset))


    def flag_cell(self, i, j):
        if self.board[i][j].flagged == True:
            self.board[i][j].flagged = False
        else:
            self.board[i][j].flagged = True
        self.draw_board()


    def reveal_cell(self, row, col):
        """
        Mark a cell as revealed and if it's not a mine 
        either display its neighbor count or reveal its empty neighbors.
        :param row: int, row index for cell to reveal in board
        :param col: int, col index for cell to reveal in board
        """
        cell = self.board[row][col]        
        if cell.is_mine == True:
            print "You lose! Final Score: ", self.score
            cell.revealed = True
            self.reset_game()
        elif cell.neighbors > 0:
            # cell has a neighbor # value, show it
            cell.revealed = True
            self.total_revealed += 1
            if self.total_revealed == self.total_to_reveal:
                print "You won! Final Score: ", self.score
                self.reset_game()
            self.score += 1
        else:
            # cell is empty, reveal all empty neighbors
            cell.revealed = True
            self.score += 1
            self.total_revealed += 1
            if self.total_revealed == self.total_to_reveal:
                print "You won! Final Score: ", self.score
                self.reset_game()
            self.reveal_neighbors(row, col)


    def reveal_neighbors(self, row, col):
        """
        Recursive function that marks all adjacent unrevealed empty cells as revealed
        :param row: int, row index for cell in board
        :param col: int, col index for cell in board
        """
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
                                self.total_revealed += 1
                                if self.total_revealed == self.total_to_reveal:
                                    print "You won! Final Score: ", self.score
                                    self.reset_game()
                                if cell.neighbors == 0 and cell.is_mine == False:
                                    self.reveal_neighbors(row+ni, col+nj)
                        except IndexError:
                            # if there are no neighbors on this side of the cell, continue
                            pass


    """
    # Pygame Setup and Event Functions
    """

    def setup_screen(self):
        """
        :return: pygame screen object
        """
        pygame.init()
        screen = pygame.display.set_mode(self.size, pygame.HWSURFACE | pygame.DOUBLEBUF)
        screen.fill(bg_gray_dark)
        pygame.display.flip()
        return screen


    def loop(self):
        """
        Game loop that responds to user events
        """
        self._running = True
        while (self._running):
            now = time.time()
            self.time_elapsed = now - self.start_time
            for event in pygame.event.get():
                self.on_event(event)
            self.draw_board()


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
        elif event.type == MOUSEBUTTONUP:
            # left-click
            if event.button == 1:
                # macs don't have right click, so process control-click as right click
                key = pygame.key.get_pressed()
                if key[K_LCTRL]:
                    print "Control and left click pressed"
                    self.flag_event(event)
                else:
                    # left click reveals a cell
                    x,y = event.pos
                    print "You clicked", x, y
                    for i in xrange(self.rows):
                        for j in xrange(self.cols):
                            cell_rect = self.board[i][j].rect
                            if cell_rect.collidepoint(x,y):
                                self.reveal_cell(i, j)
            # right click
            elif event.button == 3:
                print 'right click'
                self.flag_event(event)


    def flag_event(self, event):
        """
        Action taken when screen is right-clicked or ctrl-clicked
        :param event: 
        :return:
        """
        x,y = event.pos
        for i in xrange(self.rows):
            for j in xrange(self.cols):
                cell_rect = self.board[i][j].rect
                if cell_rect.collidepoint(x,y):
                    self.flag_cell(i, j)


if __name__ == "__main__":
    # run graph application
    app = Minesweeper()
