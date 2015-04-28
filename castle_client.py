from twisted.internet.protocol import Factory, ClientFactory, Protocol
from twisted.internet.task import LoopingCall   # Let Twisted run main loop
from twisted.internet import reactor

from castle_game import CastleGameCommand, CastleGameModel

import json                     # For serializing dicts


class CastleClientProtocol(Protocol):
    PAYLOAD_TYPE_COMMAND = "cmd"

    def __init__(self, client):
        self.client = client

    def connectionMade(self):
        if DEBUG:
            print "Connection made with server:{0}".format(self.transport.getPeer())
        self.client.conn = self

    def connectionLost(self, reason):
        if DEBUG:
            print "Connection lost from server:{0}".format(self.transport.getPeer())
        self.client.conn = None

    def dataReceived(self, data):
        # Received a response from the server
        if DEBUG:
            print data
        ddict = json.loads(data)

    def sendCommandDict(self, cmd_dict):
        # cmd_dict: {"turn": turn, "command": cmd}
        # final dict: {"type": "cmd", "lturn": cmd_dict["turn"], "cmd": cmd_dict["command"].serialize()}
        final_cmd = {
            "type": self.PAYLOAD_TYPE_COMMAND,
            "lturn": cmd_dict["turn"],
            "cmd": cmd_dict["command"].serialize()
        }
        print final_cmd
        self.transport.write(json.dumps(final_cmd))


class CastleClientProtocolFactory(ClientFactory):
    def __init__(self, castle_client):
        self.castle_client = castle_client

    def buildProtocol(self, ipv4addr):
        new_protocol = CastleClientProtocol(self.castle_client)
        return new_protocol


class CastleClient:
    """Castle game client class."""
    # FPS requested
    # NOTE (SL): this is 50 instead of 60 to avoid floating point division
    DESIRED_FPS = 50.0

    # Game states
    GAME_STATE_WAITING = 0
    GAME_STATE_READY   = 1
    GAME_STATE_PLAYING = 2
    GAME_STATE_MENU    = 3

    # For synchronized ticking mechanism
    lock_step_id = 0


    def __init__(self, debug=False):
        self.current_state = self.GAME_STATE_PLAYING
        self.pending_commands = []  # [{"turn": turn, "command": cmd}]
        self.conn = None

        global DEBUG
        DEBUG = debug

    def set_server(self, host, port):
        self.server_host = host
        self.server_port = port

    def set_game_gui(self, game_ui):
        self.game_ui = game_ui
        self.ui_tick_call = LoopingCall(self.tick_ui)
        self.ui_tick_call.start(1.0 / self.DESIRED_FPS)

    def set_game_model(self, model):
        self.game_model = model

    def connect(self):
        client_protocol_factory = CastleClientProtocolFactory(self)
        reactor.connectTCP(self.server_host, self.server_port, client_protocol_factory)
        reactor.run()

    # ================
    # Command handling
    # ================
    def queue_command(self, cmd):
        # Queue command to be executed AFTER the NEXT lockstep
        cmd_dict = {"turn": self.lock_step_id + 2, "command": cmd}
        self.pending_commands.append(cmd_dict)
        self.conn.sendCommandDict(cmd_dict)

    @property
    def ready_commands(self):
        # Compute commands that are ready to be executed in the CURRENT lockstep
        cmds = [x for x in self.pending_commands if x["turn"] == self.lock_step_id]
        for c in cmds:
            self.pending_commands.remove(c)

        return cmds

    # =================
    # Ticking mechanism
    # =================
    def tick_lock_step(self):
        # Called every lock step (~10 fps), simulate actual game
        # Check if it's ready first, and return false if it's not ready to advance
        self.lock_step_id += 1
        for cmd in self.ready_commands:
            self.game_model.apply_command(cmd)
        return True

    def tick_ui(self):
        # Dispatcher for UI tick
        if self.current_state == self.GAME_STATE_MENU:
            self.game_ui.ui_tick_menu()
        elif self.current_state == self.GAME_STATE_WAITING:
            self.game_ui.ui_tick_waiting()
        elif self.current_state == self.GAME_STATE_READY:
            self.game_ui.ui_tick_ready()
        elif self.current_state == self.GAME_STATE_PLAYING:
            self.game_ui.ui_tick_game()
        else:
            # Something bad occured
            print "Bad current state"
