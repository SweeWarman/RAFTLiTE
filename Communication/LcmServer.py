import lcm
import sys

from LcmRaftMessages import *

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
        if type(message) is heartbeat_t:
            hbeat = message # type: heartbeat_t
            self._lcm.publish("HEARTBEAT",hbeat.encode())
        elif type(message) is append_entries_t:
            entry = message # type: append_entries_t
            self._lcm.publish(entry.receiver+"_APPEND_ENTRIES",entry.encode())
        elif type(message) is request_vote_t:
            reqvote = message # type: request_vote_t
            self._lcm.publish(reqvote.receiver+"_REQUEST_VOTE",reqvote.encode())
        elif type(message) is vote_response_t:
            voteresponse = message # type: vote_response_t
            self._lcm.publish(voteresponse.receiver+"_VOTE_RESPONSE",voteresponse.encode())
        elif type(message) is response_t:
            response = message # type: response_t
            self._lcm.publish(response.receiver+"_RESPONSE",response.encode())
        elif type(message) is request_membership_t:
            mem_request = message # type: request_membership_t
            self._lcm.publish(mem_request.receiver+"_MEMBERSHIP",mem_request.encode())


    def run(self):
        try:
            while True:
                self._lcm.handle()
                message = self._board.get_message()
                self.send_message(message)
        except KeyboardInterrupt:
            print "Exiting lcm thread"

