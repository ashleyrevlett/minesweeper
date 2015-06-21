import os
import random
import pygame
from pygame.locals import *  # for keypress constants
from cell import Cell

class Board(object):
    def __init__(self, width, height, rows, cols, mines, screen, header_height):   
        """
        Create game board and populate with mines.        
        """
        self.header_height = header_height
        self.screen = screen      
        self.width = width
        self.height = height
        self.rows = rows
        self.cols = cols
        self.mines = mines
        self.mine_locations = []
        self.cell_margin = 0
        self.cell_size = 24
        self.board_padding = 5

        # board object
        self.cells = [[None for i in xrange(self.cols)] for i in xrange(self.rows)]

        # add unrevealed cells and hidden mines to board
        self.reset()


    def reset(self):
        """
        Reset tiles and spawn mines at new locations
        """

        # set cells up on board
        for i in xrange(self.rows):
            for j in xrange(self.cols):
                cell = Cell(i, j, self.screen)
                # cell.revealed = True
                ypos = self.board_padding + (self.cell_size * i) + (self.cell_margin * i) + self.header_height
                xpos = self.board_padding + (self.cell_size * j) + (self.cell_margin * j)
                rect = Rect(xpos, ypos, self.cell_size, self.cell_size)
                cell.rect = rect
                self.cells[i][j] = cell

        # remove previous mine locations
        del self.mine_locations[:]

        # add new random mines
        for m in xrange(self.mines):            
            rand_row = random.randint(0, self.rows-1)
            rand_col = random.randint(0, self.cols-1)
            random_mine = (rand_row, rand_col)            
            if random_mine not in self.mine_locations:                
                random_mine = (rand_row, rand_col)            
                self.cells[rand_row][rand_col].is_mine = True
                self.mine_locations.append(random_mine)

        # reset cell state and calculate new neighbor values for each cell
        for i in xrange(self.rows):
            for j in xrange(self.cols):
                cell = self.cells[i][j]
                neighbors = self.get_neighbor_cells(i, j)
                for n in neighbors:
                    if n.is_mine: cell.neighbors += 1


    def draw(self):
        """
        Draw all cells on the board
        """
        for i in xrange(self.rows):
            for j in xrange(self.cols):
                # draw the cell
                self.cells[i][j].draw()


    def get_neighbor_cells(self, row, col):
        """        
        :return: list of cell objects surrounding cell at (row, col) position
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

       

