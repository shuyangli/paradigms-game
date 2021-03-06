import sys, os
import pygame
from pygame.locals import *
from pygame import font

from castle_game import CastleGameCommand, CastleGameModel
from castle_game_sprites import *

class CastleGameUI:
    """UI class for Castle game."""

    # screen size
    SCREEN_SIZE = (800, 600)
    FONT_NAME = None
    FONT_SIZE = 26

    # colors
    COLOR_WHITE = (255, 255, 255)
    COLOR_BLACK = (0, 0, 0)
    COLOR_YELLOW = (255, 255, 0)
    COLOR_GREEN = (0, 255, 0, 0.1)
    COLOR_RED = (255, 0, 0)
    COLOR_GREY = (84, 84, 84)
    # colors for castles
    COLOR_DARK_PURPLE = (118, 66, 200)
    COLOR_PURPLE = (144, 82, 245)
    COLOR_LIGHT_PURPLE = (235, 210, 252)
    COLOR_DARK_CYAN = (39, 190, 173)
    COLOR_CYAN = (50, 233, 213)
    COLOR_LIGHT_CYAN = (177, 254, 238)
    COLOR_DARK_PINK = (192, 62, 62)
    COLOR_PINK = (240, 74, 76)
    COLOR_LIGHT_PINK = (244, 182, 187)
    COLOR_DARK_ORANGE = (200, 146, 37)
    COLOR_ORANGE = (247, 184, 45)
    COLOR_LIGHT_ORANGE = (249, 243, 209)

    PLAYER_COLOR_LIGHT = [COLOR_LIGHT_PURPLE, COLOR_LIGHT_PINK, COLOR_LIGHT_CYAN, COLOR_LIGHT_ORANGE]
    PLAYER_COLOR_DARK = [COLOR_DARK_PURPLE, COLOR_DARK_PINK, COLOR_DARK_CYAN, COLOR_DARK_ORANGE]

    # route directions
    ROUTE_UP = 1
    ROUTE_DOWN = 2
    ROUTE_LEFT = 3
    ROUTE_RIGHT = 4
    ROUTE_CANCEL = 5

    def __init__(self, debug=False):
        # Init pygame
        self.init_pygame()

        global DEBUG
        DEBUG = debug

        # Init other aspects
        self.cursor_x = 0
        self.cursor_y = 0

        # Initial state
        self.transition_to_menu()


    def init_pygame(self):
        pygame.init()
        pygame.mixer.init(frequency=44100, size=16, channels=2, buffer=65536)
        self.screen = pygame.display.set_mode(self.SCREEN_SIZE)
        self.font = pygame.font.Font(self.FONT_NAME, self.FONT_SIZE)

        pygame.mixer.music.load("assets/sound/ice-cream-sandwich.ogg")
        pygame.mixer.music.play(-1, 0.0)


    def set_client(self, client):
        self.client = client

    def exit(self):
        pygame.mixer.music.stop()
        pygame.quit()
        self.client.exit()


    # ===================
    # Starting a new game
    # ===================
    def start_game(self, all_players_pos, current_player_pos):
        self.game_model = CastleGameModel(self, all_players_pos, current_player_pos, DEBUG)
        self.client.set_game_model(self.game_model)

    def end_game(self):
        self.client.set_game_model(None)
        self.game_model = None

    # =================
    # State transitions
    # =================
    def transition_to_menu(self):
        self.cursor_x = 0
        self.cursor_y = 0

        screen_centerx = self.screen.get_rect().centerx

        self.logo = pygame.image.load("assets/img/logo.png")
        self.logo_rect = self.logo.get_rect()
        self.logo_rect.centerx = screen_centerx
        self.logo_rect.centery = 150

        play_label = BasicLabel("PLAY", self.font, self.COLOR_BLACK, centerx=screen_centerx, centery=375)
        instr_label = BasicLabel("INSTRUCTIONS", self.font, self.COLOR_BLACK, centerx=screen_centerx, centery=425)
        exit_label = BasicLabel("QUIT", self.font, self.COLOR_BLACK, centerx=screen_centerx, centery=475)
        self.menu_label_group = pygame.sprite.Group(play_label, instr_label, exit_label)

        self.cursor = Cursor(self.COLOR_RED, play_label.rect, width=4)
        self.cursor_pos_menu = [play_label.rect, instr_label.rect, exit_label.rect]


    def transition_to_instructions(self):
        screen_centerx = self.screen.get_rect().centerx
        self.instr_screen = pygame.image.load("assets/img/instructions.png")


    def transition_to_waiting(self):
        self.cursor_x = 0
        self.cursor_y = 0

        self.ready_label = BasicLabel("READY", self.font, self.COLOR_BLACK, centerx=self.screen.get_rect().centerx, centery=525)
        self.ready_rect = Rect(self.COLOR_GREY, [250, 550, 475, 575])

        # minx, maxx, miny, maxy of the four rectangles for players to choose
        player_rect_coords = [[125, 225, 275, 375],
                            [275, 375, 275, 375],
                            [425, 525, 275, 375],
                            [575, 675, 275, 375]]
        self.player_rects = [Rect(self.COLOR_GREEN, player_rect_coords[i]) for i in range(4)]
        self.cursor = Cursor(self.COLOR_RED, self.player_rects[0].rect)


    def transition_to_ready(self):
        self.cursor_x = 0
        self.cursor_y = 1

        self.waiting_label = BasicLabel("WAITING FOR OPPONENTS ...", self.font, self.COLOR_BLACK, centerx=self.screen.get_rect().centerx, centery=525)


    def transition_to_playing(self):
        default_cursor_positions = [(0, 0), (0, 7), (7, 7), (7, 0)]
        self.cursor_y, self.cursor_x = default_cursor_positions[self.client.own_position]

        self.cursor = Cursor(self.PLAYER_COLOR_DARK[self.client.own_position], self.game_model.board[self.cursor_y][self.cursor_x].rect)

        self.game_instr_label = InstructionLabel(self.client.own_position, self.screen.get_rect().centerx, 525)
        self.is_routing = False  # determine if the user is routing
        self.route_from_x = None  # coordinate of the house you are routing from
        self.route_from_y = None
        self.player_model = [x for x in self.game_model.player_models if x.pos == self.client.own_position][0]

    def transition_to_finish(self):
        pass

    # ===============================
    # Ticking mechanism
    # These are called every UI frame
    # ===============================
    def ui_tick_menu(self):
        # Process events
        for e in pygame.event.get():
            if e.type == KEYDOWN:
                if e.key == K_DOWN:
                    self.cursor_y += 1
                    if self.cursor_y > 2: self.cursor_y = 2
                elif e.key == K_UP:
                    self.cursor_y -= 1
                    if self.cursor_y < 0: self.cursor_y = 0
                elif e.key == K_SPACE or e.key == K_RETURN:
                    # Confirm selection
                    if self.cursor_y == 0:
                        self.client.change_state_waiting()
                    elif self.cursor_y == 1:
                        self.client.change_state_instructions()
                    elif self.cursor_y == 2:
                        self.exit()
                        return

                if DEBUG: print "[INFO][UI] Selection: {0}".format(self.cursor_y)

        # Animate
        self.cursor.update()

        # Drawing
        self.cursor.set_rect(self.cursor_pos_menu[self.cursor_y])

        self.screen.fill(self.COLOR_WHITE)
        self.screen.blit(self.logo, self.logo_rect)
        self.menu_label_group.draw(self.screen)
        self.cursor.draw(self.screen)
        pygame.display.flip()

    def ui_tick_instructions(self):
        # Process events
        for e in pygame.event.get():
            if e.type == KEYDOWN:
                self.client.change_state_menu()

        # Drawing
        self.screen.fill(self.COLOR_WHITE)
        self.screen.blit(self.instr_screen, self.instr_screen.get_rect())
        pygame.display.flip()

    def ui_tick_waiting(self):
        # Process events
        for e in pygame.event.get():
            if e.type == KEYDOWN:
                if e.key == K_DOWN or e.key == K_UP:
                    if self.client.own_position is not None:
                        self.cursor_y = 1 - self.cursor_y
                    else:
                        self.cursor_y = 0
                elif e.key == K_LEFT:
                    if self.cursor_y == 0:
                        self.cursor_x = (self.cursor_x - 1) % 4
                elif e.key == K_RIGHT:
                    if self.cursor_y == 0:
                        self.cursor_x = (self.cursor_x + 1) % 4
                elif e.key == K_SPACE or e.key == K_RETURN:
                    if self.cursor_y == 0:
                        self.client.select_pos(self.cursor_x)
                    elif self.cursor_y == 1:
                        self.client.change_state_ready()

        # Animate
        self.cursor.update()

        # Drawing
        self.screen.fill(self.COLOR_WHITE)

        # Rectangles
        for i in range(4):
            if i in self.client.taken_positions:
                self.player_rects[i].set_color(self.PLAYER_COLOR_LIGHT[i])
                self.screen.blit(self.player_rects[i].image, self.player_rects[i].rect)
                castle = PlayerCastle(i, self.player_rects[i].rect)
                self.screen.blit(castle.image, castle.rect)
            else:
                self.player_rects[i].set_color(self.COLOR_GREEN)
                self.screen.blit(self.player_rects[i].image, self.player_rects[i].rect)

        # Draw ready rect
        if self.client.own_position is not None:
            self.ready_rect.set_color(self.COLOR_YELLOW)
        self.screen.blit(self.ready_rect.image, self.ready_rect.rect)
        self.screen.blit(self.ready_label.image, self.ready_label.rect)

        # Draw cursor
        if self.cursor_y == 0:
            self.cursor.set_rect(self.player_rects[self.cursor_x].rect)
        elif self.cursor_y == 1:
            self.cursor.set_rect(self.ready_rect.rect)
        self.cursor.draw(self.screen)

        # Draw logo
        self.screen.blit(self.logo, self.logo_rect)
        pygame.display.flip()


    def ui_tick_ready(self):
        # Process events
        for e in pygame.event.get(): pass

        # Drawing
        self.screen.fill(self.COLOR_WHITE)

        # Rectangles
        for i in range(4):
            if i in self.client.taken_positions:
                self.player_rects[i].set_color(self.PLAYER_COLOR_LIGHT[i])
                self.screen.blit(self.player_rects[i].image, self.player_rects[i].rect)
                castle = PlayerCastle(i, self.player_rects[i].rect)
                self.screen.blit(castle.image, castle.rect)
            else:
                self.player_rects[i].set_color(self.COLOR_GREEN)
                self.screen.blit(self.player_rects[i].image, self.player_rects[i].rect)

        self.screen.blit(self.waiting_label.image, self.waiting_label.rect)

        # Draw logo
        self.screen.blit(self.logo, self.logo_rect)
        pygame.display.flip()

    def ui_tick_finish(self):
        for e in pygame.event.get():
            if e.type == KEYDOWN:
                self.exit()

        self.screen.fill(self.COLOR_WHITE)
        label = None
        if self.is_winning_player:
            label = BasicLabel("YOU WIN!", self.font, (0, 0, 0), centerx=self.screen.get_rect().centerx, centery=self.screen.get_rect().centery)
        else:
            label = BasicLabel("YOU LOSE:(", self.font, (0, 0, 0), centerx=self.screen.get_rect().centerx, centery=self.screen.get_rect().centery)
        self.screen.blit(label.image, label.rect)
        pygame.display.flip()


    # ===================
    # Actual game ticking
    # ===================
    def ui_tick_game(self):
        # Process events
        for e in pygame.event.get():
            if e.type == KEYDOWN:
                if e.key == K_LEFT:
                    self.cursor_x = self.cursor_x - 1 if self.cursor_x != 0 else 0
                    self.cursor.set_rect(self.game_model.board[self.cursor_y][self.cursor_x].rect)
                    if self.is_routing:
                        my_house = self.game_model.board[self.route_from_y][self.route_from_x].building
                        my_house.route(self.ROUTE_LEFT, self.cursor_x, self.cursor_y)
                        if not my_house.is_routing: # finish routing
                            cmd = CastleGameCommand.Route(self.route_from_x, self.route_from_y, my_house.path_dim)
                            self.client.queue_command(cmd)
                            self.route_from_x = None
                            self.route_from_y = None
                            my_house.complete = True
                            self.is_routing = False
                elif e.key == K_RIGHT:
                    self.cursor_x = self.cursor_x + 1 if self.cursor_x != 7 else 7
                    self.cursor.set_rect(self.game_model.board[self.cursor_y][self.cursor_x].rect)
                    if self.is_routing:
                        my_house = self.game_model.board[self.route_from_y][self.route_from_x].building
                        my_house.route(self.ROUTE_RIGHT, self.cursor_x, self.cursor_y)
                        if not my_house.is_routing:
                            cmd = CastleGameCommand.Route(self.route_from_x, self.route_from_y, my_house.path_dim)
                            self.client.queue_command(cmd)
                            self.route_from_x = None
                            self.route_from_y = None
                            my_house.complete = True
                            self.is_routing = False
                elif e.key == K_UP:
                    self.cursor_y = self.cursor_y - 1 if self.cursor_y != 0 else 0
                    self.cursor.set_rect(self.game_model.board[self.cursor_y][self.cursor_x].rect)
                    if self.is_routing:
                        my_house = self.game_model.board[self.route_from_y][self.route_from_x].building
                        my_house.route(self.ROUTE_UP, self.cursor_x, self.cursor_y)
                        if not my_house.is_routing:
                            cmd = CastleGameCommand.Route(self.route_from_x, self.route_from_y, my_house.path_dim)
                            self.client.queue_command(cmd)
                            self.route_from_x = None
                            self.route_from_y = None
                            my_house.complete = True
                            self.is_routing = False
                elif e.key == K_DOWN:
                    self.cursor_y = self.cursor_y + 1 if self.cursor_y != 7 else 7
                    self.cursor.set_rect(self.game_model.board[self.cursor_y][self.cursor_x].rect)
                    if self.is_routing:
                        my_house = self.game_model.board[self.route_from_y][self.route_from_x].building
                        my_house.route(self.ROUTE_DOWN, self.cursor_x, self.cursor_y)
                        if not my_house.is_routing:
                            cmd = CastleGameCommand.Route(self.route_from_x, self.route_from_y, my_house.path_dim)
                            self.client.queue_command(cmd)
                            self.route_from_x = None
                            self.route_from_y = None
                            my_house.complete = True
                            self.is_routing = False


                elif e.key == K_a:
                    cmd = CastleGameCommand.Build(self.client.own_position, CastleGameCommand.Build.HOUSE, self.cursor_x, self.cursor_y)
                    self.client.queue_command(cmd)
                elif e.key == K_s:
                    cmd = CastleGameCommand.Build(self.client.own_position, CastleGameCommand.Build.MARKET, self.cursor_x, self.cursor_y)
                    self.client.queue_command(cmd)
                elif e.key == K_d:
                    cmd = CastleGameCommand.Build(self.client.own_position, CastleGameCommand.Build.TOWER, self.cursor_x, self.cursor_y)
                    self.client.queue_command(cmd)
                elif e.key == K_SPACE:
                    if not self.is_routing:
                        try:
                            house = self.game_model.board[self.cursor_y][self.cursor_x].building
                            if not house.isOwnedBy(self.client.own_position): continue
                            house.route(0, self.cursor_x, self.cursor_y)
                            self.route_from_x = self.cursor_x
                            self.route_from_y = self.cursor_y
                            self.is_routing = True
                        except Exception, e:
                            print "You should route from your houses."
                    elif self.route_from_x != None and self.route_from_y != None:
                        self.game_model.board[self.route_from_y][self.route_from_x].building.route(self.ROUTE_CANCEL, self.cursor_x, self.cursor_y)
                        cmd = CastleGameCommand.Route(self.route_from_x, self.route_from_y, [])
                        self.client.queue_command(cmd)
                        self.route_from_x = None
                        self.route_from_y = None
                        self.is_routing = False

        # Animate
        self.cursor.update()

        # Ticking
        self.game_model.tick_ui()

        # Drawing
        self.screen.fill(self.COLOR_WHITE)
        self.game_model.draw(self.screen)
        self.cursor.draw(self.screen)
        self.screen.blit(self.game_instr_label.image, self.game_instr_label.rect)

        pygame.display.flip()
