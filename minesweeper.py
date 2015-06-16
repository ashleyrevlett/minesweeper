import sys
import pygame
from pygame.locals import *  # for keypress constants
import random
from colors import *  # for color constants
import time
from cell import Cell
import os
import solver
import stats
from board import Board


class Minesweeper:
    """
    Main game application
    """
    def __init__(self, width, height, rows, cols, mines, use_ai, total_games):

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
        self.use_ai = use_ai
        self.rows = rows
        self.cols = cols

        # used by solvers
        self.total_revealed = 0 # track total number of cells that have been revealed

        #scoreboard assets
        self.button_icon = None
        self.auto_button = None

        # store the absolute filepath of the script; needed later to access assets by absolute path
        self.filepath = os.path.split(os.path.realpath(__file__))[0]

        # gameboard setup        
        self.mines = mines
        self.board = Board(width, height, rows, cols, mines, self.screen, self.header_height)

        # now play!
        # change argument here if you want to play multiple times
        if self.use_ai:
            self.autoplay(total_games)
        self.loop()



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
            self.draw()

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
                self.board.cells[i][j].revealed = True


    def reset_game(self):
        # reset score and draw new board
        self.lost_game = False
        self.won_game = False
        self.score = 0
        self.total_revealed = 0 # used by the solver
        self.start_time = time.time()
        self.time_elapsed = 0
        self.board = Board(self.width, self.height, self.rows, self.cols, self.mines, self.screen, self.header_height)
        self.draw()


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
        if not self.board.cells[i][j].revealed:
            if self.board.cells[i][j].flagged == True:
                self.board.cells[i][j].flagged = False
            else:
                self.board.cells[i][j].flagged = True
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
        cell = self.board.cells[row][col]
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
        neighbors = self.board.get_neighbor_cells(row, col)
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
            self.draw()


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
                                cell_rect = self.board.cells[i][j].rect
                                if cell_rect.collidepoint(x,y):
                                    # if unrevealed, reveal the cell
                                    if not self.board.cells[i][j].revealed:
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
                cell_rect = self.board.cells[i][j].rect
                if cell_rect.collidepoint(x,y):
                    self.flag_cell(i, j)
                    self.draw()


    def draw(self):
        self.board.draw()
        self.draw_score() # update scoreboard
        pygame.display.flip() # update screen


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
                cell = self.board.cells[i][j]
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


if __name__ == "__main__":

    # default settings
    width = 400
    height = 444
    rows = 8
    cols = 8
    mines = 5
    use_ai = False
    total_games = 5

    # command line args override defaults
    if len(sys.argv) > 1:
        width = int(sys.argv[1])
    if len(sys.argv) > 2:
        height = int(sys.argv[2])
    if len(sys.argv) > 3:
        rows = int(sys.argv[3])
    if len(sys.argv) > 4:
        cols = int(sys.argv[4])
    if len(sys.argv) > 5:
        mines = int(sys.argv[5])
    if len(sys.argv) > 6:
        if (sys.argv[6] == 'T' or sys.argv[6] == 't'):
            use_ai = True
    if len(sys.argv) > 7:
        total_games = int(sys.argv[7])
    
    app = Minesweeper(width, height, rows, cols, mines, use_ai, total_games)

