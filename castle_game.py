class CastleGameCommands:
    """Wrapper class for game commands and command builder."""
    CMD_SEPARATOR = "#"
    CMD_VERB = {
        "build": "B",
        "destroy": "D",
        "route": "R",
        "B": "build",
        "D": "destroy",
        "R": "route"
    }
    CMD_BUILD_BUILDING = {
        "house": "h",
        "tower": "t",
        "market": "m",
        "h": "house",
        "t": "tower",
        "m": "market"
    }

    @classmethod
    def encode_command(cls, decoded):   # take a list
        [command, location_x, location_y, option] = decoded

        encoded = "{0}{1}{2}{3}{4}{5}{6}".format(
            self.CMD_VERB[command],
            self.CMD_SEPARATOR,
            str(location_x),
            self.CMD_SEPARATOR,
            str(location_y),
            self.CMD_SEPARATOR,
            option
        )
        return encoded                  # return a string

    @classmethod
    def decode_command(cls, encoded):   # take a string
        [command, location_x, location_y, option] = encoded.split(self.CMD_SEPARATOR)

        decoded = [
            self.CMD_VERB[command],
            int(location_x),
            int(location_y),
            option
        ]
        return decoded                  # return a list


class CastleGameModel:
    """Castle game model class. This class represents the game state."""
    def __init__(self):
        pass

    def apply_command(self, cmd):
        pass
