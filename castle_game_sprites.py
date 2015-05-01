import pygame
from pygame.locals import *

# ===========
# UI elements
# ===========
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

class Cursor(pygame.sprite.Sprite):
    def __init__(self, color, coord, width): 
        pygame.sprite.Sprite.__init__(self)
        minx = coord[0]
        maxx = coord[1]
        miny = coord[2]
        maxy = coord[3]
        cursor_width = maxx - minx
        cursor_height = maxy - miny
        cursor_coverage = 0.25 # the percentage of each size that the cursor covers  
        cursor_cover_width = cursor_coverage * cursor_width
        cursor_cover_height = cursor_coverage * cursor_height
        rect_coords = [
                        [minx - width, minx, miny - width, miny + cursor_coverage * cursor_height],
                        [minx, minx + cursor_cover_width, miny - width, miny],
                        [maxx - cursor_cover_width, maxx + width, miny - width, miny],
                        [maxx, maxx + width, miny, miny + cursor_coverage * cursor_height],
                        [maxx, maxx + width, maxy - cursor_coverage * cursor_height, maxy + width],
                        [maxx - cursor_cover_width, maxx, maxy, maxy + width],
                        [minx - width, minx + cursor_cover_width, maxy, maxy + width],
                        [minx - width, minx, maxy - cursor_coverage * cursor_height, maxy]
                      ]
        self.images = []
        for rect_coord in rect_coords:
            w = int(round(rect_coord[1] - rect_coord[0]))
            h = int(round(rect_coord[3] - rect_coord[2]))
            new_image = pygame.Surface([w, h])
            new_image.fill(color)
            new_rect = new_image.get_rect()
            new_rect.centerx = (rect_coord[0] + rect_coord[1]) / 2
            new_rect.centery = (rect_coord[2] + rect_coord[3]) / 2
            self.images.append([new_image, new_rect])

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


class SelectionBox(pygame.sprite.Sprite):
    def __init__(self, game_ui):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.Surface((0, 0)) # default surface
        self.rect = self.image.get_rect()

# =======================
# Sprites for actual game
# =======================
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
