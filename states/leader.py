from state import State
from LcmRaftMessages import *

class Leader(State):

    def __init__(self):
        self._prev_entry_time = 0
        pass

    def set_sever(self, server):
        self._sever = server
        self._send_heart_beat()

    def on_response_received(self, message):

        return self, None

    def _send_append_entries(self):
        message = append_entries_t()
        message.sender = self._sever._name
        message.receiver = None
        message.term = self._server._currentTerm
        self._server.send_message(message)

    def run(self):
        if self._currentTime - self._prev_entry_time > 0.250:
            self._send_append_entries()