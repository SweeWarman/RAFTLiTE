from states.neutral import Neutral
from servers.server import ServerDeamon
from Communication.Comm import *
from Communication.LcmServer import *

name = sys.argv[1]

board = MsgBoard()
state = Neutral()

node = ServerDeamon(name,state,[],board)
node.daemon = True

lcm = LcmServer(node._server,board)

lcm.start()
node.start()


