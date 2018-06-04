import sys
import lcm
from Communication.LcmRaftMessages import client_status_t

# name of server to send message to
name = sys.argv[1]

msg = client_status_t()
input_data = sys.argv[2:]
msg.n = len(input_data)
for val in input_data:
    msg.data.append(float(val))

print "sending data:" + str(msg.data)

lc = lcm.LCM()
lc.publish(name+"_CLIENT_STATUS",msg.encode())
