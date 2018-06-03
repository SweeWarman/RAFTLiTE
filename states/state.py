
import sys
sys.path.append("../")

import time
import random
from LcmRaftMessages import *
import enum

class ResponseType(enum.Enum):
    HBEAT_ACK = -1
    APPEND_SUCCESS = 0
    APPEND_FAILURE = 1
    INCORRECT_TERM = 2
    MEMBERSHIP_SUCCESS = 3

class EntryType(enum.Enum):
    HBEAT = 0
    DATA  = 1
    COMMAND = 2
    CONFIGURATION = 3

class State(object):

    def __init__(self):
        self.name = "STATE"

    def set_server(self, server):
        self._server = server
        self._server._expectResponse = False

    def on_message(self, message):
        """This method is called when a message is received,
        and calls one of the other corrosponding methods
        that this state reacts to.

        """

        if (type(message) is heartbeat_t):
            return self.on_heartbeat(message)

        if(type(message) is append_entries_t or type(message) is response_t):
            if (message.term > self._server._currentTerm):
                print "increasing term"
                self._server._currentTerm = message.term

            # Is the messages.term < ours? If so we need to tell
            #   them this so they don't get left behind.
            if (message.term < self._server._currentTerm):
                self._send_response_message(message, ResponseType.INCORRECT_TERM.value)
                print "other server has a lower term"
                return self, None

        if(type(message) is append_entries_t):
            return self.on_append_entries(message)
        elif (type(message) is request_vote_t):
            return self.on_vote_request(message)
        elif (type(message) is vote_response_t):
            return self.on_vote_received(message)
        elif (type(message) is response_t):
            return self.on_response_received(message)
        elif (type(message) is request_membership_t):
            return self.on_membership_request(message)
        elif (type(message) is client_status_t):
            return self.on_client_status(message)

    def on_leader_timeout(self, message):
        """This is called when the leader timeout is reached."""
        return self,None

    def on_vote_request(self, message):
        """This is called when there is a vote request."""
        return self,None

    def on_vote_received(self, message):
        """This is called when this node recieves a vote."""
        return self,None

    def on_append_entries(self, message):
        """This is called when there is a request to
        append an entry to the log.
        """
        return self,None

    def on_heartbeat(self,message):
        """
        :param heartbeat_t message:lcm heartbeat message
        :return:
        """
        return self,None

    def on_response_received(self, message):
        """This is called when a response is sent back to the Leader"""
        return self,None

    def on_membership_request(self,message):
        """Called when a new node makes a membership request"""
        return self,None

    def on_client_status(self, message):
        """This is called when there is a client request."""
        return self,None

    def _nextTimeout(self):
        self._currentTime = time.time()
        return self._currentTime + random.randrange(self._timeout,
                                                    2 * self._timeout)/1000.0

    def _send_response_message(self, msg, arg):

        response = response_t()
        response.sender = self._server._name
        response.receiver = msg.sender
        response.term = self._server._currentTerm
        response.data = arg.value

        self._server.send_message(response)

    def run(self):
        """
        Main functions that a state should perform.
        :return True if state should continue to run,
                False if state transition should occur
        """
