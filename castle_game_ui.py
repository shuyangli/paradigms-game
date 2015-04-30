import sys, os
import pygame
from pygame.locals import *
from pygame import ftfont

from castle_game import CastleGameCommand, CastleGameModel
from castle_game_sprites import *

class CastleGameUI:
    """UI class for Castle game."""

    # 10 game frames per lockstep, 5 locksteps per second
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

    def __init__(self, debug=False):
        # Init pygame
        self.init_pygame()

        global DEBUG
        DEBUG = debug

        # Init other aspects
        self.cursor_x = 0
        self.cursor_y = 0

        # Initial state
        self.enter_menu()


    def init_pygame(self):
        pygame.init()
        self.screen = pygame.display.set_mode(self.SCREEN_SIZE)
        self.font = pygame.ftfont.Font(self.FONT_NAME, self.FONT_SIZE)


    def set_client(self, client):
        self.client = client

    def exit(self):
        pygame.quit()
        self.client.exit()


    # ===================
    # Starting a new game
    # ===================
    def start_game(self):
        self.game_model = CastleGameModel()
        self.client.set_game_model(self.game_model)

    def end_game(self):
        self.client.set_game_model(None)
        self.game_model = None

    # =================
    # State transitions
    # =================
    def enter_menu(self):
        self.cursor_x = 0
        self.cursor_y = 0

        play_label = BasicLabel(self, "PLAY", self.COLOR_BLACK, centerx="center", centery=375)
        instr_label = BasicLabel(self, "INSTRUCTIONS", self.COLOR_BLACK, centerx="center", centery=425)
        exit_label = BasicLabel(self, "EXIT", self.COLOR_BLACK, centerx="center", centery=475)

        self.right_arrow = BasicArrow(self)
        arrow_pos = [(play_label.rect.left - self.right_arrow.rect.width, play_label.rect.centery),
                    (instr_label.rect.left - self.right_arrow.rect.width, instr_label.rect.centery),
                    (exit_label.rect.left - self.right_arrow.rect.width, exit_label.rect.centery)]
        self.right_arrow.positions = arrow_pos
        self.menu_label_group = pygame.sprite.Group(self.right_arrow, play_label, instr_label, exit_label)


    def transition_menu_to_waiting(self):
        self.cursor_x = 0
        self.cursor_y = 0


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

                if DEBUG:
                    print "Selection: {0}".format(self.cursor_y)

        # Drawing
        self.right_arrow.update_selection(self.cursor_y)
        self.screen.fill(self.COLOR_WHITE)
        self.menu_label_group.draw(self.screen)
        pygame.display.flip()


    def ui_tick_waiting(self):
        # Process events
        for e in pygame.event.get():
            if e.type == KEYDOWN:
                # DEBUG
                if e.key == K_SPACE:
                    self.client.change_state_ready()

        # Drawing
        self.screen.fill(self.COLOR_WHITE)
        ready_label = BasicLabel(self, "READY", self.COLOR_BLACK, centerx="center", centery=525)
        ready_rect = Rect(self.COLOR_YELLOW, 250, 550, 475, 575)
        self.screen.blit(ready_rect.image, ready_rect.rect)
        self.screen.blit(ready_label.image, ready_label.rect)
        pygame.display.flip()


    def ui_tick_ready(self):
        # Process events
        for e in pygame.event.get():
            pass

        # Drawing
        self.screen.fill(self.COLOR_WHITE)
        # DEBUG
        label = self.font.render("Ready state", 1, self.COLOR_BLACK)
        self.screen.blit(label, (100, 100))
        pygame.display.flip()


    # ===================
    # Actual game ticking
    # ===================
    def ui_tick_game(self):
        # Called every actual frame (hopefully 50 fps)
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

        # Drawing
        self.screen.fill(self.COLOR_WHITE)
        # for sprite in self.sprites:
        #     sprite.draw()
        #
        # DEBUG
        label = self.font.render("Game state", 1, self.COLOR_WHITE)
        self.screen.blit(label, (100, 100))
        pygame.display.flip()
