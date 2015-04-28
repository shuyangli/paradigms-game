from twisted.internet.protocol import Factory, Protocol
from twisted.internet.endpoints import TCP4ServerEndpoint
from twisted.internet import reactor

from castle_game import CastleGameCommand, CastleGameModel


class CastleServerProtocol(Protocol):
    def __init__(self, server):
        self.server = server

    def connectionMade(self):
        self.server.players.append(self)
        if DEBUG:
            print "New connection from {0}".format(self.transport.getPeer())

    def connectionLost(self, reason):
        self.server.players.remove(self)
        if DEBUG:
            print "Lost connection from {0}".format(self.transport.getPeer())

    def dataReceived(self, data):
        # Receive a command from the client
        if DEBUG:
            print data

        # TODO: Send some actual response back to the client
        # response = data
        # self.transport.write(response)


class CastleServerProtocolFactory(Factory):
    def __init__(self, castle_server):
        self.castle_server = castle_server

    def buildProtocol(self, ipv4addr):
        new_protocol = CastleServerProtocol(self.castle_server)
        return new_protocol


class CastleServer:
    """Castle game server class."""
    def __init__(self, port, debug=False):
        self.port = port
        self.players = []

        global DEBUG
        DEBUG = debug

    def start(self):
        # Start listening
        server_protocol_factory = CastleServerProtocolFactory(self)
        endpoint = TCP4ServerEndpoint(reactor, self.port)
        endpoint.listen(server_protocol_factory)
        reactor.run()
