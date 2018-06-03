from voter import Voter
from ..LcmRaftMessages import *
import time
from state import ResponseType,EntryType

class Follower(Voter):

    def __init__(self, timeout=1000):
        Voter.__init__(self)
        self._timeout = timeout
        self._timeoutTime = self._nextTimeout()
        self.name = "FOLLOWER"

    def on_response_received(self, message):
        # Was the last AppendEntries good?
        if self._server._expectResponse == False:
            return self,None
        else:
            if (message.data == ResponseType.MEMBERSHIP_SUCCESS.value):
                print "shutting down server"
                self._server._connectedServers.remove(self._server._name)
                self._server._availableServers.remove(self._server._name)
                self._server._shutdown = True

        return self,None

    def on_append_entries(self, message):
        """
        :param append_entries_t message: lcm append entries message
        :return:
        """
        
        # Get the next append entry timeout. Note if this timeout is elapsed,
        # a relection should be triggered.
        self._timeoutTime = self._nextTimeout()

        self._server._leader = message.sender
        self._server._commitIndex = min(message.leaderCommit,len(self._server._log))

        # if the term in the incoming message is lower than this nodes current term,
        # notify the leader
        if(message.term < self._server._currentTerm):
            self._send_response_message(message, ResponseType.INCORRECT_TERM)
            return self, None

        self._server._total_nodes = message.nodes
        active = False
        nameListAvail = []

        # Add nodeIDs in message to connectedServers if they are
        # not already available
        for i,node in enumerate(message.nodeID):
            nodeName = node 
            nameListAvail.append(nodeName)
            if nodeName == self._server._name:
                active = True
            if i < self._server._total_nodes and nodeName not in self._server._connectedServers:
                self._server._connectedServers.append(nodeName)

        # Remove servers from connectedServers if their node IDs
        # are not available in the message
        for name in self._server._connectedServers:
            if name not in nameListAvail:
                print "removing server:" + name
                try:
                    self._server._connectedServers.remove(name)
                    self._server._availableServers.remove(name)
                except:
                    pass
                print "total nodes:" + str(self._server._total_nodes)

        # TODO: removing follower like this will never work. This follower will not receive anything.
        if active != True:
            print "shutting down server"
            self._server._shutdown = True

        if (message.entryType != EntryType.HBEAT.value):
            log = self._server._log
            newlogentry = {}
            
            newlogentry["leaderCommit"] = message.leaderCommit
            newlogentry["prevLogIndex"] = message.prevLogIndex
            newlogentry["prevLogTerm"] = message.prevLogTerm
            newlogentry["data"] = message.data

            #newlogentry["intersectionID"] = message.intersectionID
            #newlogentry["vehicleID"] = message.vehicleID
            #newlogentry["entryType"] = message.entryType
            #newlogentry["entryTime"] = message.entryTime
            #newlogentry["exitTime"] = message.exitTime
            #newlogentry["crossingTime"] = message.crossingTime


            # Can't possibly be up-to-date with the log
            # If the log is smaller than the preLogIndex
            if (len(log) < newlogentry["prevLogIndex"]):
                print "APPEND FAILURE"
                self._send_response_message(message, ResponseType.APPEND_FAILURE)
                return self, None

            # We need to hold the induction proof of the algorithm here.
            #   So, we make sure that the prevLogIndex term is always
            #   equal to the server.
            if (len(log) > 0 and log[newlogentry["prevLogIndex"]-1]["term"] != newlogentry["prevLogTerm"]):

                # There is a conflict we need to resync so delete everything
                #   from this prevLogIndex and forward and send a failure
                #   to the server.
                log = log[:newlogentry["prevLogIndex"]]
                print "APPEND FAILURE"
                self._send_response_message(message, ResponseType.APPEND_FAILURE)
                self._server._log = log
                self._server._lastLogIndex = newlogentry["prevLogIndex"]
                self._server._lastLogTerm = newlogentry["prevLogTerm"]
                return self, None
            # The induction proof held so lets check if the commitIndex
            #   value is the same as the one on the leader
            else:
                # Make sure that leaderCommit is > 0 and that the
                #   data is different here
                if (len(log) > 0 and
                    len(log) >= newlogentry["leaderCommit"] and
                    newlogentry["leaderCommit"] > 0 and
                    log[newlogentry["leaderCommit"]-1]["term"] != message.term):
                    # Data was found to be different so we fix that
                    #   by taking the current log and slicing it to the
                    #   leaderCommit + 1 range then setting the last
                    #   value to the commitValue
                    log = log[:self._server._commitIndex]
                    entry = {}
                    entry["term"] = message.term
                    entry["entryType"] = message.entryType
                    entry["data"] = message.data
                    
                    #entry["intersectionID"] = newlogentry["intersectionID"]
                    #entry["vehicleID"] = newlogentry["vehicleID"]
                    #entry["entryTime"] = newlogentry["entryTime"]
                    #entry["exitTime"] = newlogentry["exitTime"]
                    #entry["crossingTime"] = newlogentry["crossingTime"]

                    log.append(entry)
                    self._send_response_message(message,ResponseType.APPEND_SUCCESS)
                    self._server._lastLogIndex = len(log)
                    self._server._lastLogTerm = log[-1]["term"]
                    self._server._commitIndex = min(newlogentry["leaderCommit"],len(log))
                    self._server._log = log
                    print log
                else:
                    # The commit index is not out of the range of the log
                    #   so we can just append it to the log now.
                    #   commitIndex = len(log)
                    #   Is this a heartbeat?
                    #print "received new append entry"
                    if (message.logIndex == self._server._lastLogIndex and
                        message.term == self._server._lastLogTerm):
                        return self,None

                    entry = {}
                    entry["term"] = message.term
                    entry["entryType"] = message.entryType
                    entry["data"] = message.data
                    
                    #entry["intersectionID"] = newlogentry["intersectionID"]
                    #entry["vehicleID"] = newlogentry["vehicleID"]
                    #entry["entryType"] = newlogentry["entryType"]
                    #entry["entryTime"] = newlogentry["entryTime"]
                    #entry["exitTime"] = newlogentry["exitTime"]
                    #entry["crossingTime"] = newlogentry["crossingTime"]

                    log.append(entry)
                    self._server._lastLogIndex = max(0,len(log))
                    self._server._lastLogTerm = max(0,log[-1]["term"])
                    self._server._commitIndex = min(newlogentry["leaderCommit"],len(log))
                    self._server._log = log
                    self._send_response_message(message,ResponseType.APPEND_SUCCESS)
                    print log

            return self, None
        else:
            self._send_response_message(message,ResponseType.HBEAT_ACK)
            return self, None


    def run(self):
        """Follower state should check for the leader timeout"""
        self._currentTime = time.time()
        if self._currentTime > self._timeoutTime:
            return False

        return True
