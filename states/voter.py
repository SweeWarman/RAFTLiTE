from state import State

import sys
sys.path.append("../")

from Messages.messages import *

class Voter(State):

    def __init__(self):
        self._last_vote = None

    def on_vote_request(self, message):
        if(self._server._currentTerm < message.term):
            self._last_vote = None

        if(self._last_vote is None):
            self._last_vote = message.sender
            self._send_vote_response_message(message)
            print "1. sending vote response to:" + message.sender
        else:
            self._send_vote_response_message(message, yes=False)
            print "2. sending vote response to:" + message.sender
        return self, None

    def _send_vote_response_message(self, msg, yes=True):
        voteResponse = vote_response()
        voteResponse.sender = self._server._name
        voteResponse.receiver = msg.sender
        voteResponse.term = msg.term
        voteResponse.data = yes
        self._server.send_message(voteResponse)
