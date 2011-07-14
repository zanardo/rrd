# Copyright (c) J. A. Zanardo Jr. <zanardo@gmail.com>
# Please refer to COPYING for license details

import sys
import os
import getopt
import socket
import rrdtool
import re

__VERSION__ = '0.3'

class InvalidPacketError(Exception):
    pass

class RRDServer(object):

    def __init__(self, host='0.0.0.0', port=23456, path='.'):
        self.host = host
        self.port = port
        self.path = path

    def chdir(self):
        if self.path != '.':
            print 'chdir() to "%s"' % self.path
            try:
                os.chdir(self.path)
            except Exception, err:
                print "ERROR: %s" % err
                exit(1)

    def chroot(self):
        # chroot() only if running as root
        if os.getuid() == 0:
            print 'chroot() to .'
            try:
                os.chroot('.')
            except Exception, str:
                print 'ERROR: chroot(): %s' % str

    def parsepacket(self, packet):
        m = re.match('^([a-z0-9\-]+) (N:[0-9U\-\.\:]+)$', packet)
        if m:
            return m.groups()
        else:
            raise InvalidPacketError()

    def updaterrd(self, name, value):
        try:
            rrdtool.update('data/%s.rrd' % name, value)
        except Exception, err:
            print 'ERROR: %s' % err

    def run(self):
        print 'starting rrd daemon'
        self.chdir()
        self.chroot()
        print 'rrd version %s running' % __VERSION__
        server = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        server.bind((self.host, int(self.port)))
        print 'listening on %s:%s' % (self.host, self.port)
        print 'rrd daemon is ready to receive requests'
        try:
            while True:
                data, addr = server.recvfrom(256)
                try:
                    name, value = self.parsepacket(data)
                    print '[%s] %s' % (addr[0], data)
                    self.updaterrd(name, value)
                except InvalidPacketError:
                    print '[%s] invalid packet' % addr[0]

        except KeyboardInterrupt:
            print "exiting rrd"
            exit(0)

if __name__ == '__main__':

    rrdhost = '0.0.0.0'
    rrdport = 23456
    rrdpath = '.'

    def usage():
        print '''usage: %s -h <host> -p <port> -d <dir>

        host: ip address to listen (default: 0.0.0.0)
        port: port to listen (default: 23456)
        dir: path to data directory (default: .)
        ''' % sys.argv[0]
        exit(1)

    try:
        opts, args = getopt.getopt(sys.argv[1:], 'h:p:d:')
    except getopt.GetoptError, err:
        usage()

    for o, a in opts:
        if o == '-h':
            rrdhost = a
        elif o == '-p':
            rrdport = a
        elif o == '-d':
            rrdpath = a
        else:
            usage()

    rrd = RRDServer(rrdhost, rrdport, rrdpath)
    rrd.run()
