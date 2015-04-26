from twisted.internet.protocol import Factory, ClientFactory, Protocol
from twisted.protocols.basic import LineReceiver
from twisted.internet.task import LoopingCall   # Let Twisted run main loop
from twisted.internet import reactor

from castle_game import CastleGameCommands, CastleGameModel


class CastleClientProtocol(LineReceiver):
    def __init__(self, client):
        self.client = client

    def connectionMade(self):
        pass

    def connectionLost(self, reason):
        pass

    def lineReceived(self, line):
        # Received a response from the server
        if DEBUG:
            print line


class CastleClientProtocolFactory(ClientFactory):
    def __init__(self, castle_client):
        self.castle_client = castle_client

    def buildProtocol(self, ipv4addr):
        new_protocol = CastleClientProtocol(self.castle_client)
        return new_protocol


class CastleClient:
    """Castle game client class."""
    DESIRED_FPS = 60.0      # FPS requested

    def __init__(self, debug=False):
        global DEBUG
        DEBUG = debug

    def setServer(self, host, port):
        self.server_host = host
        self.server_port = port

    def setGameGUI(self, game):
        self.game = game
        self.ui_tick = LoopingCall(game.tick)
        self.ui_tick.start(1.0 / self.DESIRED_FPS)

    def connect(self):
        client_protocol_factory = CastleClientProtocolFactory(self)
        reactor.connectTCP(self.server_host, self.server_port, client_protocol_factory)
        reactor.run()
