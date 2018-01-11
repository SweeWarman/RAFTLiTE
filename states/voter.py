from state import State

from LcmRaftMessages import *

class Voter(State):

    def __init__(self):
        self._last_vote = None

    def on_vote_request(self, message):
        if(self._last_vote is None):
            self._last_vote = message.sender
            self._send_vote_response_message(message)
        else:
            self._send_vote_response_message(message, yes=False)

        return self, None

    def _send_vote_response_message(self, msg, yes=True):
        voteResponse = vote_response_t()
        voteResponse.sender = self._server._name
        voteResponse.receiver = msg.sender
        voteResponse.term = msg.term
        voteResponse.data = yes
        self._server.send_message_response(voteResponse)
