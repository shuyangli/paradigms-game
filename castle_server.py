from twisted.internet.protocol import Factory, Protocol
from twisted.internet.endpoints import TCP4ServerEndpoint
import twisted.internet.reactor as reactor


class CastleServerProtocol(Protocol):
    def __init__(self, factory):
        self.factory = factory

    def connectionMade(self):
        print "New connection"

    def connectionLost(self, reason):
        print "Lost connection"

    def dataReceived(self, data):
        # Receive a command from the client
        print data


class CastleServerProtocolFactory(Factory):
    def __init__(self, castle_server):
        self.castle_server = castle_server

    def buildProtocol(self, ipv4addr):
        new_protocol = CastleServerProtocol(self)
        return new_protocol


class CastleServer:
    def __init__(self, port, debug=False):
        self.port = port
        self.debug = debug

    def start(self):
        # Start listening
        server_protocol_factory = CastleServerProtocolFactory(self)
        endpoint = TCP4ServerEndpoint(reactor, self.port)
        endpoint.listen(server_protocol_factory)
        reactor.run()
