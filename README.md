# rrd

**rrd** is a BSD-like licensed collection of tools for Linux to obtain statistical
time-based data from computer devices over the network, writing them in
databases, and serving pretty graphs via browser. It is composed by a passive
udp server collector written in Python that is very scalable and has low
resources usage, and by a Tornado web application with a simple to use
interface based on filters to display the graphs.

Uses for rrd include receiving statistical data and plotting graphs for
network traffic, disk usage, system temperatures, load averages, mail queue
sizes, spam statistics, and so on, for any number of machines or devices
inside a network, for centralized monitoring.

The system is entirely based on rrdtool. Indeed, rrd is like a thin layer that
wraps the fantastic rrdtool software into a distributed network statistical
collection and display package. It is made to be simple (think about Unix
simplicity!), and it has no fancy configuration wizard.  Instead, it is very
bare-foot -- prior knowledge in rrdtool is required, as you _will_ be barely
using rrdtool commands and arguments to create databases and graphs.

*Attention*: Although rrd daemon was designed to be secure (it runs under a
non-privileged user account and a chroot-jail), it is supposed to be run
inside a Local Area Network, so it has no authentication or encryption. Data
is send in plain text inside udp datagrams over the network. rrd is made to be
simple. Use at your own risk!

## Installing rrd

You can fetch the latest version of rrd using git:

    $ git clone git://github.com/zanardo/rrd.git

Software necessary to run rrd and rrdweb:

* Python >= 2.5 (rrd is mainly tested on Python 2.7)
* rrdtool installed with Python libraries
* tornado Python's module

Installing the daemons:

    $ cd rrd
    $ sudo install -o root -g root -m 755 rrd /usr/sbin/rrd
    $ sudo install -o root -g root -m 755 rrdweb /usr/sbin/rrdweb

Creating the database and configurations directory:

    $ sudo mkdir -p /var/lib/rrd
    $ sudo chown -R daemon:daemon /var/lib/rrd

If you want to start rrd and rrdweb at system bootup, use the commands below
in your initialization scripts (like rc.local). In this example, we are using
gnu screen to manage the daemons:

    echo 'Starting rrd daemon...'
    /usr/bin/screen -S rrdudp -m -d /usr/sbin/rrd

    echo 'Starting rrd web server...'
    /usr/bin/screen -S rrdweb -m -d /usr/sbin/rrdweb

## Collectors

rrd is not useful without collectors, the programs/scripts that actually
send data. You can create your own collectors or use example collectors.
To download the example collectors:

    # cd /opt
    # git clone git://github.com/zanardo/rrd-collectors.git

The rrd-collectors distribution contains some useful collectors like cpu
and memory usage, network traffic usage, and the usage of each one is
documented into the source code. Generally, each script has its own
command line arguments and should run on cron. You can read more details
about those examples in the README file from the rrd-collectors
distribution.

## The rrd protocol

rrd only processes udp packets with rrdupdates, or time-based data to update
its databases. Example for a typical packet content:

    localhost-iftraff-eth0 N:864703:6629

The first term, localhost-iftraff-eth0, is the database name. It must have
been previously configured in /var/lib/rrd/conf-data/localhost-iftraff-eth0.
In this example, we are collecting network traffic in localhost, on the
interface eth0.

The second term, N:864703:6629, is a rrdupdate argument. Read the rrdupdate
documentation from rrdtool to understand it. The first number is the RX
(received) traffic and the second number is the TX (transmitted) traffic, both
measured in bytes and in absolute form.

## Creating collectors

It's very easy to create collectors. Suppose you want to collect the
percentage of used space in the filesystem mounted as / on server01 machine.
Create the following bash shell-script:

    used=$(df / | grep "/" | sed -e 's/^.* \([0-9]\+\)% .*$/\1/')
    echo "server01-df-root N:$used" > /dev/udp/192.168.1.10/23456

This sends the information to the rrd daemon, listening on 192.168.1.10.

You can create collectors in any programming language you want, that supports
sending data via udp datagrams.
