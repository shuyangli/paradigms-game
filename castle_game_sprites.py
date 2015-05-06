import pygame
from pygame.locals import *

import math

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
    ANIMATION_PERIOD = 20

    def __init__(self, color, rect, width=5):
        pygame.sprite.Sprite.__init__(self)
        self.width = width
        self.color = color
        self.set_rect(rect)

        self._frame_count = 0

    def set_color(self, color):
        self.color = color
        self.set_rect(self.rect)

    def set_rect(self, rect):
        minx = 0
        maxx = rect.width + self.width
        miny = 0
        maxy = rect.height + self.width
        cursor_coverage = 0.25 # the percentage of each size that the cursor covers
        border_length = round(cursor_coverage * rect.width + self.width)
        border_height = round(cursor_coverage * rect.height + self.width)

        self._image = pygame.Surface((rect.width + 2 * self.width, rect.height + 2 * self.width), pygame.SRCALPHA, 32).convert_alpha()

        # (x, y, w, h)
        rect_coords = [(minx, miny, self.width, border_height),
                        (minx, maxy + self.width - border_height, self.width, border_height),
                        (maxx, miny, self.width, border_height),
                        (maxx, maxy + self.width - border_height, self.width, border_height),

                        (minx, miny, border_length, self.width),
                        (maxx + self.width - border_length, miny, border_length, self.width),
                        (minx, maxy, border_length, self.width),
                        (maxx + self.width - border_length, maxy, border_length, self.width)]

        for (x, y, w, h) in rect_coords:
            new_image = pygame.Surface((w, h))
            new_image.fill(self.color)
            new_image_rect = new_image.get_rect()
            new_image_rect.left = x
            new_image_rect.top = y
            self._image.blit(new_image, new_image_rect)

        self._canonical_rect = self._image.get_rect()
        self._canonical_rect.center = rect.center

    def update(self):
        self._frame_count = (self._frame_count + 1) % self.ANIMATION_PERIOD

    @property
    def image(self):
        scale_factor = 1.0
        if self._frame_count < 10:
            scale_factor = 0.95 + 0.01 * self._frame_count
        else:
            scale_factor = 1.15 - 0.01 * self._frame_count

        new_image = pygame.transform.scale(self._image, (int(self._canonical_rect.width * scale_factor), int(self._canonical_rect.height * scale_factor)))
        self._rect = new_image.get_rect()
        self._rect.center = self._canonical_rect.center
        return new_image

    @property
    def rect(self):
        return self._rect

    # draw onto image
    def draw(self, surface):
        surface.blit(self.image, self.rect)


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


