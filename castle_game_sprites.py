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
    def __init__(self, text, font, color, antialias=True, **kwargs):
        # kwargs: centerx, ypos
        pygame.sprite.Sprite.__init__(self)
        self.image = font.render(text, antialias, color)
        self.rect = self.image.get_rect()

        # process kwargs
        if "centerx" in kwargs:
            self.rect.centerx = kwargs["centerx"]
        if "centery" in kwargs:
            self.rect.centery = kwargs["centery"]
        if "topright" in kwargs:
            self.rect.topright = kwargs["topright"]
        if "topleft" in kwargs:
            self.rect.topleft = kwargs["topleft"]
        if "bottomright" in kwargs:
            self.rect.bottomright = kwargs["bottomright"]
        if "bottomleft" in kwargs:
            self.rect.bottomleft = kwargs["bottomleft"]


class Rect(pygame.sprite.Sprite):
    def __init__(self, color, coord): # coord: (minx, maxx, miny, maxy)
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.Surface([coord[1] - coord[0], coord[3] - coord[2]])
        self.image.fill(color)
        self.rect = self.image.get_rect()
        self.rect.centerx = (coord[0] + coord[1]) / 2
        self.rect.centery = (coord[2] + coord[3]) / 2

    def set_color(self, color):
        self.image.fill(color)


class Cursor(pygame.sprite.Sprite):
    def __init__(self, color, rect, width=5):
        pygame.sprite.Sprite.__init__(self)
        self.width = width
        self.color = color
        self.rect = rect
        self.set_rect(rect)

    def set_color(self, color):
        self.color = color
        self.set_rect(self.rect)

    def set_rect(self, rect):
        minx = rect.left
        maxx = rect.right
        miny = rect.top
        maxy = rect.bottom
        cursor_coverage = 0.25 # the percentage of each size that the cursor covers
        cursor_cover_width = cursor_coverage * rect.width
        cursor_cover_height = cursor_coverage * rect.height
        rect_coords = [
            [minx - self.width, minx, miny - self.width, miny + cursor_coverage * rect.height],
            [minx, minx + cursor_cover_width, miny - self.width, miny],
            [maxx - cursor_cover_width, maxx + self.width, miny - self.width, miny],
            [maxx, maxx + self.width, miny, miny + cursor_coverage * rect.height],
            [maxx, maxx + self.width, maxy - cursor_coverage * rect.height, maxy + self.width],
            [maxx - cursor_cover_width, maxx, maxy, maxy + self.width],
            [minx - self.width, minx + cursor_cover_width, maxy, maxy + self.width],
            [minx - self.width, minx, maxy - cursor_coverage * rect.height, maxy]
                      ]
        self.images = []
        for rect_coord in rect_coords:
            w = int(round(rect_coord[1] - rect_coord[0]))
            h = int(round(rect_coord[3] - rect_coord[2]))
            new_image = pygame.Surface([w, h])
            new_image.fill(self.color)
            new_rect = new_image.get_rect()
            new_rect.centerx = (rect_coord[0] + rect_coord[1]) / 2
            new_rect.centery = (rect_coord[2] + rect_coord[3]) / 2
            self.images.append((new_image, new_rect))

        # draw onto image
    def draw(self, surface):
        for img, rect in self.images:
            surface.blit(img, rect)


class SelectionBox(pygame.sprite.Sprite):
    def __init__(self, game_ui):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.Surface((0, 0)) # default surface
        self.rect = self.image.get_rect()

class PlayerCastle(pygame.sprite.Sprite):
    CASTLE_CYAN = pygame.image.load("assets/img/castle-cyan-large.png")
    CASTLE_PINK = pygame.image.load("assets/img/castle-pink-large.png")
    CASTLE_ORANGE = pygame.image.load("assets/img/castle-orange-large.png")
    CASTLE_PURPLE = pygame.image.load("assets/img/castle-purple-large.png")

    CASTLE_IMG = [CASTLE_PURPLE, CASTLE_PINK, CASTLE_CYAN, CASTLE_ORANGE]

    def __init__(self, pos, rect):
        pygame.sprite.Sprite.__init__(self)

        self.pos = pos
        self.w = int(rect.width * 0.8)
        self.h = int(rect.height * 0.8)
        self.rect = self.image.get_rect()
        self.rect.centerx = rect.centerx
        self.rect.centery = rect.centery

    @property
    def image(self):
        return pygame.transform.scale(self.CASTLE_IMG[self.pos], (self.w, self.h))


