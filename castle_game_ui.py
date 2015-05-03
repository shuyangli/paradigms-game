import sys, os
import pygame
from pygame.locals import *
from pygame import font

from castle_game import CastleGameCommand, CastleGameModel
from castle_game_sprites import *

class CastleGameUI:
    """UI class for Castle game."""

    # 10 game frames per lockstep, 6 locksteps per second
    # Realistically this would change based on network latency
    GAME_FRAMES_PER_LOCK_STEP = 10
    game_frame_id = 0

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

    PLAYER_COLOR_SELECTED = [COLOR_LIGHT_PURPLE, COLOR_LIGHT_PINK, COLOR_LIGHT_CYAN, COLOR_LIGHT_ORANGE]

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
        self.screen = pygame.display.set_mode(self.SCREEN_SIZE)
        self.font = pygame.font.Font(self.FONT_NAME, self.FONT_SIZE)


    def set_client(self, client):
        self.client = client

    def exit(self):
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

        play_label = BasicLabel(self, "PLAY", self.COLOR_BLACK, centerx="center", centery=375)
        instr_label = BasicLabel(self, "INSTRUCTIONS", self.COLOR_BLACK, centerx="center", centery=425)
        exit_label = BasicLabel(self, "QUIT", self.COLOR_BLACK, centerx="center", centery=475)
        self.menu_label_group = pygame.sprite.Group(play_label, instr_label, exit_label)

        self.cursor = Cursor(self.COLOR_RED, play_label.rect, width=4)
        self.cursor_pos_menu = [play_label.rect, instr_label.rect, exit_label.rect]


    def transition_to_waiting(self):
        self.cursor_x = 0
        self.cursor_y = 0

        self.ready_label = BasicLabel(self, "READY", self.COLOR_BLACK, centerx="center", centery=525)
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

        self.waiting_label = BasicLabel(self, "WAITING FOR OPPONENTS ...", self.COLOR_BLACK, centerx="center", centery=525)

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

    # get the coordinates of the encompassing rectangle
    # that is width wider on each side
    def border_coord(self, coord, width): # coord: [minx, maxx, miny, maxy]
        return [coord[0] - width,
                coord[1] + width,
                coord[2] - width,
                coord[3] + width]

    # TODO: transition to the ready state when all people are ready
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
                self.player_rects[i].set_color(self.PLAYER_COLOR_SELECTED[i])
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
                self.player_rects[i].set_color(self.PLAYER_COLOR_SELECTED[i])
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
        # First process lockstep stuff
        if self.game_frame_id == 0:
            # Every first game frame, we advance the lock step
            if not self.client.tick_lock_step():
                # If we failed to tick lockstep, make sure we try to tick again
                self.game_frame_id -= 1

        # Increment game frame
        self.game_frame_id += 1
        if self.game_frame_id >= self.GAME_FRAMES_PER_LOCK_STEP:
            self.game_frame_id = 0

        # Then handle regular game stuff
        # Process events
        for e in pygame.event.get():
            if e.type == KEYDOWN:
                # DEBUG
                if e.key == K_SPACE:
                    cmd = CastleGameCommand.Build(CastleGameCommand.Build.HOUSE, 0, 0)
                    self.client.queue_command(cmd)

        # Ticking
        self.game_model.tick_ui()

        # Drawing
        self.screen.fill(self.COLOR_WHITE)
        self.game_model.draw(self.screen)
        # TODO: draw instructions, user labels, and so on

        pygame.display.flip()
