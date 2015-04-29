import sys, os
import pygame
from pygame.locals import *
from pygame import ftfont

from castle_game import CastleGameCommand, CastleGameModel
from castle_game_sprites import *

class CastleGameUI:
    """UI class for Castle game."""

    # 5 game frames per lockstep, 10 locksteps per second
    # Realistically this would change based on network latency
    GAME_FRAMES_PER_LOCK_STEP = 5
    game_frame_id = 0

    def __init__(self):
        # Init pygame
        self.init_pygame()

        # Init other aspects


    def init_pygame(self):
        pygame.init()
        self.screen_size = (640, 480)
        self.screen = pygame.display.set_mode(self.screen_size)
        self.font = pygame.ftfont.Font(None, 13)


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

    # ===============================
    # Ticking mechanism
    # These are called every UI frame
    # ===============================
    def ui_tick_menu(self):
        # Process events
        for e in pygame.event.get():
            if e.type == KEYDOWN:
                # DEBUG
                if e.key == K_SPACE:
                    self.client.change_state_waiting()

        # Drawing
        self.screen.fill((0, 0, 0))
        # DEBUG
        label = self.font.render("Menu state", 1, (255, 255, 255))
        self.screen.blit(label, (100, 100))
        pygame.display.flip()

    def ui_tick_waiting(self):
        # Process events
        for e in pygame.event.get():
            if e.type == KEYDOWN:
                # DEBUG
                if e.key == K_SPACE:
                    self.client.change_state_ready()

        # Drawing
        self.screen.fill((0, 0, 0))
        # DEBUG
        label = self.font.render("Waiting state", 1, (255, 255, 255))
        self.screen.blit(label, (100, 100))
        pygame.display.flip()

    def ui_tick_ready(self):
        # Process events
        for e in pygame.event.get():
            pass

        # Drawing
        self.screen.fill((0, 0, 0))
        # DEBUG
        label = self.font.render("Ready state", 1, (255, 255, 255))
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
        self.screen.fill((0, 0, 0))
        # for sprite in self.sprites:
        #     sprite.draw()
        #
        # DEBUG
        label = self.font.render("Game state", 1, (255, 255, 255))
        self.screen.blit(label, (100, 100))
        pygame.display.flip()
