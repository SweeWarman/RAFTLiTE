import time
import random
from LcmRaftMessages import *

class State(object):

    def set_server(self, server):
        self._server = server

    def on_message(self, message):
        """This method is called when a message is received,
        and calls one of the other corrosponding methods
        that this state reacts to.

        """

        if (message.term > self._server._currentTerm):
            self._server._currentTerm = message.term
        # Is the messages.term < ours? If so we need to tell
        #   them this so they don't get left behind.
        elif (message.term < self._server._currentTerm):
            self._send_response_message(message, yes=False)
            return self, None


        if (type(message) is heartbeat_t):
            return self.on_heartbeat(message)
        elif(type(message) is append_entries_t):
            return self.on_append_entries(message)
        elif (type(message) is request_vote_t):
            a = self.on_vote_request(message)
            return a
        elif (type(message) is vote_response_t):
            return self.on_vote_received(message)
        elif (type(message) is response_t):
            return self.on_response_received(message)

    def on_leader_timeout(self, message):
        """This is called when the leader timeout is reached."""

    def on_vote_request(self, message):
        """This is called when there is a vote request."""

    def on_vote_received(self, message):
        """This is called when this node recieves a vote."""

    def on_append_entries(self, message):
        """This is called when there is a request to
        append an entry to the log.

        """
    def on_heartbeat(self,message):
        """
        :param heartbeat_t message:lcm heartbeat message
        :return:
        """
        if message.sender not in self._server._connectedServer:
            self._server._connectedServer.append(message.sender)
            self._server._total_nodes = self._server._total_nodes + 1

    def on_response_received(self, message):
        """This is called when a response is sent back to the Leader"""

    def on_client_command(self, message):
        """This is called when there is a client request."""

    def _nextTimeout(self):
        self._currentTime = time.time()
        return self._currentTime + random.randrange(self._timeout,
                                                    2 * self._timeout)/1000.0

    def _send_response_message(self, msg, yes=True):

        response = response_t()
        response.sender = self._server._name
        response.receiver = msg.sender
        response.term = self._server._currentTerm
        response.data = yes

        self._server.send_message_response(response)

    def run(self):
        """Main functions that a state should perform"""
