from twisted.internet.protocol import Factory, Protocol
from twisted.internet.endpoints import TCP4ServerEndpoint
from twisted.internet import reactor

from castle_game import CastleGameCommand, CastleGameModel

import json


class CastleServerProtocol(Protocol):
    PAYLOAD_TYPE_COMMAND = "cmd"
    PAYLOAD_TYPE_STATE_CHANGE = "chgstate"
    FAYLOAD_TYPE_ERROR = "error"

    def __init__(self, server):
        self.server = server

    def connectionMade(self):
        # Check if game is on; if it's on, deny incoming connection
        if self.server.is_game_on():
            self.rejectClient()
            return

        self.server.players.append(self)
        self.server.player_states[self] = self.server.GAME_STATE_MENU

        if DEBUG:
            print "New connection from {0}".format(self.transport.getPeer())
            print self.server.player_states

    def connectionLost(self, reason):
        if self in self.server.players:
            self.server.players.remove(self)
            self.server.player_states.pop(self, None)
        if DEBUG:
            print "Lost connection from {0}".format(self.transport.getPeer())
            print "Reason: "reason

    def rejectClient(self):
        # rejection: {"type": "error", "info": "game is on"}
        ddict = {"type": self.PAYLOAD_TYPE_ERROR, "info": "Game is currently on"}
        payload = json.dumps(ddict)
        if DEBUG: print payload
        self.transport.write(payload)
        self.transport.loseConnection()


    def dataReceived(self, data):
        # Receive a command from the client
        if DEBUG:
            print data

        ddict = json.loads(data)
        if ddict["type"] == self.PAYLOAD_TYPE_COMMAND:
            # game command: {"type": "cmd", "lturn": cmd_dict["turn"], "cmd": cmd_dict["command"].serialize()}
            # broadcast command
            self.server.broadcast_command(self, ddict)
        elif ddict["type"] == self.PAYLOAD_TYPE_STATE_CHANGE:
            # state change: {"type": "chgstate", "state": state}
            # change state
            self.server.player_states[self] = ddict["state"]
            # if everyone is ready, broadcast game start
            if self.server.is_everyone_ready():
                # TODO
                self.server.broadcast_ready()


class CastleServerProtocolFactory(Factory):
    def __init__(self, castle_server):
        self.castle_server = castle_server

    def buildProtocol(self, ipv4addr):
        new_protocol = CastleServerProtocol(self.castle_server)
        return new_protocol


class CastleServer:
    """Castle game server class."""
    # Game states
    GAME_STATE_WAITING = 0
    GAME_STATE_READY   = 1
    GAME_STATE_PLAYING = 2
    GAME_STATE_MENU    = 3

    # Payload
    PAYLOAD_TYPE_STATE_CHANGE = "chgstate"

    def __init__(self, port, debug=False):
        self.port = port
        self.players = []           # [conns]
        self.player_states = {}     # {conn: state}

        global DEBUG
        DEBUG = debug

    def start(self):
        # Start listening
        server_protocol_factory = CastleServerProtocolFactory(self)
        endpoint = TCP4ServerEndpoint(reactor, self.port)
        endpoint.listen(server_protocol_factory)
        reactor.run()

    def is_game_on(self):
        if len(self.players) > 0:
            return (self.player_states[self.players[0]] == self.GAME_STATE_PLAYING)
        else:
            return False

    # =================================
    # Command handling and broadcasting
    # =================================
    def is_everyone_ready(self):
        if DEBUG:
            print self.player_states

        if len(self.players) < 2:
            return False

        for player in self.players:
            if self.player_states[player] != self.GAME_STATE_READY:
                return False
        return True

    def broadcast_command(self, origin_protocol, cmd_dict):
        payload = json.dumps(cmd_dict)
        if DEBUG: print payload
        dests = [x for x in self.players if x != origin_protocol]
        for d in dests:
            d.transport.write(payload)

    def broadcast_ready(self):
        payload_dict = {"type": self.PAYLOAD_TYPE_STATE_CHANGE, "state": self.GAME_STATE_PLAYING}
        payload = json.dumps(payload_dict)
        if DEBUG: print payload
        for d in self.players:
            d.transport.write(payload)
