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
        self.game_model = CastleGameModel(all_players_pos, current_player_pos, DEBUG)
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
        play_label = BasicLabel("PLAY", self.font, self.COLOR_BLACK, centerx=screen_centerx, centery=375)
        instr_label = BasicLabel("INSTRUCTIONS", self.font, self.COLOR_BLACK, centerx=screen_centerx, centery=425)
        exit_label = BasicLabel("QUIT", self.font, self.COLOR_BLACK, centerx=screen_centerx, centery=475)
        self.menu_label_group = pygame.sprite.Group(play_label, instr_label, exit_label)

        self.cursor = Cursor(self.COLOR_RED, play_label.rect, width=4)
        self.cursor_pos_menu = [play_label.rect, instr_label.rect, exit_label.rect]


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
        self.isRouting = False  # determine if the user is routing

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
                elif e.key == K_SPACE:
                    # Confirm selection
                    if self.cursor_y == 0:
                        self.client.change_state_waiting()
                    elif self.cursor_y == 1:
                        # TODO: instructions
                        pass
                    elif self.cursor_y == 2:
                        self.exit()
                        return

                if DEBUG: print "[INFO][UI] Selection: {0}".format(self.cursor_y)

        # Drawing
        self.cursor.set_rect(self.cursor_pos_menu[self.cursor_y])

        self.screen.fill(self.COLOR_WHITE)
        self.menu_label_group.draw(self.screen)
        self.cursor.draw(self.screen)
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
                elif e.key == K_SPACE:
                    if self.cursor_y == 0:
                        self.client.select_pos(self.cursor_x)
                    elif self.cursor_y == 1:
                        self.client.change_state_ready()

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

        pygame.display.flip()


    # ===================
    # Actual game ticking
    # ===================
    def ui_tick_game(self):
        # Process events
        for e in pygame.event.get():
            if e.type == KEYDOWN:
                if e.key == K_LEFT:
                    self.cursor_x = (self.cursor_x - 1) % 8
                    self.cursor.set_rect(self.game_model.board[self.cursor_y][self.cursor_x].rect)
                elif e.key == K_RIGHT:
                    self.cursor_x = (self.cursor_x + 1) % 8
                    self.cursor.set_rect(self.game_model.board[self.cursor_y][self.cursor_x].rect)
                elif e.key == K_UP:
                    self.cursor_y = (self.cursor_y - 1) % 8
                    self.cursor.set_rect(self.game_model.board[self.cursor_y][self.cursor_x].rect)
                elif e.key == K_DOWN:
                    self.cursor_y = (self.cursor_y + 1) % 8
                    self.cursor.set_rect(self.game_model.board[self.cursor_y][self.cursor_x].rect)

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
                    cmd = CastleGameCommand.Route(self.client.own_position, self.cursor_x, self.cursor_y)
                    self.client.queue_command(cmd)

        # Ticking
        self.game_model.tick_ui()

        # Drawing
        self.screen.fill(self.COLOR_WHITE)
        self.game_model.draw(self.screen)
        self.cursor.draw(self.screen)
        self.screen.blit(self.game_instr_label.image, self.game_instr_label.rect)

        pygame.display.flip()
