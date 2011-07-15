# Copyright (c) J. A. Zanardo Jr. <zanardo@gmail.com>
# Please refer to COPYING for license details
#
# This rrd collector is used to collect CPU usage. It sleeps
# for 60 seconds to calculate the average usage.
#
# Usage:
#
#  /path/to/python2 rrd_cpu.py rrdhost:rrdport rrdname
#
# Example:
#
#  /usr/bin/python2 rrd_cpu.py 127.0.0.1:23456 localhost-cpu

import socket
import sys
import re
import time

rrdhost, rrdport = sys.argv[1].split(':')
rrdname = sys.argv[2]

def getstats():
    f = open('/proc/stat')
    for line in f:
        m = re.match('^cpu +(\d+) +(\d+) +(\d+)+ (\d+) ', line)
        if m:
            user, nice, system, idle = m.groups()
            return ( int(user), int(nice), int(system), int(idle) )

user1, nice1, system1, idle1 = getstats()
time.sleep(60)
user2, nice2, system2, idle2 = getstats()

total = ( user2 + system2 + nice2 + idle2 ) - \
    ( user1 + system1 + nice1 + idle1 )

total *= 1.0

puser = ( user2 - user1 ) / total * 100.0
pnice = ( nice2 - nice1 ) / total * 100.0
psystem = ( system2 - system1 ) / total * 100.0
pidle = ( idle2 - idle1 ) / total * 100.0

# Sending data via UDP
msg = "%s N:%.2f:%.2f:%.2f:%.2f" % ( rrdname, puser, pnice, psystem, pidle)
socket.socket(socket.AF_INET, socket.SOCK_DGRAM).sendto(msg, (rrdhost, int(rrdport)))
sys.stderr.write(msg + '\n')
