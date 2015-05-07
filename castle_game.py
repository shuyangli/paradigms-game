from castle_game_sprites import *
import pickle
import time


class CastleGameImmediateCommand:
    CMD_SEPARATOR = "#"

    class BeginRouting:
        def __init__(self, house_x, house_y):
            self.house_x = house_x
            self.house_y = house_y

        def apply_to(self, game):
            house = game.board[self.house_y][self.house_x].building
            house.reset_path()

        def serialize(self):
            return "T{0}{1}{2}{3}".format(
                CastleGameImmediateCommand.CMD_SEPARATOR,
                self.house_x,
                CastleGameImmediateCommand.CMD_SEPARATOR,
                self.house_y
            )

        @classmethod
        def deserialize(cls, encoded):
            _, house_x, house_y = encoded.split(CastleGameImmediateCommand.CMD_SEPARATOR)
            return cls(int(house_x), int(house_y))

    @classmethod
    def decode_command(cls, encoded):   # take a string
        if encoded[0] == "T":
            return cls.BeginRouting.deserialize(encoded)
        else:
            raise ValueError("Unknown encoded command: {0}".format(encoded))


class CastleGameCommand:
    """Wrapper class for game commands and command deserializer."""
    CMD_SEPARATOR = "#"

    class Build:
        HOUSE = "h"
        TOWER = "t"
        MARKET = "m"
        PATH = "p"
        NAME_TO_CLS = {
            "h": House,
            "t": Tower,
            "m": Market
        }

        def __init__(self, player_pos, building, x, y):
            self.player_pos = player_pos
            self.building = building
            self.x = x
            self.y = y

        def __str__(self):
            return "<Build>Player: {0}, Building: {1}, Position: {2}".format(self.player_pos, self.building, (self.x, self.y))

        def apply_to(self, game):
            assert len([x for x in game.player_models if x.pos == self.player_pos]) == 1

            player = [x for x in game.player_models if x.pos == self.player_pos][0]
            new_building = self.NAME_TO_CLS[self.building](game, player, game.board[self.y][self.x])

            # Test building criteria
            pred_no_building = (game.board[self.y][self.x].building is None)
            pred_grid_owner = (self.player_pos in game.board[self.y][self.x].owners)
            pred_enough_money = (player.money >= new_building.price)
            if pred_no_building and pred_grid_owner and pred_enough_money:
                # build
                game.board[self.y][self.x]._set_building(new_building)
                player.add_building(new_building)
                player.money -= new_building.price

                # add owner to grids around the current one
                for grid in game.grids_surrounding(self.x, self.y):
                    grid.owners.append(self.player_pos)


        def serialize(self):
            return "B{0}{1}{2}{3}{4}{5}{6}{7}".format(
                CastleGameCommand.CMD_SEPARATOR,
                self.player_pos,
                CastleGameCommand.CMD_SEPARATOR,
                self.x,
                CastleGameCommand.CMD_SEPARATOR,
                self.y,
                CastleGameCommand.CMD_SEPARATOR,
                self.building
            )

        @classmethod
        def deserialize(cls, encoded):
            _, player_pos, x, y, building = encoded.split(CastleGameCommand.CMD_SEPARATOR)
            return cls(int(player_pos), building, int(x), int(y))


    class Route:
        # TODO: print routes
        def __init__(self, house_x, house_y, path_dim):
            self.house_x = house_x
            self.house_y = house_y
            self.path_dim = path_dim

        def apply_to(self, game):
            # copy out route
            house = game.board[self.house_y][self.house_x].building
            house.reload_path_from_dimensions(self.path_dim)

        def serialize(self):
            return "R{0}{1}{2}{3}{4}{5}".format(
                CastleGameCommand.CMD_SEPARATOR,
                self.house_x,
                CastleGameCommand.CMD_SEPARATOR,
                self.house_y,
                CastleGameCommand.CMD_SEPARATOR,
                pickle.dumps(self.path_dim)
            )

        @classmethod
        def deserialize(cls, encoded):
            _, house_x, house_y, path_dim = encoded.split(CastleGameCommand.CMD_SEPARATOR)
            return cls(int(house_x), int(house_y), pickle.loads(str(path_dim)))

    @classmethod
    def decode_command(cls, encoded):   # take a string
        if encoded[0] == "B":
            return cls.Build.deserialize(encoded)
        elif encoded[0] == "R":
            return cls.Route.deserialize(encoded)
        else:
            raise ValueError("Unknown encoded command: {0}".format(encoded))


