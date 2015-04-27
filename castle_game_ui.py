import sys, os
import time
import pygame
from pygame.locals import *

from castle_game import CastleGameCommands, CastleGameModel

class CastleGameUI:
    """UI class for Castle game."""

    # 5 game frames per lockstep, 10 locksteps per second
    GAME_FRAMES_PER_LOCK_STEP = 5

    real_time = 0.0
    accumulated_time = 0.0

    game_frame_id = 0


    def __init__(self):
        # Init pygame
        pygame.init()
        pygame.mixer.init()         # for sound

        # Init other aspects


    def set_client(self, client):
        self.client = client


    # =============
    # Game handling
    # =============
    def start_actual_game():
        pass


    # =================
    # Ticking mechanism
    # =================
    def ui_tick_ready(self):
        pass

    def ui_tick_waiting(self):
        pass

    def ui_tick_game(self):
        # Called every actual frame (hopefully 50 fps)
        print "UI tick"

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
        # for event in pygame.event.get():
        #     pass

        # Drawing
        # for sprite in self.sprites:
        #     sprite.draw()
        #
        # pygame.display.flip()
