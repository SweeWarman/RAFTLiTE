from state import State
import time

from LcmRaftMessages import *

class Neutral(State):

    def __init__(self):
        """neutral state"""
        self.prev_hbeat_time = 0

    def run(self):

        currentTime = time.time()
        if currentTime > self.prev_hbeat_time > 0.5:
            hbeat = heartbeat_t()
            hbeat.sender = self._server._name
            self._server.send_message(hbeat)
            self.prev_hbeat_time = currentTime
