import sys, os
import pygame
from pygame.locals import *

from castle_game import CastleGameCommands, CastleGameModel

class CastleGameUI:
    """UI class for Castle game."""

    def __init__(self):
        # Init pygame
        pygame.init()
        pygame.mixer.init()         # for sound

        # Init other aspects

    def setClient(self, client):
        self.client = client

    def tick(self):
        # Called every actual frame (hopefully 60 fps)
        print "Called"

        # Process events
        for event in pygame.event.get():
            pass

        # Tick sprites (no game tick yet, only advance their simulated state)
        if self.client.current_state == GAME_STATE_WAITING:
            # Drawing
            pass
        elif self.client.current_state == GAME_STATE_READY:
            # Drawing
            pass
        elif self.client.current_state == GAME_STATE_PLAYING:
            # Actual game tick should happen at 10 fps (tolerate a 50ms delay)

            # Drawing
            pass
        else:
            # Something bad occured
            pass

        pygame.display.flip()
