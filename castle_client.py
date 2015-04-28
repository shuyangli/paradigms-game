from twisted.internet.protocol import Factory, ClientFactory, Protocol
from twisted.internet.task import LoopingCall   # Let Twisted run main loop
from twisted.internet import reactor

from castle_game import CastleGameCommand, CastleGameModel


class CastleClientProtocol(Protocol):
    def __init__(self, client):
        self.client = client

    def connectionMade(self):
        pass

    def connectionLost(self, reason):
        pass

    def dataReceived(self, data):
        # Received a response from the server
        if DEBUG:
            print data


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

        self.ready_commands = []
        self.pending_commands = []

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
        pass

    # =================
    # Ticking mechanism
    # =================
    def tick_lock_step(self):
        # Called every lock step (~10 fps), simulate actual game
        # Check if it's ready first, and return false if it's not ready to advance
        print "Lock step tick"

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
