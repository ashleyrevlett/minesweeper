import minesweeper as ms
import random
import time

def check_corners(game, unrevealed):

        for x in xrange(game.rows):
            for y in xrange(game.cols):
                curr_cell = game.board[x][y]
                if curr_cell.neighbors == 1:
                    #check if it's on an edge or corner
                    if x - 1 < 0:
                        left.append([curr_cell.row, curr_cell.col])
                    if x + 1 > game.rows:
                        print curr_cell.row, curr_cell.col, "on the right edge"
                    if y - 1 < 0:
                        print curr_cell.row, curr_cell.col, "on the top edge"
                    if y + 1 > game.cols:
                        print curr_cell.row, curr_cell.col, "on the bottom edge"

class Solver:

    def play_randomly(self, game):
        """
        Play a game of minesweeper, randomly selecting the next move.
        :param game: instance of Minesweeper object
        """

        # create a stack of unrevealed cells
        unrevealed = []

        for i in xrange(game.rows):
            for j in xrange(game.cols):
                unrevealed.append(game.board[i][j])
        # we will pop the cells from the stack, so randomize their order first
        random.shuffle(unrevealed)

        # while the game is being played, choose a random unrevealed cell to reveal next
        while not game.lost_game and not game.won_game:

            cell = unrevealed.pop()

            # before we click the cell, see if only mines remain
            # if so, flag this cell, otherwise reveal it.
            if len(unrevealed) < game.mines:
                game.flag_cell(cell.row, cell.col)
                print "Flagging", cell

            # cell may have been previously revealed as a neighbor
            # if not, reveal it now, otherwise discard the cell and continue
            elif not cell.revealed:
                game.reveal_cell(cell.row, cell.col)
                print "Revealing", cell
            # update the stack to only contain non-revealed cells
            # TODO: make this more efficient by not modifying the list in place
            unrevealed = []
            for i in xrange(game.rows):
                for j in xrange(game.cols):
                    if not game.board[i][j].revealed and not game.board[i][j].flagged:
                        unrevealed.append(game.board[i][j])
            random.shuffle(unrevealed)

            #check to see if there's any corners that can be flagged as bombs
            check_corners(game, unrevealed)

            # draw updated board and pause for a second
            game.draw_board()
            time.sleep(1)