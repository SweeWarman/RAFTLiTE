"""LCM type definitions
This file automatically generated by lcm.
DO NOT MODIFY BY HAND!!!!
"""

try:
    import cStringIO.StringIO as BytesIO
except ImportError:
    from io import BytesIO
import struct

class append_entries_t(object):
    __slots__ = ["timeStamp", "sender", "receiver", "term", "nodes", "nodeID", "entryType", "leaderCommit", "logIndex", "prevLogIndex", "prevLogTerm", "data"]

    def __init__(self):
        self.timeStamp = 0
        self.sender = ""
        self.receiver = ""
        self.term = 0
        self.nodes = 0
        self.nodeID = [ 0 for dim0 in range(10) ]
        self.entryType = 0
        self.leaderCommit = 0
        self.logIndex = 0
        self.prevLogIndex = 0
        self.prevLogTerm = 0
        self.data = [ 0.0 for dim0 in range(10) ]

    def encode(self):
        buf = BytesIO()
        buf.write(append_entries_t._get_packed_fingerprint())
        self._encode_one(buf)
        return buf.getvalue()

    def _encode_one(self, buf):
        buf.write(struct.pack(">q", self.timeStamp))
        __sender_encoded = self.sender.encode('utf-8')
        buf.write(struct.pack('>I', len(__sender_encoded)+1))
        buf.write(__sender_encoded)
        buf.write(b"\0")
        __receiver_encoded = self.receiver.encode('utf-8')
        buf.write(struct.pack('>I', len(__receiver_encoded)+1))
        buf.write(__receiver_encoded)
        buf.write(b"\0")
        buf.write(struct.pack(">qq", self.term, self.nodes))
        buf.write(struct.pack('>10q', *self.nodeID[:10]))
        buf.write(struct.pack(">qqqqq", self.entryType, self.leaderCommit, self.logIndex, self.prevLogIndex, self.prevLogTerm))
        buf.write(struct.pack('>10d', *self.data[:10]))

    def decode(data):
        if hasattr(data, 'read'):
            buf = data
        else:
            buf = BytesIO(data)
        if buf.read(8) != append_entries_t._get_packed_fingerprint():
            raise ValueError("Decode error")
        return append_entries_t._decode_one(buf)
    decode = staticmethod(decode)

    def _decode_one(buf):
        self = append_entries_t()
        self.timeStamp = struct.unpack(">q", buf.read(8))[0]
        __sender_len = struct.unpack('>I', buf.read(4))[0]
        self.sender = buf.read(__sender_len)[:-1].decode('utf-8', 'replace')
        __receiver_len = struct.unpack('>I', buf.read(4))[0]
        self.receiver = buf.read(__receiver_len)[:-1].decode('utf-8', 'replace')
        self.term, self.nodes = struct.unpack(">qq", buf.read(16))
        self.nodeID = struct.unpack('>10q', buf.read(80))
        self.entryType, self.leaderCommit, self.logIndex, self.prevLogIndex, self.prevLogTerm = struct.unpack(">qqqqq", buf.read(40))
        self.data = struct.unpack('>10d', buf.read(80))
        return self
    _decode_one = staticmethod(_decode_one)

    _hash = None
    def _get_hash_recursive(parents):
        if append_entries_t in parents: return 0
        tmphash = (0xc799c49ca0abbcad) & 0xffffffffffffffff
        tmphash  = (((tmphash<<1)&0xffffffffffffffff)  + (tmphash>>63)) & 0xffffffffffffffff
        return tmphash
    _get_hash_recursive = staticmethod(_get_hash_recursive)
    _packed_fingerprint = None

    def _get_packed_fingerprint():
        if append_entries_t._packed_fingerprint is None:
            append_entries_t._packed_fingerprint = struct.pack(">Q", append_entries_t._get_hash_recursive([]))
        return append_entries_t._packed_fingerprint
    _get_packed_fingerprint = staticmethod(_get_packed_fingerprint)

