import sys

from RAFTLiTE.states.neutral import Neutral
from RAFTLiTE.servers.server import ServerDeamon
from RAFTLiTE.Communication.Comm import *
from RAFTLiTE.Communication.LcmServer import *

name = sys.argv[1]

board = MsgBoard()
state = Neutral()

node = ServerDeamon(name,state,[],board)
node.daemon = True

lcm = LcmServer(node._server,board)
lcm.daemon = True

node.start()
lcm.start()

try:
    while True:
        lcm._lcm.handle()
except KeyboardInterrupt:
    print "Exiting lcm thread"