class InstructionLabel(pygame.sprite.Sprite):
    FONT_NAME = None
    FONT_SIZE = 26
    LABEL_COLORS = [(118, 66, 200), (192, 62, 62), (39, 190, 173), (200, 146, 37)]

    def __init__(self, pos, centerx, centery):
        pygame.sprite.Sprite.__init__(self)

        label_font = pygame.font.Font(self.FONT_NAME, self.FONT_SIZE)
        label_color = self.LABEL_COLORS[pos]

        # Positioning
        house_img = House.HOUSE_IMG[pos]
        house_rect = house_img.get_rect()
        house_rect.left = 0
        house_rect.centery = 26

        market_img = Market.MARKET_IMG[pos]
        market_rect = market_img.get_rect()
        market_rect.centery = 26

        tower_img = Tower.TOWER_IMG[pos]
        tower_rect = tower_img.get_rect()
        tower_rect.centery = 26

        left = house_img.get_rect().width + 10
        house_key = BasicLabel("a: House", label_font, label_color, topleft=(left, 0))
        house_money = BasicLabel("$100", label_font, label_color, topleft=(left, 30))

        left += house_key.rect.width + 10
        market_rect.left = left
        left += market_img.get_rect().width + 10
        market_key = BasicLabel("s: Market", label_font, label_color, topleft=(left, 0))
        market_money = BasicLabel("$50", label_font, label_color, topleft=(left, 30))

        left += market_key.rect.width + 10
        tower_rect.left = left
        left += tower_img.get_rect().width + 10
        tower_key = BasicLabel("d: Tower", label_font, label_color, topleft=(left, 0))
        tower_money = BasicLabel("$100", label_font, label_color, topleft=(left, 30))

        left += tower_key.rect.width

        self.image = pygame.Surface((left, 60), pygame.SRCALPHA, 32).convert_alpha()
        self.image.blit(house_img, house_rect)
        self.image.blit(house_key.image, house_key.rect)
        self.image.blit(house_money.image, house_money.rect)
        self.image.blit(market_img, market_rect)
        self.image.blit(market_key.image, market_key.rect)
        self.image.blit(market_money.image, market_money.rect)
        self.image.blit(tower_img, tower_rect)
        self.image.blit(tower_key.image, tower_key.rect)
        self.image.blit(tower_money.image, tower_money.rect)

        self.rect = self.image.get_rect()
        self.rect.centerx = centerx
        self.rect.centery = centery


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
    DEFAULT_PRICE = 100

    def __init__(self, game, player, _image, grid, max_hp=None, price=None):
        pygame.sprite.Sprite.__init__(self)
        self.player = player
        self.game = game
        self.grid = grid
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
        self.hp = self.max_hp

        if price is None:
            self.price = self.DEFAULT_PRICE
        else:
            self.price = price

        self.state = self.STATE_BUILDING

    def update(self):
        # called every ui frame for animation
        self._ui_frame_count = (self._ui_frame_count + 1) % 28

    def tick_lock_step(self):
        pass

    def isOwnedBy(self, player_pos):
        return self.player.pos == player_pos

    # ======
    # Events
    # ======
    def destroyed(self):
        self.player.remove_building(self)

    def hit_by_soldier(self, soldier):
        if soldier.player.pos != self.owner:
            # cause damange if the building and the soldier are different
            self.hp -= soldier.damage
            if self.hp < 0:
                self.destroyed()

        # but kill the soldier anyways
        soldier.die()

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

        if self.hp < self.max_hp:
            # TODO: hp not full, we also blit a hp bar
            pass

        return img

    @property
    def rect(self):
        return self._rect


class Castle(BasicBuilding):
    CASTLE_CYAN = pygame.image.load("assets/img/castle-cyan.png")
    CASTLE_PINK = pygame.image.load("assets/img/castle-pink.png")
    CASTLE_ORANGE = pygame.image.load("assets/img/castle-orange.png")
    CASTLE_PURPLE = pygame.image.load("assets/img/castle-purple.png")
    CASTLE_IMG = [CASTLE_PURPLE, CASTLE_PINK, CASTLE_CYAN, CASTLE_ORANGE]

    def __init__(self, game, player, grid):
        BasicBuilding.__init__(self, game, player, self.CASTLE_IMG[player.pos], grid, max_hp=200)
        self.state = self.STATE_READY

    # =================
    # Ticking mechanism
    # =================
    def update(self):
        pass

    def isOwnedBy(self, player_pos):
        return self.player.pos == player_pos


