# Copyright (c) J. A. Zanardo Jr. <zanardo@gmail.com>
# Please refer to COPYING for license details
#
# This rrd collector is used to collect network interface traffic.
#
# Usage:
#
#  /path/to/python2 rrd_iftraff.py rrdhost:rrdport rrdname iface
#
# Example:
#
#  /usr/bin/python2 rrd_iftraff.py 127.0.0.1:23456 localhost-iftraff-eth0 eth0

import socket
import sys
import re

rrdhost, rrdport = sys.argv[1].split(':')
rrdname = sys.argv[2]
rrdiface = sys.argv[3]

rx = None
tx = None

fp = open('/proc/net/dev')
for line in fp:
    s = re.split(' *', line)
    if s[1] == rrdiface + ':':
        rx = int(s[2])
        tx = int(s[10])
fp.close()

# Sending data via UDP
msg = "%s N:%d:%d" % ( rrdname, rx, tx )
socket.socket(socket.AF_INET, socket.SOCK_DGRAM).sendto(msg, (rrdhost, int(rrdport)))
sys.stderr.write(msg + '\n')
