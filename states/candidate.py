
import sys
sys.path.append("../")

from voter import Voter
from leader import Leader
from follower import Follower
import time, random


class Candidate(Voter):
    def __init__(self):
        self.name = "CANDIDATE"

    def set_server(self, server):
        self._server = server
        self._votes = {}
        self._electionStartTime = 0
        self._start_election()

    def on_vote_received(self, message):
        if message.sender not in self._votes.keys():
            self._votes[message.sender] = message

            if(len(self._votes.keys()) > (self._server._total_nodes) / 2):
                leader = Leader(self._server._currentTerm)
                leader.set_server(self._server)
                print "Server: " + self._server._name + " is leader for term:" + str(self._server._currentTerm)
                return leader, None

        return self, None

    def on_append_entries(self, message):
        print "Server: " + self._server._name + "is transitioning to a follower"
        follower = Follower()
        follower.set_server(self._server)
        return follower, None

    def _start_election(self):
        self._server._currentTerm += 1
        self._electionStartTime = time.time()
        self._votes[self._server._name] = []
        self._last_vote = self._server._name
        for node in self._server._connectedServers:
            if node == self._server._name:
                continue
            election = request_vote_t()
            election.sender = self._server._name
            election.receiver = node
            election.term = self._server._currentTerm
            self._server.send_message(election)
            #print self._server._name + ": requesting votes from: " + node




    def run(self):

        if time.time() - self._electionStartTime > random.randrange(1000,2000)/1000.0:
            print "Election timeout: restarting election"
            self._votes = {}
            if self._server._total_nodes > 1:
                self._start_election()
            else:
                return False
        return True