# =======================
# Sprites for actual game
# =======================
GAME_FRAMES_PER_LOCK_STEP = 5

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
            surface.blit(self.building.image, self.building.rect)

    def _set_owner(self, owner):
        self.owners = [owner]

    def add_owner(self, owner):
        self.owners.append(owner)

    def _set_building(self, building):
        self.building = building

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


class BasicBuilding(pygame.sprite.Sprite):
    HAMMER_CYAN = pygame.image.load("assets/img/hammer-cyan.png")
    HAMMER_PINK = pygame.image.load("assets/img/hammer-pink.png")
    HAMMER_ORANGE = pygame.image.load("assets/img/hammer-orange.png")
    HAMMER_PURPLE = pygame.image.load("assets/img/hammer-purple.png")
    HAMMER_IMG = [HAMMER_PURPLE, HAMMER_PINK, HAMMER_CYAN, HAMMER_ORANGE]

    STATE_BUILDING = 0
    STATE_READY = 1
    STATE_COOLDOWN = 2

    COUNT_BUILDING_TO_READY = 5
    COUNT_COOLDOWN_TO_READY = 3

    MAX_HP = 100

    def __init__(self, player, _image, grid, max_hp=None):
        pygame.sprite.Sprite.__init__(self)
        self.player = player
        self._image = _image
        self._hammer_image = self.HAMMER_IMG[player.pos]
        self._rect = self._image.get_rect()
        self._rect.center = grid.rect.center
        self._ui_frame_count = 0

        self.owner = player.pos

        # Game data
        if max_hp is None:
            self.max_hp = self.MAX_HP
        else:
            self.max_hp = max_hp
        self.state = self.STATE_BUILDING

        # Add to player
        self.player.add_building(self)


    def update(self):
        # called every ui frame for animation
        self._ui_frame_count += 1
        if self._ui_frame_count >= 28:
            self._ui_frame_count = 0

    def tick_lock_step(self):
        pass

    def destroyed(self):
        pass

    @property
    def image(self):
        base_rect = self._image.get_rect()
        img = pygame.Surface((base_rect.width, base_rect.height), pygame.SRCALPHA, 32).convert_alpha()
        img.blit(self._image, base_rect)

        if self.state == self.STATE_BUILDING:
            # building state, we also blit a hammer
            rotated = None
            if self._ui_frame_count >= 14:
                rotated = pygame.transform.rotate(self._hammer_image, 98 - self._ui_frame_count * 3.5)
            else:
                rotated = pygame.transform.rotate(self._hammer_image, self._ui_frame_count * 3.5)

            rotated_rect = rotated.get_rect()
            rotated_rect.center = base_rect.center
            img.blit(rotated, rotated_rect)

        return img

    @property
    def rect(self):
        return self._rect


class Castle(pygame.sprite.Sprite):
    CASTLE_CYAN = pygame.image.load("assets/img/castle-cyan.png")
    CASTLE_PINK = pygame.image.load("assets/img/castle-pink.png")
    CASTLE_ORANGE = pygame.image.load("assets/img/castle-orange.png")
    CASTLE_PURPLE = pygame.image.load("assets/img/castle-purple.png")
    CASTLE_IMG = [CASTLE_PURPLE, CASTLE_PINK, CASTLE_CYAN, CASTLE_ORANGE]

    def __init__(self, player, grid):
        self.owner = player.pos
        self.grid = grid
        self.image = self.CASTLE_IMG[self.owner]
        self.rect = self.image.get_rect()
        self.rect.center = self.grid.rect.center

    # =================
    # Ticking mechanism
    # =================
    def update(self):
        pass


class House(BasicBuilding):
    HOUSE_CYAN = pygame.image.load("assets/img/house-cyan.png")
    HOUSE_PINK = pygame.image.load("assets/img/house-pink.png")
    HOUSE_ORANGE = pygame.image.load("assets/img/house-orange.png")
    HOUSE_PURPLE = pygame.image.load("assets/img/house-purple.png")
    HOUSE_IMG = [HOUSE_PURPLE, HOUSE_PINK, HOUSE_CYAN, HOUSE_ORANGE]

    COUNT_BUILDING_TO_READY = 5
    COUNT_COOLDOWN_TO_READY = 3
    step_count = 0

    def __init__(self, player, grid):
        BasicBuilding.__init__(self, player, self.HOUSE_IMG[player.pos], grid)

    # =================
    # Ticking mechanism
    # =================
    def tick_lock_step(self):
        # called every lockstep for game logic
        if self.state == self.STATE_BUILDING:
            # count states
            self.step_count += 1
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
        # TODO: Remove all soldiers
        pass


