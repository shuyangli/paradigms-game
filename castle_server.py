from twisted.internet.protocol import Factory, Protocol
from twisted.protocols.basic import LineReceiver
from twisted.internet.endpoints import TCP4ServerEndpoint
from twisted.internet import reactor

from castle_game import CastleGameCommands, CastleGameModel


class CastleServerProtocol(LineReceiver):
    def __init__(self, factory):
        self.factory = factory

    def connectionMade(self):
        self.factory.players.append(self)
        if DEBUG:
            print "New connection from {0}".format(self.transport.getPeer())

    def connectionLost(self, reason):
        self.factory.players.remove(self)
        if DEBUG:
            print "Lost connection from {0}".format(self.transport.getPeer())

    def lineReceived(self, line):
        # Receive a command from the client
        if DEBUG:
            print line

        # TODO: Send some actual response back to the client
        # response = line
        # self.sendLine(response)


class CastleServerProtocolFactory(Factory):
    def __init__(self, castle_server):
        self.castle_server = castle_server
        self.players = []

    def buildProtocol(self, ipv4addr):
        new_protocol = CastleServerProtocol(self)
        return new_protocol


class CastleServer:
    """Castle game server class."""
    def __init__(self, port, debug=False):
        self.port = port
        global DEBUG
        DEBUG = debug

    def start(self):
        # Start listening
        server_protocol_factory = CastleServerProtocolFactory(self)
        endpoint = TCP4ServerEndpoint(reactor, self.port)
        endpoint.listen(server_protocol_factory)
        reactor.run()
