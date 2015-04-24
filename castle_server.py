from twisted.internet.protocol import Factory, Protocol
from twisted.internet.endpoints import TCP4ServerEndpoint
import twisted.internet.reactor as reactor


class CastleServerProtocol(Protocol):
    def __init__(self, factory):
        self.factory = factory

    def connectionMade(self):
        pass

    def connectionLost(self, reason):
        pass

    def dataReceived(self, data):
        # Receive a command from the client
        pass


class CastleServerProtocolFactory(Factory):
    def __init__(self, castle_server):
        super(CastleServerProtocolFactory, self).__init__()
        self.castle_server = castle_server

    def buildProtocol(self, ipv4addr):
        new_protocol = CastleServerProtocol(self)
        return new_protocol


class CastleServer(object):
    def __init__(self, port, debug=False):
        super(CastleServer, self).__init__()
        self.port = port
        self.debug = debug

    def start():
        # Start listening
        server_protocol_factory = CastleServerProtocolFactory(self)
        endpoint = TCP4ServerEndpoint(reactor, self.port)
        endpoint.listen(server_protocol_factory)
        reactor.run()
