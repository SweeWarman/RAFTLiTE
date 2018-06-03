import lcm
import sys

from LcmRaftMessages import *
from ..Messages.messages import *

class LcmServer(object):
    def __init__(self,server,board):
        self._lcm = lcm.LCM()
        self._server = server
        self._board = board

        _lcm_heartbeat_handler   = lambda channel,data:self.HandleHeartBeat(channel,data)
        _lcm_appendentry_handler = lambda channel,data:self.HandleAppendEntries(channel,data)
        _lcm_requestvote_handler = lambda channel,data:self.HandleRequestVote(channel,data)
        _lcm_response_handler    = lambda channel,data:self.HandleResponse(channel,data)
        _lcm_voteresponse_handler= lambda channel,data:self.HandleVoteResponse(channel,data)
        _lcm_membership_handler  = lambda channel,data:self.HandleMemberShip(channel,data)
        _lcm_clientstatus_handler= lambda channel,data:self.HandleClientStatus(channel,data)


        self._lcm.subscribe("HEARTBEAT",_lcm_heartbeat_handler)
        self._lcm.subscribe(server._name + "_APPEND_ENTRIES",_lcm_appendentry_handler)
        self._lcm.subscribe(server._name + "_REQUEST_VOTE",_lcm_requestvote_handler)
        self._lcm.subscribe(server._name + "_VOTE_RESPONSE",_lcm_voteresponse_handler)
        self._lcm.subscribe(server._name + "_RESPONSE",_lcm_response_handler)
        self._lcm.subscribe(server._name + "_MEMBERSHIP",_lcm_membership_handler)
        self._lcm.subscribe(server._name + "_CLIENT_STATUS",_lcm_clientstatus_handler)

    def HandleHeartBeat(self,channel, data):
        msg = heartbeat_t.decode(data)
        if msg.sender != self._server._name:
            self._server.on_message(msg)

    def HandleRequestVote(self,channel, data):
        msg = request_vote_t.decode(data)
        if msg.sender != self._server._name:
            self._server.on_message(msg)

    def HandleVoteResponse(self,channel, data):
        msg = vote_response_t.decode(data)
        if msg.sender != self._server._name:
            self._server.on_message(msg)

    def HandleResponse(self,channel, data):
        msg = response_t.decode(data)
        if msg.sender != self._server._name:
            self._server.on_message(msg)

    def HandleAppendEntries(self,channel, data):
        msg = append_entries_t.decode(data)
        if msg.sender != self._server._name:
            self._server.on_message(msg)

    def HandleMemberShip(self, channel, data):
        msg = request_membership_t.decode(data)
        self._server.on_message(msg)

    def HandleClientStatus(self,channel, data):
        msg = client_status_t.decode(data)
        self._server.on_message(msg)

    def send_message(self, message):
        if type(message) is heartbeat:
            hbeat = heartbeat_t()
            hbeat.sender = message.sender
            hbeat.receiver = message.receiver
            self._lcm.publish("HEARTBEAT",hbeat.encode())
        elif type(message) is append_entries:
            entry = append_entries_t()
            entry.sender = message.sender
            entry.receiver = message.receiver
            entry.term = message.term
            entry.nodes = message.nodes
            entry.nodeID = message.nodeID
            entry.entryType = message.entryType
            entry.logIndex = message.logIndex
            entry.prevLogIndex = message.prevLogIndex
            entry.prevLogTerm = message.prevLogTerm
            entry.data = message.data
            self._lcm.publish(entry.receiver+"_APPEND_ENTRIES",entry.encode())
        elif type(message) is request_vote:
            reqvote = request_vote_t()
            reqvote.sender = message.sender
            reqvote.receiver = message.receiver
            reqvote.term = message.term
            self._lcm.publish(reqvote.receiver+"_REQUEST_VOTE",reqvote.encode())
        elif type(message) is vote_response:
            voteresponse = vote_response_t()
            voteresponse.sender = message.sender
            voteresponse.receiver = message.receiver
            voteresponse.term = message.term
            voteresponse.data = message.data
            self._lcm.publish(voteresponse.receiver+"_VOTE_RESPONSE",voteresponse.encode())
        elif type(message) is response:
            _response = response_t()
            _response.sender = message.sender
            _response.receiver = message.receiver
            _response.data = message.data
            self._lcm.publish(response.receiver+"_RESPONSE",_response.encode())
        elif type(message) is request_membership:
            mem_request = request_membership_t()
            mem_request.sender = message.sender
            mem_request.receiver = message.receiver
            mem_request.request = message.request
            self._lcm.publish(mem_request.receiver+"_MEMBERSHIP",mem_request.encode())


    def run(self):
        try:
            while True:
                self._lcm.handle()
                message = self._board.get_message()
                self.send_message(message)
        except KeyboardInterrupt:
            print "Exiting lcm thread"

