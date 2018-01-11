from voter import Voter
from leader import Leader
from LcmRaftMessages import *
from follower import Follower
import time, random


class Candidate(Voter):

    def set_server(self, server):
        self._server = server
        self._votes = {}
        self._electionStartTime = 0
        self._start_election()

    def on_vote_request(self, message):
        return self, None

    def on_vote_received(self, message):
        if message.sender not in self._votes:
            self._votes[message.sender] = message

            if(len(self._votes.keys()) > (self._server._total_nodes - 1) / 2):
                leader = Leader()
                leader.set_server(self._server)
                print "Server: " + self._server.get_name() + "is leader for term:" + self._server._currentTerm
                return leader, None
        return self, None

    def on_append_entries(self, message):
        follower = Follower()
        follower.set_server(self._server)
        return follower, None

    def _start_election(self):
        self._server._currentTerm += 1
        self._electionStartTime = time.time()
        election = request_vote_t()
        election.sender = self._server._name
        election.term = self._server._currentTerm
        self._server.send_message(election)
        self._last_vote = self._server._name

    def run(self):

        if time.time() - self._electionStartTime > random.randrange(1000,2000)/1000.0:
            print "Election timeout: restarting election"
            self._votes = {}
            self._start_election()



