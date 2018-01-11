from LcmRaftMessages import *
from states.candidate import Candidate
import threading

class Server(threading.Thread):

    def __init__(self, name, state, lc):
        threading.Thread.__init__(self)
        self.threadLock = threading.Lock()
        self._name = name
        self._state = state
        self._total_nodes = 0
        self._lc = lc
        self._state.set_server(self)
        self._currentTerm = 0
        self._connectedServers = []

    def send_message(self, message):
        if type(message) is heartbeat_t:
            hbeat = message # type: heartbeat_t
            self._lc.publish("HEARTBEAT",hbeat.encode())
        elif type(message) is append_entries_t:
            entry = message # type: append_entries_t
            self._lc.publish("APPEND_ENTRIES",entry.encode())
        elif type(message) is request_vote_t:
            reqvote = message # type: request_vote_t
            self._lc.publish("REQUEST_VOTE",reqvote.encode())
        elif type(message) is vote_response_t:
            voteresponse = message # type: vote_response_t
            self._lc.publish("VOTE_RESPONSE",voteresponse.encode())
        elif type(message) is response_t:
            response = message # type: response_t
            self._lc.publish("RESPONSE",response.encode())

    def on_message(self, message):
        state, response = self._state.on_message(message)

        self.threadLock.acquire()
        self._state = state
        self.threadLock.release()

    def run(self):
        while True:
            status = self._state.run()

            if status == False:
                self.threadLock.acquire()
                print self._name+" is transitioning to a candidate"
                candidate = Candidate()
                candidate.set_server(self)
                self._state = candidate
                self.threadLock.release()
