from castle_client import CastleClient

if __name__ == '__main__':
    debug = True
    client = CastleClient(debug)
    client.setServer("localhost", 9001)
    client.connect()
