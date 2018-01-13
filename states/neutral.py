
from state import State,ResponseType
from follower import Follower
import time


from ..LcmRaftMessages import *

class Neutral(State):

    def __init__(self):
        """neutral state"""
        self.prev_hbeat_time = 0
        self.numServers = 1
        self.newServerDiscoveredTime = 0
        self.entryRequestMade = False
        self.entryRequestServer = ""


    def on_heartbeat(self,message):
        if message.sender not in self._server._availableServers:
            self._server._availableServers.append(message.sender)
            print "discovered new server:" + message.sender

        return self, None

    def on_append_entries(self, message):
        """
        :param append_entries_t message: lcm append entries message
        :return:
        """
        if self.entryRequestMade is False:
            entry = request_membership_t()
            entry.sender = self._server._name
            entry.receiver = message.sender
            entry.request = True
            print "sending membership request to: " + self.entryRequestServer
            self._server.send_message(entry)
            self.entryRequestMade = True
            self.entryRequestServer = message.sender


        return self, None

    def on_response_received(self, message):

        if self.entryRequestMade:
            if self.entryRequestServer == message.sender and message.data == ResponseType.MEMBERSHIP_SUCCESS.value:
                follower = Follower()
                follower.set_server(self._server)
                print self._server._name + ": becoming a follower to " + message.sender
                return follower,None

        return self,None


    def run(self):

        currentTime = time.time()
        if (currentTime - self.prev_hbeat_time) > 0.5:
            hbeat = heartbeat_t()
            hbeat.sender = self._server._name
            self._server.send_message(hbeat)
            self.prev_hbeat_time = currentTime

        if len(self._server._availableServers) > 1:
            if self.numServers < len(self._server._availableServers):
                self.newServerDiscoveredTime = currentTime
                self.numServers = len(self._server._availableServers)

            if (currentTime - self.newServerDiscoveredTime) > 2:
                print "Exiting Neutral State"
                self._server._connectedServers[:] = self._server._availableServers[:]
                self._server._total_nodes = len(self._server._connectedServers)
                return False

        return True
