import pygame
from pygame.locals import *

PLAYER_NONE = -1
PLAYER_PURPLE = 0
PLAYER_PINK = 1
PLAYER_CYAN = 2
PLAYER_ORANGE = 3

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
GAME_FRAMES_PER_LOCK_STEP = 10

class BoardGrid(pygame.sprite.Sprite):
    GROUND_CYAN = pygame.image.load("assets/img/ground-cyan.png")
    GROUND_PINK = pygame.image.load("assets/img/ground-pink.png")
    GROUND_ORANGE = pygame.image.load("assets/img/ground-orange.png")
    GROUND_PURPLE = pygame.image.load("assets/img/ground-purple.png")
    GROUND_GREEN = pygame.image.load("assets/img/ground-green.png")

    GROUND_IMG = [GROUND_PURPLE, GROUND_PINK, GROUND_CYAN, GROUND_ORANGE, GROUND_GREEN]

    X_OFFSET = 200
    Y_OFFSET = 50
    WIDTH = 50
    HEIGHT = 50
    TRUE_WIDTH = 46
    TRUE_HEIGHT = 46

    def __init__(self, x, y):
        pygame.sprite.Sprite.__init__(self)
        self.owners = []
        self.building = None

        left = self.X_OFFSET + self.WIDTH * x + (self.WIDTH - self.TRUE_WIDTH) / 2
        top = self.Y_OFFSET + self.HEIGHT * y + (self.HEIGHT - self.TRUE_HEIGHT) / 2
        self.rect = pygame.Rect(left, top, self.TRUE_WIDTH, self.TRUE_HEIGHT)

    def draw(self, surface):
        # draw ground
        surface.blit(self.image, self.rect)
        # draw building
        if self.building is not None:
            surface.blit(self.building.image, self.rect)

    def _set_owner(self, owner):
        self.owners = [owner]

    def add_owner(self, owner):
        self.owners.append(owner)

    @property
    def owner(self):
        if self.building is None:
            if len(self.owners) > 0:
                return self.owners[-1]
            else:
                return PLAYER_NONE
        else:
            return self.building.owner

    @property
    def image(self):
        return self.GROUND_IMG[self.owner]


class Castle(pygame.sprite.Sprite):
    def __init__(self, image_path, coord): # coord: (minx, maxx, miny, maxy)
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.image.load(image_path)
        self.image = pygame.transform.scale(self.image,
            (coord[1] - coord[0], coord[3] - coord[2]))
        self.rect = self.image.get_rect()
        self.rect.centerx = (coord[0] + coord[1]) / 2
        self.rect.centery = (coord[2] + coord[3]) / 2

class House(pygame.sprite.Sprite):
    STATE_BUILDING = 0
    STATE_READY = 1
    STATE_COOLDOWN = 2

    COUNT_BUILDING_TO_READY = 5 * GAME_FRAMES_PER_LOCK_STEP
    COUNT_COOLDOWN_TO_READY = 3 * GAME_FRAMES_PER_LOCK_STEP
    step_count = 0

    def __init__(self, game_model, game_player):
        pygame.sprite.Sprite.__init__(self)
        self.game_model = game_model
        self.game_player = game_player
        self.state = self.STATE_BUILDING

    # =================
    # Ticking mechanism
    # =================
    def update(self):
        # called every ui frame for animation
        # update image
        pass

    def tick_lock_step(self):
        # called every lockstep for game logic
        if self.state == self.STATE_BUILDING:
            # count states
            if self.step_count == self.COUNT_BUILDING_TO_READY:
                # transition
                self.step_count = 0
                self.state = self.STATE_READY

        elif self.state == self.STATE_READY:
            self.train_soldier()

            # transition
            self.step_count = 0
            self.state = self.STATE_COOLDOWN

        elif self.state == self.STATE_COOLDOWN:
            # count states
            self.step_count += 1
            if self.step_count == self.COUNT_COOLDOWN_TO_READY:
                # transition
                self.step_count = 0
                self.state = self.STATE_READY

    # ======
    # Events
    # ======
    def train_soldier(self):
        pass

    def destroyed(self):
        pass



