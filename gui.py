import sys
import os
import random
import time
import pygame
from pygame.locals import *  # for keypress constants
from colors import *  # for color constants
from cell import Cell
from board import Board

class Gui(object):

    def __init__(self, board, game):
        self.header_height = 44
        self.button_icon = None
        self.auto_button = None
        self.board = board
        self.game = game

        # store the absolute filepath of the script; needed later to access assets by absolute path
        self.filepath = os.path.split(os.path.realpath(__file__))[0]


    def draw(self):
        # draw bg rect
        score_rect = Rect(0, 0, self.board.width, self.header_height)
        pygame.draw.rect(self.board.screen, bg_gray, score_rect, 0)

        # draw labels
        font_color = red
        font_size = 34
        text_inset = 5

        # need to get absolute pathname for font file
        path = os.path.join(self.filepath, "assets/fonts/DS-DIGIB.ttf")
        label_font = pygame.font.Font(path, font_size)

        # score
        score_text = "{:0>3d}".format(self.game.score) # pad score w/ 0s
        score_label = label_font.render(score_text, 1, font_color)
        self.board.screen.blit(score_label, (text_inset, text_inset))

        # timer
        time_text = "{:0>3d}".format(int(self.game.time_elapsed)) # pad score w/ 0s
        time_label = label_font.render(time_text, 1, font_color)
        self.board.screen.blit(time_label, (self.board.width - (text_inset+50), text_inset))

        # buttons
        self.auto_button = Rect(70, 10, 100, 25)
        pygame.draw.rect(self.board.screen, bg_gray_dark, self.auto_button)        
        auto_font = pygame.font.Font(path, 20)
        auto_label = auto_font.render("Autoplay", 1, black)
        self.board.screen.blit(auto_label, (80,12))

        # draw the playing, winning or losing icon
        if self.game.lost_game:
            icon = pygame.sprite.Sprite() # create sprite
            icon_path = os.path.join(self.filepath, "assets/images/button_frown.png")
            icon.image = pygame.image.load(icon_path).convert() # load flagimage
            icon.rect = icon.image.get_rect() # use image extent values
            icon.rect.topleft = [self.board.width/2 - self.button_icon.rect.width/2, self.header_height/2 - icon.rect.height/2]
            self.board.screen.blit(icon.image, icon.rect)
        elif self.game.won_game:
            icon = pygame.sprite.Sprite() # create sprite
            icon_path = os.path.join(self.filepath, "assets/images/button_glasses.png")
            icon.image = pygame.image.load(icon_path).convert() # load flagimage
            icon.rect = icon.image.get_rect() # use image extent values
            icon.rect.topleft = [self.board.width/2 - self.button_icon.rect.width/2, self.header_height/2 - icon.rect.height/2]
            self.board.screen.blit(icon.image, icon.rect)
        else:
            if self.button_icon == None:
                self.button_icon = pygame.sprite.Sprite() # create sprite
                icon_path = os.path.join(self.filepath, "assets/images/button_smile.png")
                self.button_icon.image = pygame.image.load(icon_path).convert() # load flagimage
            # place icon in center of header
            self.button_icon.rect = self.button_icon.image.get_rect() # use image extent values
            self.button_icon.rect.topleft = [self.board.width/2 - self.button_icon.rect.width/2,
                                             self.header_height/2 - self.button_icon.rect.height/2]
            self.board.screen.blit(self.button_icon.image, self.button_icon.rect)
