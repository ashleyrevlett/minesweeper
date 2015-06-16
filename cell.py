import pygame
from colors import *  # for color constants
import os


class Cell:
    """
    Cell class is used to track the cells' state, drawing info, and number of neighbors
    """
    def __init__(self, row, col, screen):
        self.revealed = False
        self.is_mine = False
        self.detonated = False
        self.flagged = False # flagged = user thinks a bomb is here
        self.rect = None  # used by pygame for click collisions
        self.neighbors = 0
        self.row = row
        self.col = col
        self.flag_icon = None
        self.mine_icon = None
        self.screen = screen
        (self.filepath, filename) = os.path.split(os.path.realpath(__file__))


    def reset(self):
        self.revealed = False
        self.is_mine = False
        self.detonated = False
        self.flagged = False


    def draw(self):
        """
        Draw the cell. Appearance depends on stage and # neighbors

        detonated bomb                -> red bomb icon
        revealed non-flagged non-bomb -> empty or neighbor #
        revealed non-flagged bomb     -> bomb icon
        revealed flagged bomb         -> flag icon
        revealed flagged non-bomb     -> bomb-x icon
        unrevealed flagged            -> flag icon
        unrevealed                    -> gray square

        """
        if self.detonated:
            self.draw_detonated_mine()
        elif self.revealed and not self.flagged and not self.is_mine:
            self.draw_revealed_cell()
        elif self.revealed and not self.flagged and self.is_mine:
            self.draw_mine()
        elif self.revealed and self.flagged and self.is_mine:
            self.draw_flag()
        elif self.revealed and self.flagged and not self.is_mine:
            self.draw_mine_error()
        elif not self.revealed and self.flagged:
            self.draw_flag()
        else:
            self.draw_unrevealed_cell()


    def draw_detonated_mine(self):
        pygame.draw.rect(self.screen, (255,0,0), self.rect, 0)
        icon = pygame.sprite.Sprite() # create sprite
        icon_path = os.path.join(self.filepath, "assets/images/mine_red_32.png")
        icon.image = pygame.image.load(icon_path).convert() # load flagimage
        # place icon in center of cell
        inset = 8
        icon.rect = icon.image.get_rect() # use image extent values
        icon.rect.topleft = [self.rect.x + inset, self.rect.y + inset] # put the sprite in the top left corner
        self.screen.blit(icon.image, icon.rect)



    def draw_flag(self):
        # if flagged by user, draw flag sprite
        # cache flag sprite on first creation
        if self.flag_icon == None:
            self.flag_icon = pygame.sprite.Sprite() # create sprite
            icon_path = os.path.join(self.filepath, "assets/images/flag_32.png")
            self.flag_icon.image = pygame.image.load(icon_path).convert() # load flagimage
        # place flag in center of cell
        flag_inset = 8
        self.flag_icon.rect = self.flag_icon.image.get_rect() # use image extent values
        self.flag_icon.rect.topleft = [self.rect.x + flag_inset, self.rect.y + flag_inset] # put the ball in the top left corner
        self.screen.blit(self.flag_icon.image, self.flag_icon.rect)


    def draw_unrevealed_cell(self):
        # if not revealed, cell is gray with highlight and shadow
        pygame.draw.rect(self.screen, bg_gray, self.rect, 0)
        line_width = 2
        # horizontal bottom shadow
        pygame.draw.line(self.screen, bg_gray_dark,
                         (self.rect.x, self.rect.y + self.rect.height - line_width/2),
                         (self.rect.x + self.rect.width, self.rect.y + self.rect.height - line_width/2), line_width)
        # vertical right shadow
        pygame.draw.line(self.screen, bg_gray_dark,
                         (self.rect.x + self.rect.width - line_width/2, self.rect.y),
                         (self.rect.x + self.rect.width - line_width/2, self.rect.y + self.rect.height), line_width)
        # horizontal top highlight
        pygame.draw.line(self.screen, white,
                         (self.rect.x, self.rect.y + line_width/2 - 1),
                         (self.rect.x + self.rect.width - line_width, self.rect.y + line_width/2 - 1), line_width)
        # vertical left highlight
        pygame.draw.line(self.screen, white,
                         (self.rect.x + line_width/2 - 1, self.rect.y),
                         (self.rect.x + line_width/2 - 1, self.rect.y + self.rect.height - line_width), line_width)


    def draw_mine(self):
        if self.mine_icon == None:
            self.mine_icon = pygame.sprite.Sprite() # create sprite
            icon_path = os.path.join(self.filepath, "assets/images/mine_32.png")
            self.mine_icon.image = pygame.image.load(icon_path).convert() # load flagimage
        # place icon in center of cell
        inset = 8
        self.mine_icon.rect = self.mine_icon.image.get_rect() # use image extent values
        self.mine_icon.rect.topleft = [self.rect.x + inset, self.rect.y + inset] # put the sprite in the top left corner
        self.screen.blit(self.mine_icon.image, self.mine_icon.rect)


    def draw_revealed_cell(self):
        # all revealed cells get a solid bg rect
        pygame.draw.rect(self.screen, (170,170,170), self.rect, 0)
        # if the cell isn't flagged, is revealed and has neighbors, show the neighbor count
        if (self.is_mine == False) and (self.revealed == True) and (self.neighbors > 0) and not self.flagged:
            # font color is based on neighbor count
            font_color = black
            if self.neighbors == 1:
                font_color = blue
            if self.neighbors == 2:
                font_color = green
            if self.neighbors == 3:
                font_color = red
            if self.neighbors == 4:
                font_color = purple
            font_size = 22
            text_inset = 5
            label_text = "%d" % (self.neighbors)
            label_font = pygame.font.SysFont('Arial', font_size)
            label = label_font.render(label_text, 1, font_color)
            self.screen.blit(label, (self.rect.x + text_inset, self.rect.y + text_inset))

    def draw_mine_error(self):
        icon = pygame.sprite.Sprite() # create sprite
        icon_path = os.path.join(self.filepath, "assets/images/mine_x_32.png")
        icon.image = pygame.image.load(icon_path).convert() # load flagimage
        # place icon in center of cell
        inset = 8
        icon.rect = icon.image.get_rect() # use image extent values
        icon.rect.topleft = [self.rect.x + inset, self.rect.y + inset] # put the sprite in the top left corner
        self.screen.blit(icon.image, icon.rect)



    def __str__(self):
        return "Cell[%d][%d]: Mine - %r, Mines Nearby - %d" % (self.row, self.col, self.is_mine, self.neighbors)


