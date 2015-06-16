# board.py

import pygame
from colors import *  # for color constants
import os
from cell import Cell
from pygame.locals import *  # for keypress constants
import random

class Board:
    """
    Cell class is used to track the cells' state, drawing info, and number of neighbors
    """
    def __init__(self, width, height, rows, cols, mines, screen, header_height):   

        """
        Create the initial game board and populate with mines.
        :return: board - list of lists of Cell objects
        """
        self.header_height = header_height
        self.screen = screen      
        self.width = width
        self.height = height
        self.rows = rows
        self.cols = cols
        self.mines = mines
        self.mine_locations = []
        cell_margin = 0

        # board object
        self.cells = [[None for i in xrange(cols)] for i in xrange(rows)]

        # calculate positions of cells
        cell_size_w = int((self.width - (cols * cell_margin)) / self.cols)
        cell_size_h = int(((self.height) - header_height - (rows * cell_margin)) / self.rows)
        self.cell_size = min(cell_size_h, cell_size_w)

        # populate board with cells
        for i in xrange(self.rows):
            for j in xrange(self.cols):
                cell = Cell(i, j, self.screen)
                # cell.revealed = True
                ypos = (self.cell_size * i) + (cell_margin * i) + header_height
                xpos = (self.cell_size * j) + (cell_margin * j)
                rect = Rect(xpos, ypos, self.cell_size, self.cell_size)
                cell.rect = rect
                self.cells[i][j] = cell

        # add mines to random cells
        # have to track which mines have been added so we don't duplicate them        
        for m in xrange(mines):
            # try to randomly set a random mine
            rand_row = random.randint(0, rows-1)
            rand_col = random.randint(0, cols-1)
            random_mine = (rand_row, rand_col)            
            if random_mine not in self.mine_locations:                
                random_mine = (rand_row, rand_col)            
            	self.cells[rand_row][rand_col].is_mine = True
            	self.mine_locations.append(random_mine)

        # calculate new neighbor values for each cell
        for i in xrange(rows):
            for j in xrange(cols):
                # get this cell's neighbors
                cell = self.cells[i][j]
                neighbors = self.get_neighbor_cells(i, j)
                for n in neighbors:
                    if n.is_mine: cell.neighbors += 1



    def get_neighbor_cells(self, row, col):
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
        # calculate rows and columns values for each neighboring cell
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
                            # try to add the neighbor to the list
                            cell = self.cells[row+ni][col+nj]
                            neighbors.append(cell)
                        except IndexError:
                            # but if there are no neighbors on this side of the cell, continue
                            # like if we are on the edge of the board
                            pass
        return neighbors



    def draw(self):
        """
        Draws self.board in its current state
        """
        for i in xrange(self.rows):
            for j in xrange(self.cols):
                # draw the cell
                self.cells[i][j].draw()
        


    def __str__(self):        
        for i in xrange(self.rows):
            for j in xrange(self.cols):
                neighbors = self.get_neighbor_cells(i,j)
                print self.cells[i][j]
                for n in neighbors:
                    print '\t', n
                print ""

