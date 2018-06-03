import sys
import lcm
from Communication.LcmRaftMessages import client_status_t

# name of server to send message to
name = sys.argv[1]

msg = client_status_t()
msg.data[0] = float(sys.argv[2])
msg.data[1] = float(sys.argv[3])
msg.data[2] = float(sys.argv[4])
lc = lcm.LCM()
lc.publish(name+"_CLIENT_STATUS",msg.encode())
