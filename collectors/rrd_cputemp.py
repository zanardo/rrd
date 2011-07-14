# Copyright (c) J. A. Zanardo Jr. <zanardo@gmail.com>
# Please refer to COPYING for license details
#
# This rrd collector is used to collect CPU temperature
#
# Usage:
#
#  /path/to/python2 rrd_cputemp.py rrdhost:rrdport rrdname temperfile
#
# Example:
#
#  /usr/bin/python2 rrd_cputemp.py 127.0.0.1:23456 localhost-cputemp \
#       /sys/class/hwmon/hwmon0/device/temp1_input

import socket
import sys

rrdhost, rrdport = sys.argv[1].split(':')
rrdname = sys.argv[2]
temperfile = sys.argv[3]

# Temperature is registered in Celsius and needs to be divided by 1000
f = open(temperfile)
temp = f.read().strip()
temp = int(temp) / 1000.0
f.close()

# Sending data via UDP
msg = "%s N:%.2f" % ( rrdname, temp)
socket.socket(socket.AF_INET, socket.SOCK_DGRAM).sendto(msg, (rrdhost, int(rrdport)))
sys.stderr.write(msg + '\n')
