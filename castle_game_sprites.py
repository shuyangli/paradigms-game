import pygame
from pygame.locals import *

class BasicLabel(pygame.sprite.Sprite):
    def __init__(self, game_ui, text, color, antialias=True, **kwargs):
        # kwargs: centerx, ypos
        pygame.sprite.Sprite.__init__(self)
        self.image = game_ui.font.render(text, antialias, color)
        self.rect = self.image.get_rect()

        # process kwargs
        if "centerx" in kwargs:
            if kwargs["centerx"] == "center":
                self.rect.centerx = game_ui.screen.get_rect().centerx
            else:
                self.rect.centerx = kwargs["centerx"]

        if "centery" in kwargs:
            if kwargs["centery"] == "center":
                self.rect.centery = game_ui.screen.get_rect().centery
            else:
                self.rect.centery = kwargs["centery"]

class Rect(pygame.sprite.Sprite):
    def __init__(self, color, minx, maxx, miny, maxy):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.Surface([maxx - minx, maxy - miny])
        self.image.fill(color)
        self.rect = self.image.get_rect()
        self.rect.centerx = (minx + maxx) / 2
        self.rect.centery = (miny + maxy) / 2