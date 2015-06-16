import random
import time
import minesweeper as ms


class Solver(object):

    def __init__(self):
        pause = True
        sleep_time = .5

    @staticmethod
    def is_cell_safe(cell, board):
        """
        Assumes cell is unrevealed. Tries to find if it's safe to click based on neighbors
        """
        # look at a cell and the cell's revealed neighbors
        # if any neighbors say there's 1 mine nearby, and that neighbor has neighbors which
        # contain a flag, it's safe to click here
        # TODO: this really needs to only check neighbors' neighbors that border the original cell.
        # right now more cells are considered than should be.
        safe = False
        neighbors = board.get_neighbor_cells(cell.row, cell.col)
        revealed_neighbors = [n for n in neighbors if n.revealed or n.flagged]
        for n in revealed_neighbors:
            if n.neighbors > 0:
                n_neighbors = board.get_neighbor_cells(n.row, n.col)
                flagged_n_neighbors = [n for n in n_neighbors if n.flagged]
                if len(flagged_n_neighbors) > 0:
                    safe = True
        return safe



    @staticmethod
    def play_best_guess(game, pause=True, sleep_time=.25):
        """
        Best-guess AI effort. First looks for any revealed cells that have the same number
        of unrevealed neighbors as there are neighboring bombs. If so, flags all neighbors.
        Then it looks at all unrevealed squares and sees if their neighbors prove this square is safe.
        If so, it reveals the square. If no changes were performed in the previous two steps,
        a random unrevealed squares is selected for revealing. Then the whole process loops again.
        """
        # create a list of cells
        cells = [game.board.cells[i][j]
                 for i in xrange(game.rows)
                 for j in xrange(game.cols)]

        first_cell = cells[0]
        game.reveal_cell(first_cell.row, first_cell.col)

        # draw updated board and self.pause for a second
        game.draw()
        if pause == True:
            time.sleep(sleep_time)


        total_flagged = 0
        while not game.lost_game and not game.won_game:

            # remember if we've made a move in the while loop
            # so we know whether to make a random move later on
            made_move = False

            # look through all revealed cells for any with a number of neighboring mines.
            # if the cell has the same number of unrevealed neighbors as the cell's
            # number of neighboring mines, all the unrevealed neighbors must be mines.
            revealed_numbered_cells = [c for c in cells if c.revealed and (not c.flagged) and (c.neighbors > 0)]
            while revealed_numbered_cells:
                cell = revealed_numbered_cells.pop()
                # cell may have been marked flagged after revealed_numbered_cells was compiled
                if not cell.flagged:
                    neighbor_cells = game.board.get_neighbor_cells(cell.row, cell.col)
                    flagged_neighbors = [n for n in neighbor_cells if n.flagged]
                    number_remaining_mines = cell.neighbors - len(flagged_neighbors)
                    unknown_neighbors = [n for n in neighbor_cells if not n.flagged and not n.revealed]
                    if number_remaining_mines > 0 and len(unknown_neighbors) == number_remaining_mines:
                        # flag every neighbor
                        for c in unknown_neighbors:
                            if total_flagged < game.mines:
                                total_flagged += 1
                                game.flag_cell(c.row, c.col)
                                if (game.test_did_win()):
                                    game.game_over()
                                game.draw()
                                if pause == True:
                                    time.sleep(sleep_time)
                                made_move = True

            # we may have won with the flag above so test whether we're still playing
            # before further calculations
            if not game.lost_game and not game.won_game:
                # loop through all unrevealed, unflagged cells and see if we know it's safe to reveal
                for c in cells:
                    if not c.revealed and not c.flagged and Solver.is_cell_safe(c, game.board):
                        game.reveal_cell(c.row, c.col)
                        if (game.test_did_win()):
                            game.game_over()
                        game.draw()
                        if pause == True:
                            time.sleep(sleep_time)
                        made_move = True

                # assume we've made our best guesses and now have to guess randomly
                # this will prevent us from looping forever if no obvious moves are available
                if not made_move:
                    unrevealed = [c for c in cells if not c.revealed and not c.flagged]
                    if len(unrevealed) > 0:
                        cell = random.choice(unrevealed)
                        game.reveal_cell(cell.row, cell.col)
                        if (game.test_did_win()):
                            game.game_over()
                        game.draw()
                        if pause == True:
                            time.sleep(sleep_time)

