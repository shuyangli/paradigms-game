import sys, os
import pygame
from pygame.locals import *

from castle_game import CastleGameCommands, CastleGameModel

class CastleGameUI:
    """UI class for Castle game."""

    GAME_STATE_WAITING = 0
    GAME_STATE_PLAYING = 1

    def __init__(self):
        # Init pygame
        pygame.init()
        pygame.mixer.init()         # for sound

        # Init other aspects
        self.current_state = self.GAME_STATE_WAITING

    def tick(self):
        # Called every actual frame (hopefully 60 fps)
        print "Called"

        # Process events
        for event in pygame.event.get():
            pass

        # Tick sprites (no game tick yet, only advance their simulated state)

        # Drawing
        pygame.display.flip()
