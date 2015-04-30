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

    def __init__(self):
        # Init pygame
        self.init_pygame()

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
        play_label = BasicLabel(self, "PLAY", self.COLOR_BLACK, centerx="center", centery=375)
        instr_label = BasicLabel(self, "INSTRUCTIONS", self.COLOR_BLACK, centerx="center", centery=425)
        exit_label = BasicLabel(self, "EXIT", self.COLOR_BLACK, centerx="center", centery=475)
        self.menu_label_group = pygame.sprite.Group(play_label, instr_label, exit_label)

    def transition_menu_to_waiting(self):
        pass

    # ===============================
    # Ticking mechanism
    # These are called every UI frame
    # ===============================
    def ui_tick_menu(self):
        # Process events
        for e in pygame.event.get():
            if e.type == KEYDOWN:
                if e.key == K_SPACE:
                    # Confirm selection
                    self.client.change_state_waiting()

        # Drawing
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
        # DEBUG
        label = self.font.render("Waiting state", 1, self.COLOR_WHITE)
        self.screen.blit(label, (100, 100))
        pygame.display.flip()

    def ui_tick_ready(self):
        # Process events
        for e in pygame.event.get():
            pass

        # Drawing
        self.screen.fill(self.COLOR_WHITE)
        # DEBUG
        label = self.font.render("Ready state", 1, self.COLOR_WHITE)
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
