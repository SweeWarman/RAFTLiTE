import lcm
import sys
sys.path.append("../")
from LcmRaftMessages import *
from Messages.messages import *
import threading

class LcmServer(threading.Thread):
    def __init__(self,server,board):
        threading.Thread.__init__(self)
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
        hbeat = heartbeat()
        hbeat.sender = msg.sender
        hbeat.receiver = msg.receiver
        if msg.sender != self._server._name:
            self._server.on_message(hbeat)

    def HandleRequestVote(self,channel, data):
        msg = request_vote_t.decode(data)
        reqvote = request_vote()
        reqvote.sender = msg.sender
        reqvote.receiver = msg.receiver
        reqvote.term = msg.term
        if msg.sender != self._server._name:
            self._server.on_message(reqvote)

    def HandleVoteResponse(self,channel, data):
        msg = vote_response_t.decode(data)
        voteresponse = vote_response()
        voteresponse.sender = msg.sender
        voteresponse.receiver = msg.receiver
        voteresponse.term = msg.term
        voteresponse.data = msg.data
        if msg.sender != self._server._name:
            self._server.on_message(voteresponse)

    def HandleResponse(self,channel, data):
        msg = response_t.decode(data)
        _response = response()
        _response.sender = msg.sender
        _response.receiver = msg.receiver
        _response.data = msg.data
        _response.term = msg.term
        if msg.sender != self._server._name:
            self._server.on_message(_response)

    def HandleAppendEntries(self,channel, data):
        msg = append_entries_t.decode(data)
        entry = append_entries()
        entry.sender = msg.sender
        entry.receiver = msg.receiver
        entry.term = msg.term
        entry.nodes = msg.nodes
        entry.nodeID = msg.nodeID
        entry.entryType = msg.entryType
        entry.logIndex = msg.logIndex
        entry.prevLogIndex = msg.prevLogIndex
        entry.prevLogTerm = msg.prevLogTerm
        entry.data = msg.data
        if msg.sender != self._server._name:
            self._server.on_message(entry)

    def HandleMemberShip(self, channel, data):
        msg = request_membership_t.decode(data)
        mem_request = request_membership()
        mem_request.sender = msg.sender
        mem_request.receiver = msg.receiver
        mem_request.request = msg.request

        self._server.on_message(mem_request)

    def HandleClientStatus(self,channel, data):
        msg = client_status_t.decode(data)
        cstatus = client_status()
        cstatus.data = msg.data
        self._server.on_message(cstatus)

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
            _response.term = message.term
            _response.data = message.data
            self._lcm.publish(_response.receiver+"_RESPONSE",_response.encode())
        elif type(message) is request_membership:
            mem_request = request_membership_t()
            mem_request.sender = message.sender
            mem_request.receiver = message.receiver
            mem_request.request = message.request
            self._lcm.publish(mem_request.receiver+"_MEMBERSHIP",mem_request.encode())

    def run(self):
        while True:
            message = self._board.get_message()
            if message is not None:
                self.send_message(message)

