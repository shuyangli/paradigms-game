import sys, os
import pygame
from pygame.locals import *

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
        pygame.mixer.init()         # for sound
        self.screen_size = (640, 480)
        self.screen = pygame.display.set_mode(self.screen_size)


    def set_client(self, client):
        self.client = client


    # ===============================
    # Ticking mechanism
    # These are called every UI frame
    # ===============================
    def ui_tick_menu(self):
        pass

    def ui_tick_waiting(self):
        pass

    def ui_tick_ready(self):
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
        for e in pygame.event.get():
            if e.type == KEYDOWN:
                if e.key == K_1:
                    cmd = CastleGameCommand.Build(["build", 0, 0, "house"])
                    self.client.queue_command(cmd)

        # Drawing
        # for sprite in self.sprites:
        #     sprite.draw()
        #
        pygame.display.flip()
