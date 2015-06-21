import sys
import time
import yaml
import pygame
from pygame.locals import *  # for keypress constants
from cell import Cell
from board import Board
from gui import Gui
import solver
import colors


class Minesweeper(object):
    """
    Main game application
    """
    def __init__(self, difficulty, use_ai, total_games):

        # read settings file
        with open('settings.yaml', 'r') as f:
            settings = yaml.load(f)            
            self.rows = settings[difficulty]["rows"]
            self.cols = settings[difficulty]["columns"]
            self.mines = settings[difficulty]["mines"]
            self.width = settings[difficulty]["width"]
            self.height = settings[difficulty]["height"]
            self.size = self.width, self.height
        
        # pygame setup
        self._running = True # used to stop game loop        
        self.screen = self.setup_screen()

        # scorekeeping
        self.start_time = time.time()
        self.time_elapsed = 0        
        self.score = 0
        self.lost_game = False
        self.won_game = False

        # game board setup        


        # AI / autoplay
        self.use_ai = use_ai        

        # create board and gui 
        self.board = Board(self.width, self.height, self.rows, self.cols, self.mines, self.screen, 36)    
        self.gui = Gui(self.board, self)

        # autoplay or enter event loop        
        if self.use_ai:
            self.autoplay(total_games)
        self.loop()



    def autoplay(self, times_to_play):
        """
        Automatically play minesweeper a certain number of times.        
        :param times_to_play: int
        """
        for i in range(times_to_play):
            print "\n### Playthrough", i

            # draw the starting board; also draws scores
            self.draw()

            # play 1 game

            solver.Solver.play_best_guess(self)            
            
            # reset board
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
        self.start_time = time.time()
        self.time_elapsed = 0
        self.board.reset()
        self.draw()


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
        screen.fill(colors.bg_gray)        
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
                    self.flag_event(event)
                else:
                    # left click reveals a cell
                    x,y = event.pos
                    if self.gui.button_icon.rect.collidepoint(x,y):
                        self.reset_game()
                    if self.gui.auto_icon.rect.collidepoint(x,y):
                        self.autoplay(total_games)
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
        # Fill background
        background = pygame.Surface(self.screen.get_size())
        background = background.convert()
        background.fill(colors.gray) 
        self.board.draw()
        self.gui.draw() # update scoreboard
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

    # defaults
    difficulty = "easy"
    use_ai = False
    total_games = 5

    # command line args override defaults
    if len(sys.argv) > 1:
        difficulty = sys.argv[1].lower()
        if not (difficulty == "easy" or difficulty == "intermediate" or difficulty == "expert"):
            print """
            Error in command line arguments.
            Usage: python minesweeper.py difficulty use_ai total_games
            \tdifficulty - easy, intermediate, expert
            \tuse_ai - t or f
            \ttotal_games - integer\n"""
            exit()

    if len(sys.argv) > 2:
        if (sys.argv[2].lower() == 't'):
            use_ai = True
    if len(sys.argv) > 3:
        total_games = max(1, int(sys.argv[3])) # at least 1 game
    
    app = Minesweeper(difficulty, use_ai, total_games)
