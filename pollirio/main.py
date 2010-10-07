#!/usr/bin/env python
# -*- coding: utf-8 -*-

# © 2010, David Paleino <dapal@debian.org>

from twisted.words.protocols import irc
from twisted.internet import protocol, reactor
from twisted.python import log

import random
import time
import re
import sys

from pollirio.modules.lart import *
from pollirio.modules import plugin_run, check_args
from pollirio.confreader import ConfReader
from pollirio import commands, get_command

conf = ConfReader('pollirio.ini')

class Logger:
    def __init__(self, file):
        self.file = file

    def log(self, message):
        """Write a message to the file."""
        timestamp = time.strftime("[%H:%M:%S]", time.localtime(time.time()))
        self.file.write('%s %s\n' % (timestamp, message))
        self.file.flush()

    def close(self):
        self.file.close()

class IrcEvent:
    def __init__(self, username, channel, msg):
        self.nick = username
        self.channel = channel
        self.msg = msg
        self.args = self.msg.split()[1:]

class MyBot(irc.IRCClient):
    def _get_nickname(self):
        return self.factory.nickname
    nickname = property(_get_nickname)

    # override IRCClient's methods, just to get them logged
    def msg(self, channel, message):
        # FIXME: use the configurable nick
        irc.IRCClient.msg(self, channel, message)
        if message.find("ACTION") == -1:
            self.logger.log("<pollirio> %s" % message)

    def describe(self, channel, message):
        # FIXME: use the configurable nick
        irc.IRCClient.describe(self, channel, message)
        self.logger.log("* pollirio %s" % message)

    # callback
    def connectionMade(self):
        irc.IRCClient.connectionMade(self)
        self.logger = Logger(open(self.factory.logfile, "a"))
        self.logger.log("[connected at %s]" %
                        time.asctime(time.localtime(time.time())))

    # callback
    def connectionLost(self, reason):
        irc.IRCClient.connectionLost(self, reason)
        self.logger.log("[disconnected at %s]" %
                        time.asctime(time.localtime(time.time())))
        self.logger.close()

    # callback
    def signedOn(self):
        self.msg('NickServ', 'identify %s' % conf.password)
        self.join(self.factory.channel)

    # callback
    def privmsg(self, user, channel, msg):
        user = user.split('!', 1)[0]
        ievent = IrcEvent(user, channel, msg)

        if msg[0] == '.':
            cmd = get_command(msg)
        else:
            if channel == self.nickname:
                cmd = get_command(msg)
            else:
                cmd = None

        print user, channel, msg
        if user == 'NickServ' or channel == "*":
            # this is a message from the server, temporarily just skip it
            # TODO: maybe handle authentication here?
            return

        self.logger.log("<%s> %s" % (user, msg))

        # execute the plugin if a command is passed
        if cmd and check_args(cmd, self, ievent):
            plugin_run(cmd, self, ievent)

    # callback
    def action(self, user, channel, msg):
        """This will get called when the bot sees someone do an action."""
        user = user.split('!', 1)[0]
        self.logger.log("* %s %s" % (user, msg))

    # callback
    def irc_NICK(self, prefix, params):
        """Called when an IRC user changes their nickname."""
        old_nick = prefix.split('!')[0]
        new_nick = params[0]
        self.logger.log("-!- %s is now known as %s" % (old_nick, new_nick))

    # callback
    def userJoined(self, user, channel):
        """Called when I see another user joining a channel."""
        self.logger.log("-!- %s joined %s" % (user, channel))

    # callback
    def userLeft(self, user, channel):
        """Called when I see another user leaving a channel."""
        self.logger.log("-!- %s has left %s" % (user, channel))

    # callback
    def userQuit(self, user, msg):
        """Called when I see another user disconnect from the network."""
        self.logger.log("-!- %s has quit (%s)" % (user, msg))

    # callback
    def userKicked(self, kickee, channel, kicker, message):
        """Called when I observe someone else being kicked from a channel."""
        self.logger.log("-!- %s has been kicked by %s (%s)" % (kickee, kicker, message))

class MyBotFactory(protocol.ClientFactory):
    protocol = MyBot

    def __init__(self, channel, nickname="pollirio"):
        self.channel = channel
        self.nickname = nickname
        self.logfile = "%s.log" % self.channel[1:]

    def clientConnectionLost(self, connector, reason):
        print "Lost connection (%s), reconnecting." % (reason,)
        connector.connect()

    def clientConnectionFailed(self, connector, reason):
        print "Could not connect: %s" % (reason,)

def main():
    log.startLogging(sys.stdout)

    reactor.connectTCP(conf.server_addr, conf.server_port, MyBotFactory(conf.channel, conf.nickname))
    reactor.run()

if __name__ == "__main__":
    main()
