# Copyright (c) J. A. Zanardo Jr. <zanardo@gmail.com>
# Please refer to COPYING for license details

# Usage: cd /rrd/data/path ; python2 rrd_create_databases.py

# Scans new templates in ./conf-data and creates each rrdtool database
# in ./data. This doesn't rewrite already created rrdtool databases!

import sys
import os
import os.path
import rrdtool
import re

def rrdcreate(name):
    conf = []
    fp = open('./conf-data/%s' % name)
    for line in fp:
        line = line.strip()
        if re.match('^#', line):
            continue
        conf.append(line)
    fp.close()
    print ';; creating ./data/%s.rrd' % name
    try:
        rrdtool.create('./data/%s.rrd' % name, conf)
    except Exception, err:
        print 'ERROR: [%s] %s' % ( name, err )

if __name__ == '__main__':

    if not os.path.isdir('./data'):
        print ';; creating ./data'
        os.mkdir('data')

    if os.path.isdir('./conf-data'):
        for f in os.listdir('./conf-data'):
            if not os.path.isfile('./data/%s.rrd' % f):
                rrdcreate(f)
