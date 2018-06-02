from state import State,ResponseType,EntryType
from collections import defaultdict
from ..LcmRaftMessages import *
import time

class Leader(State):

    def __init__(self,term = 0):
        self._prev_entry_time = 0
        self._prev_loop_time = 0
        self._currentTerm = term
        self._nextIndexes = defaultdict(int)
        self._matchIndex = defaultdict(int)
        self.name = "LEADER"


    def set_server(self, server):

        self._server = server
        self._server._leader = self._server._name
        self._send_append_entries_hbeat()

        for n in self._server._connectedServers:
            if n == self._server._name:
                continue
            self._nextIndexes[n] = self._server._lastLogIndex + 1
            self._matchIndex[n] = 0

    def on_heartbeat(self, message):
        if message.sender not in self._server._availableServers:
            self._server._availableServers.append(message.sender)
            print "discovered new server:" + message.sender
            entry = append_entries_t()
            entry.sender = self._server._name
            entry.receiver = message.sender
            self._server.send_message(entry)

        return self, None

    def on_client_status(self, message):
        """called when client sends messages"""
        log_entry = {}
        log_entry["entryType"] = EntryType.DATA.value
        log_entry["term"] = self._server._currentTerm
        
        #log_entry["intersectionID"] = message.intersectionID
        #log_entry["vehicleID"] = message.vehicleID
        #log_entry["entryTime"] = message.entryTime
        #log_entry["exitTime"] = message.exitTime
        #log_entry["crossingTime"] = message.crossingTime

        if not self.CheckIfAlreadyAvailable(log_entry):
            self._server._log.append(log_entry)
            self._server._lastLogIndex += 1
            print "received new client status from:" + message.sender


        return self,None

    def CheckIfAlreadyAvailable(self,entry):

        log = self._server._log[:]
        log.reverse()
        for i,element in enumerate(log):
            if element["entryType"] == EntryType.DATA.value:
                if sum(element["data"]) == sum(entry["data"]):
                        #print "Entry already available"
                        return True
            if element["entryType"] == EntryType.COMMAND.value:
                return False


        return False


    def SendComputeCommand(self,id):

        self._server.threadLock.acquire()
        log_entry = {}
        log_entry["entryType"] = EntryType.COMMAND.value
        log_entry["term"] = self._server._currentTerm

        self._server._log.append(log_entry)
        self._server._lastLogIndex += 1
        self._server.threadLock.release()

    def on_response_received(self, message):
        # Was the last AppendEntries good?
        if (message.data == ResponseType.APPEND_FAILURE.value):
            # No, so lets back up the log for this node
            self._nextIndexes[message.sender] -= 1

            # Get the next log entry to send to the client.
            logIndex = self._nextIndexes[message.sender]
            #previousIndex = max(0, logIndex - 1)
            #previous = self._server._log[previousIndex-1]
            current = self._server._log[logIndex-1]

            self._send_append_entries(message.sender,logIndex,current)

        elif (message.data == ResponseType.APPEND_SUCCESS.value):
            # The last append was good so increase their index.
            self._matchIndex[message.sender] = self._nextIndexes[message.sender]
            self._nextIndexes[message.sender] += 1

            # Are they caught up?
            #if (self._nextIndexes[message.sender] > self._server._lastLogIndex):
                #self._nextIndexes[message.sender] = self._server._lastLogIndex

            print "entry appended successfully in " + message.sender

            for N in range(self._server._commitIndex + 1, self._server._lastLogIndex + 1):
                if (self.TestMatchIndexMajority(N) and self._server._log[N-1]["term"] == self._server._currentTerm):
                    self._server._commitIndex = N
                    print "Updating server commit index to:" + str(self._server._commitIndex)

        return self, None

    def on_membership_request(self,message):
        #TODO: Replace this membership function with proper functions
        # NOTE: for a newly discovered server, _nextIndex is still not available, so we start with _lastLogIndex

        if message.request == True:
            self._server._total_nodes = self._server._total_nodes + 1
            self._server._connectedServers.append(message.sender)
            self._nextIndexes[message.sender] = self._server._lastLogIndex
            self._matchIndex[message.sender] = 0
        else:
            self._server._total_nodes -= 1
            try:
                self._server._connectedServers.remove(message.sender)
                self._server._availableServers.remove(message.sender)
            except:
                pass
            print "removing server:" + message.sender

        self._send_append_entries_hbeat()

        print self._server._name + ": is sending membership response to:" + message.sender
        self._send_response_message(message,ResponseType.MEMBERSHIP_SUCCESS)

        if message.request == False and message.sender == self._server._name:
            print "leader shutdown requested"
            self._server._shutdownRequest = True
            self._server._shutdown = True


        return self,None

    def _send_append_entries_hbeat(self):
        for node in self._server._connectedServers:
            if node == self._server._name:
                continue
            entry = append_entries_t()
            entry.sender = self._server._name
            entry.receiver = node
            entry.entryType = EntryType.HBEAT.value
            entry.term = self._server._currentTerm
            entry.nodes = self._server._total_nodes
            for i, nodes in enumerate(self._server._connectedServers):
                entry.nodeID[i] = int(nodes[7])
            entry.leaderCommit = self._server._commitIndex
            self._server.send_message(entry)

        self._prev_entry_time = time.time()

    def _send_append_entries(self,receiver,logIndex,log_entry):

        entry = append_entries_t()
        entry.sender = self._server._name
        entry.receiver = receiver
        entry.entryType = EntryType.DATA.value
        entry.term = self._server._currentTerm
        entry.nodes = self._server._total_nodes
        for i, nodes in enumerate(self._server._connectedServers):
            entry.nodeID[i] = int(nodes[7])

        entry.logIndex = logIndex
        entry.entryType = log_entry["entryType"]

        if entry.entryType == EntryType.DATA.value:
            entry.data = log_entry["data"]
            #entry.vehicleID = log_entry["vehicleID"]
            #entry.leaderCommit = self._server._commitIndex
            #entry.entryTime = log_entry["entryTime"]
            #entry.exitTime = log_entry["exitTime"]
            #entry.crossingTime = log_entry["crossingTime"]
        #else:
            #entry.vehicleID = "NONE"
            #entry.leaderCommit = 0
            #entry.entryTime = 0
            #entry.exitTime = 0
            #entry.crossingTime = 0

        entry.prevLogIndex = self._nextIndexes[receiver]-1
        if entry.prevLogIndex > 0:
            entry.prevLogTerm = self._server._log[entry.prevLogIndex-1]["term"]
        else:
            entry.prevLogTerm = 0

        self._server.send_message(entry)

    def TestMatchIndexMajority(self,N):

        count = 1
        for follower in self._server._connectedServers:
            if follower == self._server._name:
                continue

            if self._matchIndex[follower] >= N:
                count += 1

        # TODO: re-evaluate if this should be a majory vote or unanimous
        if count == len(self._server._connectedServers):
            return True
        else:
            return False


    def run(self):
        self._currentTime = time.time()
        sent = False

        if (self._currentTime - self._prev_entry_time) > 0.3:
            self._prev_entry_time = time.time()
            if self._currentTerm < self._server._currentTerm:
                return False

            for follower in self._server._connectedServers:
                if follower == self._server._name:
                    continue

                if self._server._lastLogIndex >= self._nextIndexes[follower]:
                    # NOTE: _lastLogIndex assume 1 is the first entry in the log
                    print "sending entry to: " + follower
                    logIndex = self._nextIndexes[follower]
                    log_entry = self._server._log[logIndex-1]
                    print log_entry
                    self._send_append_entries(follower,logIndex,log_entry)
                    sent = True

            if not sent:
                self._send_append_entries_hbeat()

        if self._server._shutdownRequest:
            shutdown = False
            for name in self._server._connectedServers:
                print name
                print self._matchIndex[name],self._server._commitIndex
                if name == self._server._name:
                    shutdown = True
                elif self._matchIndex[name] == self._server._commitIndex:
                    shutdown = True
                else:
                    shutdown = False

            if shutdown:
                print "shutting down server"
                self._server._shutdown = True


        return True

