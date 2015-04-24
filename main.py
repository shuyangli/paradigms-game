import argparse
from castle_server import CastleServer

if __name__ == '__main__':
    # Parse command line arguments
    parser = argparse.ArgumentParser(description="Server for Castles game.")
    parser.add_argument("-p", "--port", type=int, default=9001, dest="port", help="port number")
    parser.add_argument("-d", "--debug", action="store_true", dest="debug", help="enable debug mode")
    args = parser.parse_args()

    # Run server
    server = CastleServer(args.port, args.debug)
    server.start()
