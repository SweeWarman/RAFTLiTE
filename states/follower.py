from voter import Voter
from LcmRaftMessages import *
import time

class Follower(Voter):

    def __init__(self, timeout=5000):
        Voter.__init__(self)
        self._timeout = timeout
        self._timeoutTime = self._nextTimeout()

    def on_append_entries(self, message):
        """
        :param append_entries_t message: lcm append entries message
        :return:
        """

        self._timeoutTime = self._nextTimeout()

        if(message.term < self._server._currentTerm):
            self._send_response_message(message, yes=False)
            return self, None

        return self,None

    def run(self):
        """Follower state should check for the leader timeout"""
        self._currentTime = time.time()
        if self._currentTime > self._timeoutTime:
            return False

        return True