class House(BasicBuilding):
    HOUSE_CYAN = pygame.image.load("assets/img/house-cyan.png")
    HOUSE_PINK = pygame.image.load("assets/img/house-pink.png")
    HOUSE_ORANGE = pygame.image.load("assets/img/house-orange.png")
    HOUSE_PURPLE = pygame.image.load("assets/img/house-purple.png")
    HOUSE_IMG = [HOUSE_PURPLE, HOUSE_PINK, HOUSE_CYAN, HOUSE_ORANGE]

    COUNT_BUILDING_TO_READY = 5 * GAME_FRAMES_PER_LOCK_STEP
    COUNT_COOLDOWN_TO_READY = 3 * GAME_FRAMES_PER_LOCK_STEP
    step_count = 0

    COLOR_DARK_CYAN = (39, 190, 173)
    COLOR_DARK_PINK = (192, 62, 62)
    COLOR_DARK_ORANGE = (200, 146, 37)
    COLOR_DARK_PURPLE = (118, 66, 200)
    COLORS = [COLOR_DARK_PURPLE, COLOR_DARK_PINK, COLOR_DARK_CYAN, COLOR_DARK_ORANGE] # TODO: Weird color order

    ROUTE_UP = 1
    ROUTE_DOWN = 2
    ROUTE_LEFT = 3
    ROUTE_RIGHT = 4
    ROUTE_CANCEL = 5

    def __init__(self, game, player, grid):
        BasicBuilding.__init__(self, game, player, self.HOUSE_IMG[player.pos], grid)
        self.isRouting = False
        self.prev_x = None # default of the end point of previous route
        self.prev_y = None
        self.path = None
        self.path_dim = [] # used for pickling of the path object
        self.dir_list = [] # list of directions
        self.color = self.COLORS[player.pos]

    def reload_path_from_dimensions(self, path_dim):
        self.path = Path()
        for section in path_dim:
            new_section = PathSection(*section)
            self.path.pathSections.append(new_section)

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
    def route(self, direction, x, y): # TODO: reformat this stupid function
        if not self.isRouting:
            self.path = Path()
            self.isRouting = True
            self.prev_x = 225 + 50 * x # TODO: change this so that it's not hard-coded
            self.prev_y = 75 + 50 * y
            self.dir_list = [ 0 ]
            self.path_dim = []
        else:
            if direction == self.ROUTE_CANCEL:
                self.path = None
                self.path_dim = []
                self.prev_x = None
                self.prev_y = None
                self.dir_list = []
                self.isRouting = False
                return
            if 225 + 50 * x == self.prev_x and 75 + 50 * y == self.prev_y: return # check boundaries
            if direction == self.ROUTE_UP:
                if self.dir_list[-1] == self.ROUTE_DOWN:
                    self.prev_x = self.path.pathSections[-1].x1
                    self.prev_y = self.path.pathSections[-1].y1
                    self.path.popBackPathSection()
                    self.path_dim.pop(-1)
                    self.dir_list.pop(-1)
                else:
                    self.path_dim.append((self.color, self.prev_x, self.prev_y, self.prev_x, self.prev_y - 50, 4))
                    new_path = PathSection(self.color, self.prev_x, self.prev_y, self.prev_x, self.prev_y - 50, 4)
                    self.prev_y = self.prev_y - 50
                    self.path.pushBackPathSection(new_path)
                    self.dir_list.append(direction)
            elif direction == self.ROUTE_DOWN:
                if self.dir_list[-1] == self.ROUTE_UP:
                    self.prev_x = self.path.pathSections[-1].x1
                    self.prev_y = self.path.pathSections[-1].y1
                    self.path.popBackPathSection()
                    self.path_dim.pop(-1)
                    self.dir_list.pop(-1)
                else:
                    self.path_dim.append((self.color, self.prev_x, self.prev_y, self.prev_x, self.prev_y + 50, 4))
                    new_path = PathSection(self.color, self.prev_x, self.prev_y, self.prev_x, self.prev_y + 50, 4)
                    self.prev_y = self.prev_y + 50
                    self.path.pushBackPathSection(new_path)
                    self.dir_list.append(direction)
            elif direction == self.ROUTE_LEFT:
                if self.dir_list[-1] == self.ROUTE_RIGHT:
                    self.prev_x = self.path.pathSections[-1].x1
                    self.prev_y = self.path.pathSections[-1].y1
                    self.path.popBackPathSection()
                    self.path_dim.pop(-1)
                    self.dir_list.pop(-1)
                else:
                    self.path_dim.append((self.color, self.prev_x, self.prev_y, self.prev_x - 50, self.prev_y, 4))
                    new_path = PathSection(self.color, self.prev_x, self.prev_y, self.prev_x - 50, self.prev_y, 4)
                    self.prev_x = self.prev_x - 50
                    self.path.pushBackPathSection(new_path)
                    self.dir_list.append(direction)
            elif direction == self.ROUTE_RIGHT:
                if self.dir_list[-1] == self.ROUTE_LEFT:
                    self.prev_x = self.path.pathSections[-1].x1
                    self.prev_y = self.path.pathSections[-1].y1
                    self.path.popBackPathSection()
                    self.path_dim.pop(-1)
                    self.dir_list.pop(-1)
                else:
                    self.path_dim.append((self.color, self.prev_x, self.prev_y, self.prev_x + 50, self.prev_y, 4))
                    new_path = PathSection(self.color, self.prev_x, self.prev_y, self.prev_x + 50, self.prev_y, 4)
                    self.prev_x = self.prev_x + 50
                    self.path.pushBackPathSection(new_path)
                    self.dir_list.append(direction)
            building_at_new_pos = self.game.grid_for_coordinates(self.prev_x, self.prev_y).building
            if building_at_new_pos != None and not building_at_new_pos.isOwnedBy(self.player.pos):
                self.isRouting = False
                self.path.destination = building_at_new_pos


    def train_soldier(self):
        # TODO: Create a soldier
        pass

    def destroyed(self):
        # TODO: Remove all soldiers
        super(House, self).destroyed()
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

    COUNT_BUILDING_TO_READY = 5 * GAME_FRAMES_PER_LOCK_STEP
    COUNT_COOLDOWN_TO_READY = 5 * GAME_FRAMES_PER_LOCK_STEP
    step_count = 0

    def __init__(self, game, player, grid):
        BasicBuilding.__init__(self, game, player, self.TOWER_IMG[player.pos], grid)

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

    COUNT_BUILDING_TO_READY = 5 * GAME_FRAMES_PER_LOCK_STEP
    step_count = 0

    MONEY_INCREMENT = 5

    def __init__(self, game, player, grid):
        BasicBuilding.__init__(self, game, player, self.MARKET_IMG[player.pos], grid, price=50)

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
        super(Market, self).destroyed()
        self.player.money_increment -= self.MONEY_INCREMENT


