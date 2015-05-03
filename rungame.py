import argparse
from castle_client import CastleClient
from castle_game_ui import CastleGameUI

class FakeConnection:
    def sendStateChange(self, *args, **kwargs): pass
    def sendCommandDict(self, *args, **kwargs): pass


if __name__ == '__main__':
    # Parse command line arguments
    parser = argparse.ArgumentParser(description="Castles game.")
    parser.add_argument("-s", "--server", type=str, dest="server", help="server address", required=True)
    parser.add_argument("-p", "--port", type=int, default=9001, dest="port", help="server port number")
    parser.add_argument("-d", "--debug", action="store_true", dest="debug", help="enable debug mode")
    parser.add_argument("--testdraw", action="store_true", dest="testdraw", help="enable testing mode to test game drawing")
    args = parser.parse_args()

    client = CastleClient(args.debug)
    client.set_server(args.server, args.port)

    game_ui = CastleGameUI(args.debug)
    game_ui.set_client(client)
    client.set_game_gui(game_ui)

    if args.testdraw:
        client.current_state = client.GAME_STATE_PLAYING
        client.taken_positions = [1]
        client.own_position = 1
        client.conn = FakeConnection()
        client.change_state_start_game()

    client.connect()
