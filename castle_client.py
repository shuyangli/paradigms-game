from twisted.internet.protocol import Factory, ClientFactory, Protocol
from twisted.protocols.basic import LineReceiver
from twisted.internet.task import LoopingCall   # Let Twisted run main loop
from twisted.internet import reactor, defer

from castle_game import CastleGameCommand, CastleGameModel

import json     # For serializing dicts
import time     # time
import sys      # exit


class CastleClientProtocol(LineReceiver):
    PAYLOAD_TYPE_COMMAND = "cmd"
    PAYLOAD_TYPE_STATE_CHANGE = "cs"
    PAYLOAD_TYPE_ALL_POSITION = "ap"
    PAYLOAD_TYPE_SELECT_POSITION = "sp"
    PAYLOAD_TYPE_LOCKSTEP_FINISH = "lkf"
    PAYLOAD_TYPE_LOCKSTEP_ALLOW = "lka"
    PAYLOAD_TYPE_ERROR = "err"

    def __init__(self, client):
        self.client = client

    def connectionMade(self):
        if DEBUG: print "[INFO] Connection made with server:{0}".format(self.transport.getPeer())
        self.client.conn = self

    def connectionLost(self, reason):
        if DEBUG: print "[INFO] Connection lost from server:{0}".format(self.transport.getPeer())
        self.client.conn = None
        # TODO (SL): this should be a fatal error

    def lineReceived(self, line):
        # Received a response from the server
        ddict = json.loads(line)
        if DEBUG: self.__logDumpLine(ddict)

        if ddict["type"] == self.PAYLOAD_TYPE_ERROR:
            # error: {"type": "err", "info": info}
            pass

        elif ddict["type"] == self.PAYLOAD_TYPE_COMMAND:
            # game command: {"type": "cmd", "lturn": cmd_dict["turn"], "cmd": cmd_dict["command"].serialize()}
            # cmd_dict: {"turn": turn, "command": cmd}
            cmd_dict = {"turn": ddict["lturn"], "command": CastleGameCommand.decode_command(ddict["cmd"])}
            self.client.receive_game_command(cmd_dict)

        elif ddict["type"] == self.PAYLOAD_TYPE_STATE_CHANGE:
            # state change: {"type": "cs", "state": state}
            # DEBUG
            if ddict["state"] == self.client.GAME_STATE_PLAYING:
                self.client.change_state_start_game()

        elif ddict["type"] == self.PAYLOAD_TYPE_ALL_POSITION:
            # all position: {"type": "ap", "ownpos": ownpos, "allpos": [pos]}
            self.client.receive_pos(ddict["ownpos"], ddict["allpos"])

        elif ddict["type"] == self.PAYLOAD_TYPE_LOCKSTEP_ALLOW:
            # allow lockstep: {"type": "lka", "step": lockstep}
            self.client.receive_allowed_lockstep(ddict["step"])

    def sendCommandDict(self, cmd_dict):
        # cmd_dict: {"turn": turn, "command": cmd}
        # final dict: {"type": "cmd", "lturn": cmd_dict["turn"], "cmd": cmd_dict["command"].serialize()}
        final_cmd = {"type": self.PAYLOAD_TYPE_COMMAND,
                     "lturn": cmd_dict["turn"],
                     "cmd": cmd_dict["command"].serialize()}
        payload = json.dumps(final_cmd)
        if DEBUG: self.__logDumpPayload(final_cmd)
        self.sendLine(payload)

    def sendPosSelection(self, pos):
        # select position: {"type": "sp", "pos": pos}
        pos_dict = {"type": self.PAYLOAD_TYPE_SELECT_POSITION,
                    "pos": pos}
        payload = json.dumps(pos_dict)
        if DEBUG: self.__logDumpPayload(pos_dict)
        self.sendLine(payload)

    def sendStateChange(self, state):
        # state change: {"type": "cs", "state": state}
        change_dict = {"type": self.PAYLOAD_TYPE_STATE_CHANGE,
                       "state": state}
        payload = json.dumps(change_dict)
        if DEBUG: self.__logDumpPayload(change_dict)
        self.sendLine(payload)

    def sendLockstepFinish(self, lockstep):
        # lockstep finish: {"type": "lkf", "step": lockstep}
        step_dict = {"type": self.PAYLOAD_TYPE_LOCKSTEP_FINISH,
                     "step": lockstep}
        payload = json.dumps(step_dict)
        if DEBUG: self.__logDumpPayload(payload)
        self.sendLine(payload)

    def __logDumpPayload(self, payload):
        print "[INFO][SEND] {0}".format(payload)

    def __logDumpLine(self, line):
        print "[INFO][RECV] {0}".format(line)



class CastleClientProtocolFactory(ClientFactory):
    def __init__(self, castle_client):
        self.castle_client = castle_client

    def buildProtocol(self, ipv4addr):
        new_protocol = CastleClientProtocol(self.castle_client)
        return new_protocol