class Soldier(pygame.sprite.Sprite):
    SOLDIER_CYAN = pygame.image.load("assets/img/soldier-cyan.png")
    SOLDIER_PINK = pygame.image.load("assets/img/soldier-pink.png")
    SOLDIER_ORANGE = pygame.image.load("assets/img/soldier-orange.png")
    SOLDIER_PURPLE = pygame.image.load("assets/img/soldier-purple.png")

    SOLDIER_IMG = [SOLDIER_PURPLE, SOLDIER_PINK, SOLDIER_CYAN, SOLDIER_ORANGE]

    SPEED = 2


    def __init__(self, house, game, player):
        pygame.sprite.Sprite.__init__(self)
        self.player = player
        self.house = house
        self.game = game
        self._image = self.SOLDIER_IMG[player.pos]

        # Initially it's located at the house
        self.current_grid = self.house.grid
        self._canonical_rect = self._image.get_rect()
        self.current_x = self.house.rect.centerx
        self.current_y = self.house.rect.centery

    # Movement per UI frame
    def update(self):
        # TODO: get current destination: (x, y)
        destination = (None, None)

        if destination is not None:
            # move towards destination
            if abs(destination[0] - self.current_x) >= self.SPEED:
                self.current_x += math.copysign(self.SPEED, destination[0] - self.current_x)
            else:
                self.current_x = destination[0]
            if abs(destination[1] - self.current_y) >= self.SPEED:
                self.current_y += math.copysign(self.SPEED, destination[1] - self.current_y)
            else:
                self.current_y = destination[1]

        # check collision with grid
        current_grid = self.game.grid_for_coordinates(self.current_x, self.current_y)
        if current_grid != self.current_grid:
            # TODO: remove soldier from the previous grid, and install it in the new grid
            # this is for easy tower attacking
            pass

        if current_grid.building is not None:
            # hit building
            current_grid.building.hit_by_soldier(self)

    # ======
    # Events
    # ======
    def die(self):
        # TODO: make it disappear
        pass


    @property
    def image(self):
        return self._image

    @property
    def rect(self):
        rect = self._canonical_rect
        rect.center = (self.current_x, self.current_y)
        return rect


class Path(pygame.sprite.Sprite):
    def __init__(self):
        pygame.sprite.Sprite.__init__(self)
        self.destination = None
        self.pathSections = []

    def pushBackPathSection(self, pathSection):
        self.pathSections.append(pathSection)

    def popBackPathSection(self):
        self.pathSections.pop(-1)

    def setDestination(self, enemy_building):
        self.destination = enemy_building


class PathSection(pygame.sprite.Sprite):
    def __init__(self, color, x1, y1, x2, y2, width):
        pygame.sprite.Sprite.__init__(self)
        self.x1 = x1
        self.y1 = y1
        self.x2 = x2
        self.y2 = y2

        # drawing
        self.image = None
        if self.x1 == self.x2: # vertical
            self.image = pygame.Surface([width, abs(self.y2 - self.y1)])
        elif self.y1 == self.y2: # horizontal
            self.image = pygame.Surface([abs(self.x2 - self.x1), width])
        else: return
        self.image.fill(color)
        self.rect = self.image.get_rect()
        self.rect.centerx = (self.x1 + self.x2) / 2
        self.rect.centery = (self.y1 + self.y2) / 2

