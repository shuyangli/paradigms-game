from twisted.internet.protocol import Factory, Protocol
from twisted.internet.endpoints import TCP4ServerEndpoint
from twisted.internet import reactor

from castle_game import CastleGameCommand, CastleGameModel

import json


class CastleServerProtocol(Protocol):
    PAYLOAD_TYPE_COMMAND = "cmd"
    PAYLOAD_TYPE_STATE_CHANGE = "chgstate"
    PAYLOAD_TYPE_ALL_POSITION = "allpos"
    PAYLOAD_TYPE_SELECT_POSITION = "selpos"
    PAYLOAD_TYPE_ERROR = "error"

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
            print "Player states: {0}".format(self.server.player_states)

    def connectionLost(self, reason):
        if self in self.server.players:
            self.server.players.remove(self)
            self.server.player_states.pop(self, None)
        if DEBUG:
            print "Lost connection from {0}".format(self.transport.getPeer())
            print "Reason: {0}".format(reason)

    def __logDumpPayload(self, payload):
        print "[INFO] To {0}: {1}".format(self.transport.getPeer(), payload)

    def __logDumpData(self, data):
        print "[INFO] From {0}: {1}".format(self.transport.getPeer(), data)

    # ==============
    # Active actions
    # ==============
    def rejectClient(self):
        # rejection: {"type": "error", "info": "game is on"}
        ddict = {"type": self.PAYLOAD_TYPE_ERROR, "info": "Game is currently on"}
        payload = json.dumps(ddict)
        if DEBUG: self.__logDumpPayload(payload)
        self.transport.write(payload)
        self.transport.loseConnection()

    def sendPosition(self):
        all_positions = [i for i, conn in enumerate(self.server.player_pos) if conn != None]
        own_position = None
        if self in self.server.player_pos:
            own_position = self.server.player_pos.index(self)

        # position: {"type": "allpos", "ownpos": ownpos, "allpos": [allpos]}
        payload_dict = {"type": self.PAYLOAD_TYPE_ALL_POSITION,
                        "ownpos": own_position,
                        "allpos": all_positions}
        payload = json.dumps(payload_dict)
        if DEBUG: self.__logDumpPayload(payload)
        self.transport.write(payload)

    def sendState(self, state):
        payload_dict = {"type": self.PAYLOAD_TYPE_STATE_CHANGE, "state": state}
        payload = json.dumps(payload_dict)
        if DEBUG: self.__logDumpPayload(payload)
        self.transport.write(payload)

    # ==============================
    # Passive action (data received)
    # ==============================
    def dataReceived(self, data):
        # Receive a command from the client
        if DEBUG: self.__logDumpData(data)

        ddict = json.loads(data)
        if ddict["type"] == self.PAYLOAD_TYPE_COMMAND:
            # game command: {"type": "cmd", "lturn": cmd_dict["turn"], "cmd": cmd_dict["command"].serialize()}
            # broadcast command
            self.server.broadcast_command(self, ddict)

        elif ddict["type"] == self.PAYLOAD_TYPE_STATE_CHANGE:
            # state change: {"type": "chgstate", "state": state}
            # change state
            self.server.player_change_state(self, int(ddict["state"]))
            # if everyone is ready, broadcast game start
            if self.server.is_everyone_ready():
                # TODO: countdown
                self.server.broadcast_ready()

        elif ddict["type"] == self.PAYLOAD_TYPE_SELECT_POSITION:
            # select position: {"type": "selpos", "pos": pos}
            pos = int(ddict["pos"])
            if self.server.player_select_position(self, pos):
                self.server.broadcast_position()
            else:
                self.sendPosition()


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
    PAYLOAD_TYPE_ALL_POSITION = "allpos"

    def __init__(self, port, debug=False):
        self.port = port
        self.players = []           # [conns]
        self.player_states = {}     # {conn: state}
        self.player_pos = [None, None, None, None] # [conns]

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

    def __logDumpPayload(self, payload):
        print "[INFO] Broadcast msg: {0}".format(payload)

    # ==============
    # Player actions
    # ==============
    def player_select_position(self, origin_protocol, pos):
        if pos >= 0 and pos < len(self.player_pos) and self.player_pos[pos] == None:
            # successfully selected position
            if origin_protocol in self.player_pos:
                original_pos = self.player_pos.index(origin_protocol)
                self.player_pos[original_pos] = None
            self.player_pos[pos] = origin_protocol
            return True
        else:
            return False

    def player_change_state(self, player, state):
        self.player_states[player] = state
        if state == self.GAME_STATE_WAITING:
            player.sendPosition()

    # =================================
    # Command handling and broadcasting
    # =================================
    def is_everyone_ready(self):
        if DEBUG: print "All player states: {0}".format(self.player_states)

        if len(self.players) < 2:
            return False

        for player in self.players:
            if self.player_states[player] != self.GAME_STATE_READY:
                return False
        return True

    def broadcast_command(self, origin_protocol, cmd_dict):
        payload = json.dumps(cmd_dict)
        if DEBUG: self.__logDumpPayload(payload)
        dests = [x for x in self.players if x != origin_protocol]
        for d in dests:
            d.transport.write(payload)

    def broadcast_position(self):
        waiting_players = [x for x in self.players if self.player_states[x] == self.GAME_STATE_WAITING or self.player_states[x] == self.GAME_STATE_READY]

        for player in waiting_players:
            player.sendPosition()

    def broadcast_ready(self):
        for player in self.players:
            player.sendState(self.GAME_STATE_PLAYING)
