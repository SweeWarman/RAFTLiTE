from ..states.follower import Follower
from ..states.neutral import Neutral
from ..states.candidate import Candidate
from ..states.leader import Leader
import threading

class Server():

    def __init__(self, name, state, log, board):
        self.threadLock = threading.Lock()
        self._name = name
        self._state = state
        self._total_nodes = 1
        self._board = board
        self._currentTerm = 0
        self._connectedServers = []
        self._availableServers = []
        self._availableServers.append(self._name)
        self._connectedServers.append(self._name)
        self._log = log
        self._commitIndex = 0
        self._lastLogIndex = 0
        self._lastLogTerm = None
        self._leader = None
        self._shutdown = False
        self._shutdownRequest = False
        self._expectResponse = False #TODO: hack - this should go away if you implement the cluster membership part.
        self._state.set_server(self)

    def send_message(self, message):
        self._board.send_message(message)

    def on_message(self, message):

        if message is None:
            return

        if self._shutdown is True:
            return

        #print "on message waiting"
        self.threadLock.acquire()
        #print "on message acquired"
        state, response = self._state.on_message(message)
        self._state = state
        self.threadLock.release()
        #print "on message released"

    def get_last_commited_log_entry(self):
        if len(self._log) > 0:
            self.threadLock.acquire()
            entry = self._log[self._commitIndex-1]
            self.threadLock.release()
            return entry
        else:
            return None

    def get_last_log_entry(self):
        if len(self._log) > 0:
            self.threadLock.acquire()
            entry = self._log[-1]
            self.threadLock.release()
            return entry
        else:
            return None

    def get_log(self):
        self.threadLock.acquire()
        log = self._log[:]
        self.threadLock.release()
        return log

    def clear_log(self):
        self.threadLock.acquire()
        self._log = []
        self._commitIndex = 0
        self._lastLogIndex = 0
        self._lastLogTerm = None
        self._state.set_server(self)
        self.threadLock.release()

    def run(self):

        if self._shutdown == False:
            #print "run waiting for lock"
            self.threadLock.acquire()
            #print "run acquired lock"
            status = self._state.run()

            if status == False:
                if type(self._state) is Follower:
                    self._leader = None
                    print self._name+" is transitioning to a candidate"
                    candidate = Candidate()
                    candidate.set_server(self)
                    self._state = candidate
                elif (type(self._state) is Neutral) or (type(self._state) is Leader):
                    self._leader = None
                    print self._name + " is transitioning to a follower"
                    follower = Follower()
                    follower.set_server(self)
                    self._state = follower
                elif (type(self._state) is Candidate):
                    self._leader = None
                    print self._name + " is transitioning to a neutral state"
                    neutral = Neutral()
                    neutral.set_server(self)
                    self._state = neutral
            self.threadLock.release()
        else:
            #print "server not running"
            #print "run released lock"
            pass


class ServerDeamon(threading.Thread):

    def __init__(self,name, state, log, lc):
        threading.Thread.__init__(self)
        self._server = Server(name,state,log,lc)
        self._stop_event = threading.Event()

    def stop(self):
        self._stop_event.set()

    def stopped(self):
        return self._stop_event.is_set()

    def run(self):
        while not self.stopped():
            self._server.run()