class CastleGamePlayerModel:
    """Castle game player class."""

    # Label drawing
    LABEL_LOCS = [(190, 50), (610, 50), (610, 450), (190, 450)]
    LABEL_COLORS = [(118, 66, 200), (192, 62, 62), (39, 190, 173), (200, 146, 37)]

    # Default value
    INITIAL_MONEY = 50
    INITIAL_MONEY_INCREMENT = 5

    last_time = 0
    acc_time = 0

    FONT_NAME = None
    FONT_SIZE = 26

    def __init__(self, game, pos, castle_grid):
        # TODO: clean this up
        self.pos = pos
        self.castle_grid = castle_grid
        self.buildings = []     # [buildings]
        self.soldiers = []      # [soldiers]

        self.castle = Castle(game, self, self.castle_grid)
        self.castle_grid._set_building(self.castle)

        self.money = self.INITIAL_MONEY
        self.money_increment = self.INITIAL_MONEY_INCREMENT

        self._game = game

        self.is_defeated = False

        # Labels
        self.font = pygame.font.Font(self.FONT_NAME, self.FONT_SIZE)

    def __str__(self):
        return "<Player> {0}".format(self.pos)

    def defeated(self):
        # called when the player is defeated
        # destroy all buildings
        for building in self.buildings:
            building.destroyed()
        for soldier in self.soldiers:
            soldier.die()

        self.is_defeated = True
        self._game.check_end()


    def add_building(self, building):
        self.buildings.append(building)

    def remove_building(self, building):
        self.buildings.remove(building)
        # also remove owner from grids around the building's grid
        for grid in self._game.grids_surrounding(building.grid.x, building.grid.y):
            grid.owners.reverse()
            grid.owners.remove(self.pos)
            grid.owners.reverse()

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
        # update money every second
        current_time = time.time()
        if self.last_time == 0:
            self.last_time = current_time
        else:
            self.acc_time += current_time - self.last_time
            self.last_time = current_time
            while self.acc_time >= 1.0:
                self.acc_time -= 1.0
                self.money += self.money_increment

        for building in self.buildings:
            building.tick_lock_step()
        for soldier in self.soldiers:
            soldier.tick_lock_step()

    # =============
    # Label drawing
    # =============
    def draw(self, surface):
        label_color = self.LABEL_COLORS[self.pos]
        label_loc = self.LABEL_LOCS[self.pos]

        if not self.is_defeated:
            money_text = "${0}".format(self.money)
            inc_text = "${0} / second".format(self.money_increment)
        else:
            money_text = "DEAD"
            inc_text = "x_x"

        money_label = None
        inc_label = None

        if self.pos == 0 or self.pos == 3:
            # topright align
            money_label = BasicLabel(money_text, self.font, label_color, topright=label_loc)
            inc_label_loc = (label_loc[0], label_loc[1] + money_label.rect.height)
            inc_label = BasicLabel(inc_text, self.font, label_color, topright=inc_label_loc)

        elif self.pos == 1 or self.pos == 2:
            # topleft align
            money_label = BasicLabel(money_text, self.font, label_color, topleft=label_loc)
            inc_label_loc = (label_loc[0], label_loc[1] + money_label.rect.height)
            inc_label = BasicLabel(inc_text, self.font, label_color, topleft=inc_label_loc)

        surface.blit(money_label.image, money_label.rect)
        surface.blit(inc_label.image, inc_label.rect)


class CastleGameModel:
    """Castle game model class. This class represents the game state."""
    WIDTH = 8
    HEIGHT = 8

    def __init__(self, game_ui, all_players_pos, current_player_pos, debug=False):
        global DEBUG
        DEBUG = debug

        self.game_ui = game_ui
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
            player = CastleGamePlayerModel(self, PLAYER_PURPLE, self.board[0][0])
            self.player_models.append(player)
        if PLAYER_PINK in all_players_pos:
            player = CastleGamePlayerModel(self, PLAYER_PINK, self.board[0][self.WIDTH-1])
            self.player_models.append(player)
        if PLAYER_CYAN in all_players_pos:
            player = CastleGamePlayerModel(self, PLAYER_CYAN, self.board[self.HEIGHT-1][self.WIDTH-1])
            self.player_models.append(player)
        if PLAYER_ORANGE in all_players_pos:
            player = CastleGamePlayerModel(self, PLAYER_ORANGE, self.board[self.HEIGHT-1][0])
            self.player_models.append(player)

        self.current_player = [x for x in self.player_models if x.pos == current_player_pos][0]


    def prepare_game(self, client):
        pass

    def check_end(self):
        surviving_players_count = reduce(lambda acc, itm: acc + 1 if not itm.is_defeated else acc, self.player_models, 0)
        if surviving_players_count == 1:
            surviving_player = [x for x in self.player_models if not x.is_defeated][0]
            if surviving_player == self.current_player:
                self.game_ui.is_winning_player = True
            else:
                self.game_ui.is_winning_player = False
            self.game_ui.client.change_state_finish()


    def tick_ui(self):
        # called every ui frame
        for player in self.player_models:
            player.update()

    def draw(self, surface):
        # actual drawing
        # draw board
        for row in self.board:
            for cell in row:
                cell.draw(surface)

        # draw user labels
        for player in self.player_models:
            player.draw(surface)

        # draw paths
        for player in self.player_models:
            for building in player.buildings:
                if hasattr(building, "path") and building.path != None:
                    for pathSection in building.path.pathSections:
                        surface.blit(pathSection.image, pathSection.rect)

        # draw soldiers
        for player in self.player_models:
            for soldier in player.soldiers:
                surface.blit(soldier.image, soldier.rect)


    def tick_lock_step(self):
        # called every lockstep
        for player in self.player_models:
            player.tick_lock_step()

    # helpers
    def grids_surrounding(self, cx, cy):
        grids = []
        for x in range(cx - 1, cx + 2):
            for y in range(cy - 1, cy + 2):
                try:
                    if x >= 0 and y >= 0:
                        grids.append(self.board[y][x])
                except IndexError:
                    pass
        return grids

    def grid_for_coordinates(self, x, y):
        x_grid = int((x - 200) // 50)
        y_grid = int((y - 50) // 50)
        if x_grid >= 0 and x_grid < 8 and y_grid >= 0 and y_grid < 8:
            return self.board[y_grid][x_grid]
        else:
            raise ValueError("Given x and y coordinates don't represent a grid: ({0},{1})".format(x, y))
