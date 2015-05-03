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

    # Default value
    INITIAL_MONEY = 0
    INITIAL_MONEY_INCREMENT = 5

    GAME_FRAMES_PER_LOCK_STEP = 10
    step_count = 0

    def __init__(self, pos, castle_grid, buildings=[], soldiers=[]):
        # TODO: clean this up
        self.pos = pos
        self.castle_grid = castle_grid
        self.buildings = buildings  # [buildings]
        self.soldiers = soldiers    # [soldiers]

        self.castle = Castle(self, self.castle_grid)
        self.castle_grid._set_building(self.castle)

        # Path
        self.path = None

        self.money = self.INITIAL_MONEY
        self.money_increment = self.INITIAL_MONEY_INCREMENT

    def destroy(self):
        # called when the player is defeated
        pass

    # =================
    # Ticking mechanism
    # =================
    def update(self):
        self.castle.update()
        for building in self.buildings:
            building.update()
        for soldier in self.soldiers:
            soldier.update()

    def tick_lock_step(self):
        self.step_count += 1

        if self.step_count >= self.GAME_FRAMES_PER_LOCK_STEP:
            # update every second
            self.step_count = 0
            self.money += self.money_increment

        for building in self.buildings:
            building.tick_lock_step()
        for soldier in self.soldiers:
            soldier.tick_lock_step()


class CastleGameModel:
    """Castle game model class. This class represents the game state."""
    WIDTH = 8
    HEIGHT = 8

    def __init__(self, all_players_pos, current_player_pos, debug=False):
        global DEBUG
        DEBUG = debug

        self.board = [[BoardGrid(x, y) for x in range(self.WIDTH)] for y in range(self.HEIGHT)]

        # Set default owners
        for i in range(3):
            for j in range(3):
                if PLAYER_PURPLE in all_players_pos:
                    self.board[i][j]._set_owner(PLAYER_PURPLE)
                if PLAYER_PINK in all_players_pos:
                    self.board[i][self.WIDTH-1-j]._set_owner(PLAYER_PINK)
                if PLAYER_CYAN in all_players_pos:
                    self.board[self.HEIGHT-1-i][self.WIDTH-1-j]._set_owner(PLAYER_CYAN)
                if PLAYER_ORANGE in all_players_pos:
                    self.board[self.HEIGHT-1-i][j]._set_owner(PLAYER_ORANGE)

        # Add player models
        self.player_models = []
        if PLAYER_PURPLE in all_players_pos:
            player = CastleGamePlayerModel(PLAYER_PURPLE, self.board[0][0])
            self.player_models.append(player)
        if PLAYER_PINK in all_players_pos:
            player = CastleGamePlayerModel(PLAYER_PINK, self.board[0][self.WIDTH-1])
            self.player_models.append(player)
        if PLAYER_CYAN in all_players_pos:
            player = CastleGamePlayerModel(PLAYER_CYAN, self.board[self.HEIGHT-1][self.WIDTH-1])
            self.player_models.append(player)
        if PLAYER_ORANGE in all_players_pos:
            player = CastleGamePlayerModel(PLAYER_ORANGE, self.board[self.HEIGHT-1][0])
            self.player_models.append(player)


    def prepare_game(self, client):
        pass

    def tick_ui(self):
        # called every ui frame
        for player in self.player_models:
            player.update()

    def draw(self, surface):
        # actual drawing
        for row in self.board:
            for cell in row:
                cell.draw(surface)

    def tick_lock_step(self):
        # called every lockstep
        for player in self.player_models:
            player.tick_lock_step()