class Tower(pygame.sprite.Sprite):
    STATE_BUILDING = 0
    STATE_READY = 1
    STATE_COOLDOWN = 2

    COUNT_BUILDING_TO_READY = 5 * GAME_FRAMES_PER_LOCK_STEP
    COUNT_COOLDOWN_TO_READY = 5 * GAME_FRAMES_PER_LOCK_STEP
    step_count = 0

    def __init__(self, game_model, game_player):
        pygame.sprite.Sprite.__init__(self)
        self.game_model = game_model
        self.game_player = game_player
        self.state = self.STATE_BUILDING

    # =================
    # Ticking mechanism
    # =================
    def update(self):
        # called every ui frame for animation
        # update image
        pass

    def tick_lock_step(self):
        # called every lockstep for game logic
        if self.state == self.STATE_BUILDING:
            # count states
            if self.step_count == self.COUNT_BUILDING_TO_READY:
                # transition
                self.step_count = 0
                self.state = self.STATE_READY

        elif self.state == self.STATE_READY:
            if self.attack():
                # transition
                self.step_count = 0
                self.state = self.STATE_COOLDOWN

        elif self.state == self.STATE_COOLDOWN:
            # count states
            self.step_count += 1
            if self.step_count == self.COUNT_COOLDOWN_TO_READY:
                # transition
                self.step_count = 0
                self.state = self.STATE_READY

    # ======
    # Events
    # ======
    def attack(self):
        # TODO
        return False

    def destroyed(self):
        pass


class Market(pygame.sprite.Sprite):
    STATE_BUILDING = 0
    STATE_READY = 1

    COUNT_BUILDING_TO_READY = 5 * GAME_FRAMES_PER_LOCK_STEP
    step_count = 0

    MONEY_INCREMENT = 5

    def __init__(self, game_model, game_player):
        pygame.sprite.Sprite.__init__(self)
        self.game_model = game_model
        self.game_player = game_player
        self.state = self.STATE_BUILDING

    # =================
    # Ticking mechanism
    # =================
    def update(self):
        # called every ui frame for animation
        # update image
        pass

    def tick_lock_step(self):
        # called every lockstep for game logic
        if self.state == self.STATE_BUILDING:
            # count states
            if self.step_count == self.COUNT_BUILDING_TO_READY:
                # transition
                self.step_count = 0
                self.state = self.STATE_READY
                self.game_player.money_increment += self.MONEY_INCREMENT

    def destroyed(self):
        self.game_player.money_increment -= self.MONEY_INCREMENT


class Path(pygame.sprite.Sprite):
    def __init__(self, game_model, game_player):
        pygame.sprite.Sprite.__init__(self)


class PathSection(pygame.sprite.Sprite):
    def __init__(self, game_model, game_player, color, start_x, start_y, end_x, end_y, width):
        pygame.sprite.Sprite.__init__(self)
        self.game_model = game_model
        self.game_player = game_player
        self.start_x = start_x
        self.start_y = start_y
        self.end_x = end_x
        self.end_y = end_y
        self.image = pygame.Surface([coord[1] - coord[0], coord[3] - coord[2]])
        self.image.fill(color)
        self.rect = self.image.get_rect()
        self.rect.centerx = (start_x + start_y) / 2
        self.rect.centery = (end_x + end_y) / 2
        self.next_from_start = []
        self.next_from_end = []

    def isStartOrEnd(self, x, y): # 0 means (x, y) is the start point, 1 means end, -1 means neither
        if x == self.start_x and y == self.start_y: return 0
        if x == self.end_x and y == self.end_y: return 1
        return -1

    def connectPathSection(self, path_section):
        pass

    def disconnectPathSection(self, path_section):
        pass
