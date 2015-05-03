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
            # TODO
            print "[TODO] Build's apply_to called"
            return
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
            # TODO
            print "[TODO] Destroy's apply_to called"
            return
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
    INITIAL_MONEY = 0
    INITIAL_MONEY_INCREMENT = 5

    GAME_FRAMES_PER_LOCK_STEP = 10
    step_count = 0

    def __init__(self):
        # TODO: clean this up
        self.money = self.INITIAL_MONEY
        self.castle = Castle()
        self.buildings = []     # [buildings]
        self.army = []          # [soldiers]
        self.money_increment = self.INITIAL_MONEY_INCREMENT

    # =================
    # Ticking mechanism
    # =================
    def update(self):
        for building in self.buildings:
            building.update()
        for soldier in self.army:
            soldier.update()

    def tick_lock_step(self):
        self.step_count += 1

        if self.step_count >= self.GAME_FRAMES_PER_LOCK_STEP:
            # update every second
            self.step_count = 0
            self.money += self.money_increment

        for building in self.buildings:
            building.tick_lock_step()
        for soldier in self.army:
            soldier.tick_lock_step()


class CastleGameModel:
    """Castle game model class. This class represents the game state."""
    WIDTH = 8
    HEIGHT = 8

    def __init__(self):
        self.board = [[BoardGrid(x, y) for x in range(self.WIDTH)] for y in range(self.HEIGHT)]

        # Set default owners
        for i in range(3):
            for j in range(3):
                self.board[i][j]._set_owner(PLAYER_PURPLE)
                self.board[self.WIDTH-1-i][j]._set_owner(PLAYER_PINK)
                self.board[self.WIDTH-1-i][self.HEIGHT-1-j]._set_owner(PLAYER_CYAN)
                self.board[i][self.HEIGHT-1-j]._set_owner(PLAYER_ORANGE)

        self.player_models = []

    def prepare_game(self, client):
        pass

    def tick_ui(self):
        # called every ui frame
        for player in self.player_models:
            player.update()

    def draw(self, surface):
        for row in self.board:
            for cell in row:
                cell.draw(surface)

    def tick_lock_step(self):
        # called every lockstep
        for player in self.player_models:
            player.tick_lock_step()
