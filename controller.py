import random

def start_game(obj, board):

    x = random.randint(1, len(board[0]))
    y = random.randint(1, len(board))

    # prevent 1st chosen cell from being a mine
    while board[x-1][y-1].is_mine is True:
        # choose initial starting point as [0,0] (http://en.wikipedia.org/wiki/Microsoft_Minesweeper#Original)
        if x is not 0 and y is not 0:
            x = 0
            y = 0
        # todo: if [0,0] was chosen first, the new cell should be the one closest to it, not a random one
        else:
            x = random.randint(1, len(board[0]))
            y = random.randint(1, len(board))
    obj.reveal_cell(x-1, y-1)
