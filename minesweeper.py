import pygame
from pygame.locals import *  # for keypress constants
import random
from colors import *  # for color constants
import time
from cell import Cell
import os
import controller
import solver
import pickle
import stats

"""
Change the USE_AI constant to switch between AI and human gameplay modes.
"""
USE_AI = False

#uncomment to play a given number of times
NUMBER_OF_GAMES = 20 # number of games AI should autoplay

class Minesweeper:
    """
    Main game application
    """
    def __init__(self, filename=None, width=400, height=444, rows=6, cols=6, mines=5):

        # pygame setup
        self._running = True # used in game loop
        self.size = self.width, self.height = width, height
        self.screen = self.setup_screen()

        # scorekeeping
        self.score = 0
        self.start_time = time.time()
        self.time_elapsed = 0
        self.header_height = 44
        self.lost_game = False
        self.won_game = False

        # used by solvers
        self.total_revealed = 0 # track total number of cells that have been revealed

        #scoreboard assets
        self.button_icon = None
        self.auto_button = None

        # store the absolute filepath of the script; needed later to access assets by absolute path
        self.filepath = os.path.split(os.path.realpath(__file__))[0]

        # gameboard setup
        self.rows = rows
        self.cols = cols
        self.cell_margin = 1
        self.mines = mines
        self.bomb_locs = list()
        self.board = self.create_game_board(rows=self.rows, cols=self.cols, mines=self.mines, cell_margin=self.cell_margin)

        # now play!
        # change argument here if you want to play multiple times
        if USE_AI:
            self.autoplay()
        self.loop()


    def test_did_win(self):
        """
        Tests whether the game's board is in a winning position.
        Also sets self.won_game for use in the solver.
        Winning conditions:
        All cells revealed or with flags
        All mines have flags
        No cells without mines have flags
        :return: bool
        """
        did_win = True
        for i in xrange(self.rows):
            for j in xrange(self.cols):
                cell = self.board[i][j]
                # unrevealed and not flagged squares
                if not cell.revealed and not cell.flagged:
                    did_win = False
                    break
                # incorrect flags
                if cell.flagged and not cell.is_mine:
                    did_win = False
                    break
                # unflagged mines
                if cell.is_mine and not cell.flagged:
                    did_win = False
                    break
        if did_win:
            print "You won!"
            self.won_game = True

        return did_win


    @staticmethod
    def get_neighbors(row, col, board):
        """
        This is a static method so it can be called using different boards.
        Currently the Minesweeper class only stores 1 board, but in the solver
        we need to get the neighbors of cells in many different board configurations.
        To call it, use the class not the instance.
        :param row: row index of the cell whose neighbors we want to retrieve
        :param col: col index of the cell
        :param board: instance of the board list of lists of cells
        :return: list of cell object
        """
        neighbors = []
        rows = len(board)
        cols = len(board[0])
        # calculate rows and columns values for each neighboring cell
        neighbor_offsets = range(-1,2,1)
        for ni in neighbor_offsets:
            for nj in neighbor_offsets:
                # do not count this (center) cell
                if not ((ni == 0) and (nj == 0)):
                    # do not wrap around the board with pythons -1 indices:
                    if (row + ni < 0) or (row + ni > rows) or (col + nj < 0) or (col + nj > cols):
                        pass
                    else:
                        try:
                            # try to add the neighbor to the list
                            cell = board[row+ni][col+nj]
                            neighbors.append(cell)
                        except IndexError:
                            # but if there are no neighbors on this side of the cell, continue
                            # like if we are on the edge of the board
                            pass
        return neighbors


    @staticmethod
    def print_board_state(board):
        """
        Prints the state of any board. Used for debugging.
        :param game: instance of minesweeper's board (list of list of cells)
        """
        # find cell surrounded by revealed 1s
        rows = len(board)
        cols = len(rows[0])
        for i in xrange(rows):
            for j in xrange(cols):
                neighbors = Minesweeper.get_neighbors(i,j,board)
                print board[i][j]
                for n in neighbors:
                    print '\t', n
                print ""

    def autoplay(self, times_to_play):
        """
        Automatically play minesweeper a certain number of times.
        Currently only has random method, but could allow for selection of other methods.
        :param times_to_play: int
        :return:
        """
        for i in range(times_to_play):
            print "\n### Playthrough", i

            # draw the starting board; also draws scores
            self.draw_board()

            # computer starts playing
            s = solver.Solver()
            # s.play_randomly(self)
            s.play_best_guess(self)

            play_info = stats.Stat(i, self.score, self.won_game)
            stats.add_stat(play_info)

            # a new board is automatically created when the game is reset
            self.reset_game()


    def game_over(self):
        # unflag and reveal all cells
        for i in xrange(self.rows):
            for j in xrange(self.cols):
                self.board[i][j].revealed = True


    def reset_game(self):
        # reset score and draw new board
        self.lost_game = False
        self.won_game = False
        self.score = 0
        self.total_revealed = 0 # used by the solver
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
        cell_size_h = int(((self.height) - self.header_height - (self.rows * cell_margin)) / self.rows)
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

        # create button for turning AI on/off

        # add mines to random cells
        # have to track which mines have been added so we don't duplicate them
        random_mines = []
        for m in xrange(mines):
            # try getting a random mine
            rand_row = random.randint(0, rows-1)
            rand_col = random.randint(0, cols-1)
            random_mine = (rand_row, rand_col)
            # if it's already been mined, try again until you get an unmined one
            while random_mine in random_mines:
                rand_row = random.randint(0, rows-1)
                rand_col = random.randint(0, cols-1)
                random_mine = (rand_row, rand_col)
            # add mine to bookkeeping list, set  as mined
            random_mines.append(random_mine)
            self.bomb_locs.append([rand_row, rand_col])
            board[rand_row][rand_col].is_mine = True

        # calculate neighbor values for each cell
        for i in xrange(rows):
            for j in xrange(cols):
                # get this cell's neighbors
                cell = board[i][j]
                neighbors = Minesweeper.get_neighbors(i, j, board)
                for n in neighbors:
                    if n.is_mine: cell.neighbors += 1

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
        """
        called by draw_board, don't call directly
        """
        # draw bg rect
        score_rect = Rect(0, 0, self.width, self.header_height)
        pygame.draw.rect(self.screen, bg_gray, score_rect, 0)

        # draw labels
        font_color = red
        font_size = 34
        text_inset = 5

        # need to get absolute pathname for font file
        path = os.path.join(self.filepath, "assets/fonts/DS-DIGIB.ttf")
        label_font = pygame.font.Font(path, font_size)

        # score
        score_text = "{:0>3d}".format(self.score) # pad score w/ 0s
        score_label = label_font.render(score_text, 1, font_color)
        self.screen.blit(score_label, (text_inset, text_inset))

        # timer
        time_text = "{:0>3d}".format(int(self.time_elapsed)) # pad score w/ 0s
        time_label = label_font.render(time_text, 1, font_color)
        self.screen.blit(time_label, (self.width - (text_inset+50), text_inset))

        # buttons
        self.auto_button = Rect(70, 5, 100, 35)
        pygame.draw.rect(self.screen, blue, self.auto_button)

        auto_font = pygame.font.SysFont("Arial Black", 20)
        auto_label = auto_font.render("Autoplay", 1, (0, 0, 0))

        self.screen.blit(auto_label, (70,5))


        # need to get absolute pathname for font file
        path = os.path.join(self.filepath, "assets/fonts/DS-DIGIB.ttf")
        label_font = pygame.font.Font(path, font_size)
        #

        # draw the playing, winning or losing icon
        if self.lost_game:
            icon = pygame.sprite.Sprite() # create sprite
            icon_path = os.path.join(self.filepath, "assets/images/button_frown.png")
            icon.image = pygame.image.load(icon_path).convert() # load flagimage
            icon.rect = icon.image.get_rect() # use image extent values
            icon.rect.topleft = [self.width/2 - self.button_icon.rect.width/2, self.header_height/2 - icon.rect.height/2]
            self.screen.blit(icon.image, icon.rect)
        elif self.won_game:
            icon = pygame.sprite.Sprite() # create sprite
            icon_path = os.path.join(self.filepath, "assets/images/button_glasses.png")
            icon.image = pygame.image.load(icon_path).convert() # load flagimage
            icon.rect = icon.image.get_rect() # use image extent values
            icon.rect.topleft = [self.width/2 - self.button_icon.rect.width/2, self.header_height/2 - icon.rect.height/2]
            self.screen.blit(icon.image, icon.rect)
        else:
            if self.button_icon == None:
                self.button_icon = pygame.sprite.Sprite() # create sprite
                icon_path = os.path.join(self.filepath, "assets/images/button_smile.png")
                self.button_icon.image = pygame.image.load(icon_path).convert() # load flagimage
            # place icon in center of header
            self.button_icon.rect = self.button_icon.image.get_rect() # use image extent values
            self.button_icon.rect.topleft = [self.width/2 - self.button_icon.rect.width/2,
                                             self.header_height/2 - self.button_icon.rect.height/2]
            self.screen.blit(self.button_icon.image, self.button_icon.rect)


    def flag_cell(self, i, j):
        """
        Flags cell and redraws board when user right-clicks or control-clicks cell
        :param i: cell row
        :param j: cell column
        """
        # do not flag revealed squares
        if not self.board[i][j].revealed:
            if self.board[i][j].flagged == True:
                self.board[i][j].flagged = False
            else:
                self.board[i][j].flagged = True
        print "testing if won:", self.test_did_win()
        if self.test_did_win():
            self.game_over()


    def reveal_cell(self, row, col):
        """
        Mark a cell as revealed and if it's not a mine 
        either display its neighbor count or reveal its empty neighbors.
        :param row: int, row index for cell to reveal in board
        :param col: int, col index for cell to reveal in board
        """
        cell = self.board[row][col]
        self.total_revealed += 1
        if cell.is_mine == True:
            print "You lose! Final Score: ", self.score
            cell.revealed = True
            cell.detonated = True
            self.lost_game = True
            self.game_over()
        elif cell.neighbors > 0:
            # cell has a neighbor # value, show it
            cell.revealed = True
            self.score += 1
        else:
            # cell is empty, reveal all empty neighbors
            cell.revealed = True
            self.score += 1
            self.reveal_neighbors(row, col)


    def reveal_neighbors(self, row, col):
        """
        Recursive function that marks all adjacent unrevealed empty cells as revealed
        :param row: int, row index for cell in board
        :param col: int, col index for cell in board
        """
        neighbors = Minesweeper.get_neighbors(row, col, self.board)
        for cell in neighbors:
            # if not revealed yet, reveal it and reveal its neighbors
            if not cell.revealed:
                cell.revealed = True
                self.total_revealed += 1
                if cell.neighbors == 0 and cell.is_mine == False:
                    self.reveal_neighbors(cell.row, cell.col)


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
            # increment the game clock if we're playing now
            if (not self.lost_game) and (not self.won_game):
                now = time.time()
                self.time_elapsed = now - self.start_time
            # listen for user input events
            for event in pygame.event.get():
                self.on_event(event)
            # draw the updated game board and score
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
                    if self.button_icon.rect.collidepoint(x,y):
                        self.reset_game()
                    if self.auto_button.collidepoint(x,y):
                        self.autoplay(NUMBER_OF_GAMES)
                        stats.plot_stats(NUMBER_OF_GAMES, self.rows, self.cols, self.mines)
                        self.reset_game()

                    else:
                        for i in xrange(self.rows):
                            for j in xrange(self.cols):
                                cell_rect = self.board[i][j].rect
                                if cell_rect.collidepoint(x,y):
                                    # if unrevealed, reveal the cell
                                    if not self.board[i][j].revealed:
                                        self.reveal_cell(i, j)
                                        # test if we won or not
                                        if self.test_did_win():
                                            self.game_over()
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
                    self.draw_board()


if __name__ == "__main__":
    # run graph application
    app = Minesweeper()
