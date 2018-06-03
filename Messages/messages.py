
class base(object):
    def __init__(self):
        self.timestamp = 0
        self.sender = ""
        self.receiver = ""

class append_entries(base):
    def __init__(self):
        self.term = 0
        self.nodes = 0
        self.nodeID = [ "" for dim0 in range(10) ]
        self.entryType = 0
        self.leaderCommit = 0
        self.logIndex = 0
        self.prevLogIndex = 0
        self.prevLogTerm = 0
        self.data = [ 0.0 for dim0 in range(10) ]

class client_status(base):
    def __init__(self):
        self.data = [ 0.0 for dim0 in range(10) ]

class heartbeat(base):
    def __init__(self):
        self.timeStamp = 0
        self.sender = ""
        self.receiver = ""

class request_membership(base):
    def __init__(self):
        self.request = False

class request_vote(base):
    def __init__(self):
        self.term = 0

class response(base):
    def __init__(self):
        self.data = False

class vote_response(base):
    def __init__(self):
        self.term = 0
        self.data = False


