class CastleGameCommand:
    """Wrapper class for game commands and command deserializer."""
    CMD_SEPARATOR = "#"

    class Build:
        HOUSE = "h"
        TOWER = "t"
        MARKET = "m"

        def __init__(self, building, x, y):
            self.building = building
            self.x = x
            self.y = y

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


class CastleGameModel:
    """Castle game model class. This class represents the game state."""
    def __init__(self):
        pass

    def apply_command(self, cmd):
        pass
