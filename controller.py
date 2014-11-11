import random

coord_list = list()

def play_game(obj, board, score, bomb_locs):

    x, y = get_random_coords(board)
    print bomb_locs, "are the locations of the bombs"

    # special starting case: prevent 1st cell from being a mine
    # if it IS a bomb, choose initial starting point as [0,0]
    # (http://en.wikipedia.org/wiki/Microsoft_Minesweeper#Original)
    if score == 0:
        while board[x][y].is_mine == True:
            print "got a mine on your first try"
            if x != 0 and y != 0:
                x = 0
                y = 0
            # todo: if [0,0] was chosen first, the new cell should be the one closest to it, not a random one
            else:
                x, y = get_random_coords(board)

    #keep revealing squares until you hit a mine OR win
    while board[x][y].is_mine != True:

        #keep picking random squares until you hit one that isn't yet been revealed
        while board[x][y].revealed == True:
                x, y = get_random_coords(board)
        print "chose cell", x, y
        coord_list.append([x,y])
        obj.reveal_cell(x, y)
        x, y = get_random_coords(board)

    print "chose cell", x, y, "where there was a mine"
    obj.reveal_cell(x, y)

def get_random_coords(board):
    x = random.randint(0, len(board[0])-1)
    y = random.randint(0, len(board)-1)
    return x, y
