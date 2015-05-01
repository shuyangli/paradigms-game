import pygame
from pygame.locals import *

class BasicLabel(pygame.sprite.Sprite):
    def __init__(self, game_ui, text, color, antialias=True, **kwargs):
        # kwargs: centerx, ypos
        pygame.sprite.Sprite.__init__(self)
        self.game_ui = game_ui
        self.image = self.game_ui.font.render(text, antialias, color)
        self.rect = self.image.get_rect()

        # process kwargs
        if "centerx" in kwargs:
            if kwargs["centerx"] == "center":
                self.rect.centerx = self.game_ui.screen.get_rect().centerx
            else:
                self.rect.centerx = kwargs["centerx"]

        if "centery" in kwargs:
            if kwargs["centery"] == "center":
                self.rect.centery = self.game_ui.screen.get_rect().centery
            else:
                self.rect.centery = kwargs["centery"]


class Rect(pygame.sprite.Sprite):
    def __init__(self, color, coord): # coord: (minx, maxx, miny, maxy)
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.Surface([coord[1] - coord[0], coord[3] - coord[2]])
        self.image.fill(color)
        self.rect = self.image.get_rect()
        self.rect.centerx = (coord[0] + coord[1]) / 2
        self.rect.centery = (coord[2] + coord[3]) / 2


class BasicArrow(pygame.sprite.Sprite):
    def __init__(self, game_ui, positions=None):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.image.load("assets/img/arrow-right.png")
        self.image = pygame.transform.scale(self.image, (50, 50))
        self.rect = self.image.get_rect()
        self.positions = positions

    def update_selection(self, selection):
        self.rect.x = self.positions[selection][0]
        self.rect.centery = self.positions[selection][1]

# Sprites for actual game
class EmptySquare(pygame.sprite.Sprite):
    def __init__(self):
        pygame.sprite.Sprite.__init__(self)


class Castle(pygame.sprite.Sprite):
    def __init__(self):
        pygame.sprite.Sprite.__init__(self)


class House(pygame.sprite.Sprite):
    def __init__(self):
        pygame.sprite.Sprite.__init__(self)


class Tower(pygame.sprite.Sprite):
    def __init__(self):
        pygame.sprite.Sprite.__init__(self)


class Market(pygame.sprite.Sprite):
    def __init__(self):
        pygame.sprite.Sprite.__init__(self)
