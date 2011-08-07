# Copyright (c) J. A. Zanardo Jr. <zanardo@gmail.com>
# Please refer to COPYING for license details

import sys
import os
import getopt
import socket
import rrdtool
import re
import pwd, grp

__VERSION__ = '0.3'

class _InvalidPacketError(Exception):
    pass

class RRDServer(object):

    host = '0.0.0.0'
    port = 23456
    path = '.'
    user = 'nobody'
    group = 'nogroup'

    def __chdir(self):
        if self.path != '.':
            print 'going to data directory: %s' % self.path
            try:
                os.chdir(self.path)
            except Exception, err:
                print "ERROR: %s" % err
                exit(1)

    def __getuidgid(self):
        if os.getuid() == 0:
            try:
                self.uid = pwd.getpwnam(self.user).pw_uid
                self.gid = grp.getgrnam(self.group).gr_gid
            except Exception, str:
                print 'ERROR: %s' % str
                exit(1)

    def __droproot(self):
        if os.getuid() == 0:
            print 'dropping root privileges - user %s group %s' % ( self.user, self.group )
            try:
                os.setgroups([])
                os.setgid(self.gid)
                os.setuid(self.uid)
            except Exception, err:
                print 'ERROR: dropping root: %s' % err
                exit(1)

    def __chroot(self):
        # chroot() only if running as root
        if os.getuid() == 0:
            print 'entering chroot() jail'
            try:
                os.chroot('.')
            except Exception, str:
                print 'ERROR: chroot(): %s' % str

    def __parsepacket(self, packet):
        m = re.match('^([a-z0-9\-]+) (N:[0-9U\-\.\:]+)$', packet)
        if m:
            return m.groups()
        else:
            raise _InvalidPacketError()

    def __createrrd(self, name):
        if not os.path.isfile('./data/%s.rrd' % name) and os.path.isfile('./conf-data/%s' % name):
            conf = []
            fp = open('./conf-data/%s' % name)
            for line in fp:
                line = line.strip()
                if re.match('^#', line):
                    continue
                conf.append(line)
            fp.close()
            print 'creating ./data/%s.rrd' % name
            try:
                rrdtool.create('./data/%s.rrd' % name, conf)
            except Exception, err:
                print 'ERROR: [%s] %s' % ( name, err )

    def __updaterrd(self, name, value):
        try:
            rrdtool.update('data/%s.rrd' % name, value)
        except Exception, err:
            print 'ERROR: %s' % err

    def run(self):
        print 'starting rrd daemon'
        self.__chdir()
        self.__getuidgid()
        self.__chroot()
        self.__droproot()
        print 'rrd version %s running' % __VERSION__
        server = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        server.bind((self.host, int(self.port)))
        print 'listening on %s:%s' % (self.host, self.port)
        print 'rrd daemon is ready to receive requests'
        while True:
            data, addr = server.recvfrom(256)
            try:
                name, value = self.__parsepacket(data)
                print '[%s] %s' % (addr[0], data)
                self.__createrrd(name)
                self.__updaterrd(name, value)
            except _InvalidPacketError:
                print '[%s] invalid packet' % addr[0]


if __name__ == '__main__':

    def usage():
        print '''usage: %s -h <host> -p <port> -d <dir> -u <user> -g <group>

        host: ip address to listen (default: 0.0.0.0)
        port: port to listen (default: 23456)
        dir: path to data directory (default: .)
        user: drop root privileges and run as user <user>
        group: drop root privileges and run as group <group>
        ''' % sys.argv[0]
        exit(1)

    try:
        opts, args = getopt.getopt(sys.argv[1:], 'h:p:d:u:g:')
    except getopt.GetoptError, err:
        usage()

    rrd = RRDServer()

    for o, a in opts:
        if o == '-h': rrd.host = a
        elif o == '-p': rrd.port = a
        elif o == '-d': rrd.path = a
        elif o == '-u': rrd.user = a
        elif o == '-g': rrd.group = a
        else: usage()

    try:
        rrd.run()
    except KeyboardInterrupt:
        print "exiting rrd"
        exit(0)
