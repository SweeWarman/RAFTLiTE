import unittest

import sys
sys.path.append("../")
from Messages.messages import *
from servers.server import Server
from states.follower import Follower
from states.candidate import Candidate
from states.leader import Leader
from states.state import EntryType
from Communication.Comm import MsgBoard

class TestLeaderServer( unittest.TestCase ):

    def setUp( self ):
        self.followers = []
        for i in range( 1, 4 ):
            state = Follower()
            self.followers.append( Server( "NODE"+str(i), state, [], MsgBoard() ) )

        state = Leader()

        self.leader = Server( "NODE0", state, [], MsgBoard() )

        for i in self.followers:
            i._leader = "NODE0"

        for i in range(1,4):
            self.leader._connectedServers.append("NODE"+str(i))
            self.leader._total_nodes = self.leader._total_nodes + 1

        state.set_server(self.leader)

    def _perform_hearbeat( self ):
        self.leader._state._send_append_entries_hbeat()

        for f in self.followers:
            message = self.leader._board.get_message()
            f.on_message(message)

        for f in self.followers:
            self.leader.on_message(f._board.get_message())

    def test_leader_server_sends_heartbeat_to_all_neighbors( self ):
        self._perform_hearbeat()
        self.assertEquals( { "NODE1": 1, "NODE2": 1, "NODE3": 1 }, self.leader._state._nextIndexes )
        self.leader._board.board = []

    def test_leader_server_sends_appendentries_to_all_neighbors_and_is_appended_to_their_logs( self ):

        self._perform_hearbeat()
        self.leader._board.board = []

        for f in self.followers:
            self.leader._state._send_append_entries(f._name,1,{"entryType":EntryType.DATA.value,"term":0,"data":[10.0,20.0]})

        for f in self.followers:
            message = self.leader._board.get_message()
            f.on_message(message)
            self.assertEquals( [{"entryType":EntryType.DATA.value,"term":0,"data":[10.0,20.0]}],f._log)

    def test_leader_server_sends_appendentries_to_all_neighbors_but_some_have_dirtied_logs( self ):

        self.followers[0]._log.append( { "entryType":EntryType.DATA.value,"term": 2, "data": [100,200] } )
        self.followers[0]._log.append( { "entryType":EntryType.DATA.value,"term": 2, "data": [300,500] } )
        self.followers[1]._log.append( { "entryType":EntryType.DATA.value,"term": 3, "data": [500,300] } )
        self.leader._log.append( { "entryType":EntryType.DATA.value,"term": 0, "data": [120,230] } )

        self._perform_hearbeat()
        self.leader._board.board = []

        for f in self.followers:
            self.leader._state._send_append_entries(f._name,1,{"entryType":EntryType.DATA.value,"term":0,"data":[120,230]})

        for f in self.followers:
            message = self.leader._board.get_message()
            f.on_message(message)
            self.assertEquals( [{ "entryType":EntryType.DATA.value,"term":0,"data":[120,230]}],f._log)


suite = unittest.TestLoader().loadTestsFromTestCase(TestLeaderServer)
unittest.TextTestRunner(verbosity=2).run(suite)
