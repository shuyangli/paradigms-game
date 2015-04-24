import argparse
from castle_client import CastleClient
from castle_game import CastleGameGUI

if __name__ == '__main__':
    # Parse command line arguments
    parser = argparse.ArgumentParser(description="Castles game.")
    parser.add_argument("-s", "--server", type=str, dest="host", help="server address", required=True)
    parser.add_argument("-p", "--port", type=int, default=9001, dest="port", help="server port number")
    parser.add_argument("-d", "--debug", action="store_true", dest="debug", help="enable debug mode")
    args = parser.parse_args()

    client = CastleClient(args.debug)
    client.setServer(args.host, args.port)

    game = CastleGameGUI()
    client.setGameGUI(game)
    client.connect()
