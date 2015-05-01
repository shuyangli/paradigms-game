from castle_game_sprites import *

class CastleGameCommand:
    """Wrapper class for game commands and command deserializer."""
    CMD_SEPARATOR = "#"

    class Build:
        HOUSE = "h"
        TOWER = "t"
        MARKET = "m"
        NAME_TO_CLS = {
            "h": House,
            "t": Tower,
            "m": Market
        }

        def __init__(self, building, x, y):
            self.building = building
            self.x = x
            self.y = y

        def apply_to(self, game):
            if game.board[self.y][self.x] == game.empty_square:
                # build
                game_board[self.y][self.x] = self.NAME_TO_CLS[self.building]()

        def serialize(self):
            return "B{0}{1}{2}{3}{4}{5}".format(
                CastleGameCommand.CMD_SEPARATOR,
                self.x,
                CastleGameCommand.CMD_SEPARATOR,
                self.y,
                CastleGameCommand.CMD_SEPARATOR,
                self.building
            )

        @classmethod
        def deserialize(cls, encoded):
            _, x, y, building = encoded.split(CastleGameCommand.CMD_SEPARATOR)
            return cls(building, int(x), int(y))


    class Destroy:
        def __init__(self, x, y):
            self.x = x
            self.y = y

        def apply_to(self, game):
            # destroy
            game.board[self.y][self.x] = game.empty_square

        def serialize(self):
            return "D{0}{1}{2}{3}".format(
                CastleGameCommand.CMD_SEPARATOR,
                self.x,
                CastleGameCommand.CMD_SEPARATOR,
                self.y
            )

        @classmethod
        def deserialize(cls, encoded):
            _, x, y = encoded.split(CastleGameCommand.CMD_SEPARATOR)
            return cls(int(x), int(y))


    class Route:
        # TODO: figure out how to handle rerouting of a house
        def __init__(self, house_x, house_y, past_x, past_y, current_x, current_y):
            self.h_x = house_x
            self.h_y = house_y
            self.p_x = past_x
            self.p_y = past_y
            self.c_x = current_x
            self.c_y = current_y


    @classmethod
    def decode_command(cls, encoded):   # take a string
        if encoded[0] == "B":
            return cls.Build.deserialize(encoded)
        elif encoded[0] == "D":
            return cls.Destroy.deserialize(encoded)
        else:
            raise ValueError("Unknown encoded command: {0}".format(encoded))


class CastleGamePlayerModel:
    """Castle game player class."""
    # Castle position
    POS_TOP_LEFT = (0, 0)
    POS_TOP_RIGHT = (0, 6)
    POS_BTM_LEFT = (6, 0)
    POS_BTM_RIGHT = (6, 6)

    # Default value
    INIT_MONEY = 0
    INIT_INCREMENT = 5

    def __init__(self):
        # TODO: clean this up
        self.money = self.INIT_MONEY
        self.castle = Castle()
        self.buildings = []
        self.army = []
        self.money_increment = self.INIT_INCREMENT


class CastleGameModel:
    """Castle game model class. This class represents the game state."""
    DEFAULT_WIDTH = 7
    DEFAULT_HEIGHT = 7

    def __init__(self, width=7, height=7):
        self.empty_square = EmptySquare()
        self.board = [[self.empty_square] * width] * height
        self.player_models = []