class CastleClient:
    """Castle game client class."""
    # FPS requested
    DESIRED_FPS = 30.0

    # 10 game frames per lockstep, 6 locksteps per second
    # Realistically this would change based on network latency
    GAME_FRAMES_PER_LOCK_STEP = 5

    # Game states
    GAME_STATE_WAITING = 0
    GAME_STATE_READY   = 1
    GAME_STATE_PLAYING = 2
    GAME_STATE_MENU    = 3

    GAME_STATE_INSTRUCTIONS = 4
    GAME_STATE_FINISH = 5

    # For synchronized ticking mechanism
    lock_step_id = 0


    def __init__(self, debug=False):
        self.current_state = self.GAME_STATE_MENU
        self.pending_commands = []  # [{"turn": turn, "command": cmd}]
        self.conn = None

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

    def exit(self):
        reactor.stop()

    # ==================
    # Game state changes
    # ==================
    def change_state_menu(self):
        self.game_ui.transition_to_menu()
        self.current_state = self.GAME_STATE_MENU
        self.conn.sendStateChange(self.current_state)

    def change_state_instructions(self):
        self.game_ui.transition_to_instructions()
        self.current_state = self.GAME_STATE_INSTRUCTIONS

    def change_state_waiting(self):
        self.own_position = None
        self.taken_positions = []
        self.game_ui.transition_to_waiting()
        self.current_state = self.GAME_STATE_WAITING
        self.conn.sendStateChange(self.current_state)

    def change_state_ready(self):
        self.game_ui.transition_to_ready()
        self.current_state = self.GAME_STATE_READY
        self.conn.sendStateChange(self.current_state)

    def change_state_start_game(self):
        self.game_ui.start_game(self.taken_positions, self.own_position)
        self.game_ui.transition_to_playing()
        self.current_state = self.GAME_STATE_PLAYING
        self.conn.sendStateChange(self.current_state)

        self.game_frame_id = 0
        self.allowed_lockstep = 2

        # DEBUG
        if DEBUG:
            self.last_time_lockstep = time.time()
            self.last_time_ui = time.time()

    def change_state_finish(self):
        self.game_ui.transition_to_finish()
        self.current_state = self.GAME_STATE_FINISH
        self.conn.sendStateChange(self.current_state)

    def change_state_end_game(self):
        self.current_state = self.GAME_STATE_MENU
        self.conn.sendStateChange(self.current_state)

    # ==========================
    # Meta game command handling
    # ==========================
    def select_pos(self, pos):
        self.conn.sendPosSelection(pos)

    def receive_pos(self, ownpos, allpos):
        self.own_position = ownpos
        self.taken_positions = allpos

    def receive_allowed_lockstep(self, step):
        self.allowed_lockstep = step

    # =====================
    # Game command handling
    # =====================
    def queue_command(self, cmd):
        # Queue command to be executed AFTER the NEXT lockstep
        cmd_dict = {"turn": self.lock_step_id + 2, "command": cmd}
        self.pending_commands.append(cmd_dict)
        self.conn.sendCommandDict(cmd_dict)

    def receive_game_command(self, cmd_dict):
        self.pending_commands.append(cmd_dict)

    @property
    def ready_commands(self):
        # Compute commands that are ready to be executed in the CURRENT lockstep
        return [x for x in self.pending_commands if x["turn"] == self.lock_step_id]

    # =================
    # Ticking mechanism
    # =================
    def tick_lock_step(self):
        # Called every lock step, simulate actual game
        # Check if it's ready first, and return false if it's not ready to advance
        self.lock_step_id += 1
        if self.lock_step_id >= self.allowed_lockstep:
            self.lock_step_id -= 1
            return False

        if DEBUG: print "[INFO][TICK] {0}".format(self.lock_step_id)

        for cmd in self.ready_commands:
            if DEBUG: print "[INFO][CMD] {0}".format(cmd)
            cmd["command"].apply_to(self.game_model)
            self.pending_commands.remove(cmd)

        # tick lock step for model
        self.game_model.tick_lock_step()

        # message server to prevent desync
        self.conn.sendLockstepFinish(self.lock_step_id)

        # DEBUG: fps
        if DEBUG:
            current_time = time.time()
            print "[INFO] Lockstep FPS: {0}".format(1 / (current_time - self.last_time_lockstep))
            self.last_time_lockstep = current_time

        return True

    def tick_ui(self):
        # Dispatcher for UI tick
        if self.current_state == self.GAME_STATE_MENU:
            self.game_ui.ui_tick_menu()
        elif self.current_state == self.GAME_STATE_INSTRUCTIONS:
            self.game_ui.ui_tick_instructions()
        elif self.current_state == self.GAME_STATE_WAITING:
            self.game_ui.ui_tick_waiting()
        elif self.current_state == self.GAME_STATE_READY:
            self.game_ui.ui_tick_ready()
        elif self.current_state == self.GAME_STATE_PLAYING:

            # First process lockstep stuff
            if self.game_frame_id == 0:
                # Every first game frame, we advance the lock step
                if not self.tick_lock_step():
                    # If we failed to tick lockstep, make sure we try to tick again
                    self.game_frame_id -= 1

            # Increment game frame
            self.game_frame_id += 1
            if self.game_frame_id >= self.GAME_FRAMES_PER_LOCK_STEP:
                self.game_frame_id = 0

            self.game_ui.ui_tick_game()

        elif self.current_state == self.GAME_STATE_FINISH:
            self.game_ui.ui_tick_finish()

            # DEBUG: fps
            # if DEBUG:
            #     current_time = time.time()
            #     print "[INFO] UI FPS: {0}".format(1 / (current_time - self.last_time_ui))
            #     self.last_time_ui = current_time
        else:
            # Something bad occured
            print "[ERROR] Invalid current state"
