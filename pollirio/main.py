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
from collections import defaultdict

from pollirio.modules import plugin_run, check_args
from pollirio.reactors import reactor_run
from pollirio import commands, reactors
from pollirio import get_command
from pollirio import conf

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
        try:
            self.nick, self.host = username.split('!', 1)
        except ValueError:
            self.nick, self.host = (username, username)
        self.user = username
        self.channel = channel
        self.msg = msg
        self.args = self.msg.split()[1:]

class MyBot(irc.IRCClient):
    def _get_nickname(self):
        return self.factory.nickname
    nickname = property(_get_nickname)

    userlist = {}

    # override IRCClient's methods, just to get them logged
    def msg(self, channel, message):
        irc.IRCClient.msg(self, channel, message)
        if message.find("ACTION") == -1:
            if channel[1:] in self.loggers.keys():
                self.loggers[channel[1:]].log("<%s> %s" % (conf.nickname, message))

    def describe(self, channel, message):
        irc.IRCClient.describe(self, channel, message)
        if channel[1:] in self.loggers.keys():
            self.loggers[channel[1:]].log("* %s %s" % (conf.nickname, message))

    # callback
    def connectionMade(self):
        irc.IRCClient.connectionMade(self)
        self.loggers = {}
        self.loggers['server'] = Logger(open('logs/server.log', 'a'))
        self.loggers['server'].log("[connected at %s]" %
                        time.asctime(time.localtime(time.time())))

    # callback
    def connectionLost(self, reason):
        irc.IRCClient.connectionLost(self, reason)
        for l in self.loggers.values():
            l.log("[disconnected at %s]" %
                        time.asctime(time.localtime(time.time())))
            l.close()

    # callback
    def signedOn(self):
        self.msg('NickServ', 'identify %s %s' % (conf.nickname, conf.password))
        self.msg('NickServ', 'identify %s' % conf.password)
        self.join_channels()

    def join_channels(self):
        for ch in self.factory.channels:
            clean_name = ch[1:]
            self.loggers[clean_name] = Logger(open('logs/%s.log' % clean_name, 'a'))
            self.loggers[clean_name].log("[joined at %s]" %
                                    time.asctime(time.localtime(time.time())))
            self.join(ch)
            self.userlist[ch] = defaultdict(str)
            self.sendLine('WHO %s' % ch)

    # callback
    def irc_RPL_WHOREPLY(self, *nargs):
        server, values = nargs
        channel = values[1]
        nickname = values[5]
        mode = values[6]

        self.userlist[channel][nickname] = mode

    # callback
    def irc_RPL_ENDOFWHO(self, *nargs):
        #~ print self.userlist
        pass
        # ~ = proprietario
        # & = amministratore
        # @ = op
        # % = hop
        # + = voice

    # callback
    def privmsg(self, user, channel, msg):
        ievent = IrcEvent(user, channel, msg)

        if msg[0] == '.':
            cmd = get_command(msg)
        else:
            if channel == self.nickname:
                cmd = get_command(msg)
            else:
                cmd = None

        if ievent.nick == "NickServ" or channel == "*":
#            # TODO: check whether it really works this way
#            if "unavailable" in msg:
#                self.msg('NickServ', 'release %s %s' % (conf.nickname, conf.password))
            return

        if channel[1:] in self.loggers.keys():
            self.loggers[channel[1:]].log("<%s> %s" % (ievent.nick, msg))

        # execute the plugin if a command is passed
        if cmd and check_args(cmd, self, ievent):
            plugin_run(cmd, self, ievent)

        # run the reactors
        reactor_run(msg, self, ievent)

    # callback
    def action(self, user, channel, msg):
        """This will get called when the bot sees someone do an action."""
        user = user.split('!', 1)[0]
        if channel[1:] in self.loggers.keys():
            self.loggers[channel[1:]].log("* %s %s" % (user, msg))

    # callback
    def irc_NICK(self, prefix, params):
        """Called when an IRC user changes their nickname."""
        old_nick = prefix.split('!')[0]
        new_nick = params[0]
        for channel in self.userlist:
            if self.userlist[channel].has_key(old_nick):
                self.userlist[channel][new_nick] = self.userlist[channel][old_nick]
                del self.userlist[channel][old_nick]
        self.loggers['server'].log("-!- %s is now known as %s" % (old_nick, new_nick))

    # callback
    def userJoined(self, user, channel):
        """Called when I see another user joining a channel."""
        if channel[1:] in self.loggers.keys():
            self.loggers[channel[1:]].log("-!- %s joined %s" % (user, channel))

    # callback
    def userLeft(self, user, channel):
        """Called when I see another user leaving a channel."""
        if channel[1:] in self.loggers.keys():
            self.loggers[channel[1:]].log("-!- %s has left %s" % (user, channel))
        # cleanup userlist
        if self.userlist.has_key(channel):
            try:
                del self.userlist[channel][user]
            except KeyError:
                pass

    # callback
    def userQuit(self, user, msg):
        """Called when I see another user disconnect from the network."""
        self.loggers['server'].log("-!- %s has quit (%s)" % (user, msg))

    # callback
    def kickedFrom(self, channel, kicker, message):
        """ Called when I am kicked from a channel. """
        self.join(channel)

    # callback
    def userKicked(self, kickee, channel, kicker, message):
        """Called when I observe someone else being kicked from a channel."""
        if channel[1:] in self.loggers.keys():
            self.loggers[channel[1:]].log("-!- %s has been kicked by %s (%s)" % (kickee, kicker, message))
        # cleanup userlist
        if self.userlist.has_key(channel):
            try:
                del self.userlist[channel][kickee]
            except KeyError:
                pass

    # callback
    def modeChanged(self, user, channel, set, modes, args):
        changer = user.split('!', 1)[0]
        if channel and args:
            subject = args[0]
            if not subject:
                return

            # TODO: owner e admin sono settabili/revocabili? IMHO no.
            umodes = []
            if 'o' in modes:
                umodes.append('@')
            if 'h' in modes:
                umodes.append('%')
            if 'v' in modes:
                umodes.append('+')

            if set:
                # modes being added
                self.userlist[channel][subject] += ''.join(umodes)
            else:
                # modes being removed
                for m in umodes:
                    self.userlist[channel][subject] = self.userlist[channel][subject].replace(m, '')

class MyBotFactory(protocol.ClientFactory):
    protocol = MyBot

    def __init__(self, channels, nickname="pollirio"):
        self.channels = channels.split('\n')
        self.nickname = nickname

    def clientConnectionLost(self, connector, reason):
        print "Lost connection (%s), reconnecting." % (reason,)
        connector.connect()

    def clientConnectionFailed(self, connector, reason):
        print "Could not connect: %s" % (reason,)

def main():
    log.startLogging(sys.stdout)

    reactor.connectTCP(conf.server_addr, conf.server_port, MyBotFactory(conf.channels, conf.nickname))
    reactor.run()

if __name__ == "__main__":
    main()
