# RAFTLiTE

RAFTLiTE is a light weight implementation of the RAFT protocol. The code in this repository is based on ideas/code found in [simpleraft](https://github.com/streed/simpleRaft).

[simpleraft](https://github.com/streed/simpleRaft) provides an excellent basic framework to construct RAFT based applications. But, requires additional work to serve clients, perform node discovery etc.... RAFTLiTE takes a shot at incorporating these features.

The default implementation uses the [Lightweight Communications and Marshalling (LCM)](https://github.com/lcm-proj/lcm) library for publish/subscribe based communication. To use other publish/subscribe libraries, appropriate interfaces need to be implemented.

Use the `StartNode.py` script to start a RAFT server:

``` 
python StartNode.py <SERVER_NAME>
```

Send data to be stored in the server. See `ClientTest.py` for an example:

```
python ClientTest.py <SERVER_NAME> val1 val2 val3
```

Every time a client sends data, the recorded log is printed to screen. Start multiple servers as separate processes and see the RAFT protocol synchronize all servers with the data being added by clients.

DISCLAIMER: Not tested extensively! Bug fixes and pull requests are welcome!

