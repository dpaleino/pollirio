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

class MyBot(irc.IRCClient):
    def _get_nickname(self):
        return self.factory.nickname
    nickname = property(_get_nickname)

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
        self.join(self.factory.channel)

    # callback
    def privmsg(self, user, channel, msg):
        user = user.split('!', 1)[0]

        if channel == self.nickname:
            self.msg(user, "Moo, sono una mooocca!!!")
            return

        print "Message is:", msg
        self.logger.log("<%s> %s" % (user, msg))

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
    channel = "#polloalforno"
    reactor.connectTCP("calvino.freenode.net", 6667, MyBotFactory(channel))
    reactor.run()

if __name__ == "__main__":
    main()