class Tower(BasicBuilding):
    TOWER_CYAN = pygame.image.load("assets/img/tower-cyan.png")
    TOWER_PINK = pygame.image.load("assets/img/tower-pink.png")
    TOWER_ORANGE = pygame.image.load("assets/img/tower-orange.png")
    TOWER_PURPLE = pygame.image.load("assets/img/tower-purple.png")
    TOWER_IMG = [TOWER_PURPLE, TOWER_PINK, TOWER_CYAN, TOWER_ORANGE]

    STATE_BUILDING = 0
    STATE_READY = 1
    STATE_COOLDOWN = 2

    COUNT_BUILDING_TO_READY = 5
    COUNT_COOLDOWN_TO_READY = 5
    step_count = 0

    def __init__(self, player, grid):
        BasicBuilding.__init__(self, player, self.TOWER_IMG[player.pos], grid)

    # =================
    # Ticking mechanism
    # =================
    def tick_lock_step(self):
        # called every lockstep for game logic
        if self.state == self.STATE_BUILDING:
            # count states
            self.step_count += 1
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


class Market(BasicBuilding):
    MARKET_CYAN = pygame.image.load("assets/img/market-cyan.png")
    MARKET_PINK = pygame.image.load("assets/img/market-pink.png")
    MARKET_ORANGE = pygame.image.load("assets/img/market-orange.png")
    MARKET_PURPLE = pygame.image.load("assets/img/market-purple.png")
    MARKET_IMG = [MARKET_PURPLE, MARKET_PINK, MARKET_CYAN, MARKET_ORANGE]

    STATE_BUILDING = 0
    STATE_READY = 1

    COUNT_BUILDING_TO_READY = 5
    step_count = 0

    MONEY_INCREMENT = 5

    def __init__(self, player, grid):
        BasicBuilding.__init__(self, player, self.MARKET_IMG[player.pos], grid)

    # =================
    # Ticking mechanism
    # =================
    def tick_lock_step(self):
        # called every lockstep for game logic
        if self.state == self.STATE_BUILDING:
            # count states
            self.step_count += 1
            if self.step_count == self.COUNT_BUILDING_TO_READY:
                # transition
                self.step_count = 0
                self.state = self.STATE_READY
                self.player.money_increment += self.MONEY_INCREMENT

    def destroyed(self):
        self.player.money_increment -= self.MONEY_INCREMENT


class Soldier(pygame.sprite.Sprite):
    def __init__(self, game_model, game_player):
        pygame.sprite.Sprite.__init__(self)


class Path(pygame.sprite.Sprite):
    def __init__(self):
        pygame.sprite.Sprite.__init__(self)
        self.destination = None
        self.pathSections = []
"""
    def onWhichPathSection(self, soldier):
        for pathSection in self.pathSections:
            if pathSection.passesPoint(soldier.x, soldier.y):
                return pathSection
        return None

    def whereToGo(self, soldier):
        return None
"""

class PathSection(pygame.sprite.Sprite):
    def __init__(self, color, start_x, start_y, end_x, end_y, width):
        pygame.sprite.Sprite.__init__(self)
        self.start_x = start_x
        self.start_y = start_y
        self.end_x = end_x
        self.end_y = end_y

        self.image = None
        if self.start_x == self.end_x: # vertical
            self.image = pygame.Surface([width, abs(self.end_y - self.start_y)])
        elif self.start_y == self.end_y: # horizontal
            self.image = pygame.Surface([abs(self.end_x - self.start_x), width])
        self.image.fill(color)
        self.rect = self.image.get_rect()
        self.rect.centerx = (start_x + start_y) / 2
        self.rect.centery = (end_x + end_y) / 2
        self.next_from_start = []
        self.next_from_end = []

    def doesConnectEnemyBuilding(self):
        return False

    def passesPoint(self, x, y):
        return ((x == self.start_x and (y - self.start_y)*(y - self.end_y) <= 0) or
            (y == self.start_y and (x - self.start_x)*(x - self.end_x) <= 0))
