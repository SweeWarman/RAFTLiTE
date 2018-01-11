from states.follower import Follower
from servers.server import Server
from LcmRaftMessages import *
import sys
import lcm

def HandleHeartBeat(channel,data):
    global server
    msg = heartbeat_t.decode(data)
    if msg.sender != server._name:
        server.on_message(msg)

def HandleRequestVote(channel,data):
    global server
    msg = request_vote_t.decode(data)
    if msg.sender != server._name:
        server.on_message(msg)

def HandleVoteResponse(channel,data):
    global server
    msg = vote_response_t.decode(data)
    if msg.sender != server._name:
        server.on_message(msg)

def HandleResponse(channel,data):
    global server
    msg = response_t.decode(data)
    if msg.sender != server._name:
        server.on_message(msg)

def HandleAppendEntries(channel,data):
    global server
    msg = append_entries_t.decode(data)
    if msg.sender != server._name:
        server.on_message(msg)

lc = lcm.LCM()

subscription = lc.subscribe("HEARTBEAT",HandleHeartBeat)
subscription = lc.subscribe("APPEND_ENTRIES",HandleAppendEntries)
subscription = lc.subscribe("REQUEST_VOTE",HandleRequestVote)
subscription = lc.subscribe("VOTE_RESPONSE",HandleVoteResponse)
subscription = lc.subscribe("RESPONSE",HandleResponse)

name = sys.argv[1]

state = Follower()
server = Server(name,state,lc)

server.start()

try:
    while True:
        lc.handle()
except KeyboardInterrupt:
    print "Exiting lcm thread"

