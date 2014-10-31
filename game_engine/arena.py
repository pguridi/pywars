# encoding=utf-8

import time
import numpy
import logging

from .basebot import DIRECTIONS, LightCycleBaseBot
from .worker import RemoteInstance

logger = logging.getLogger(__name__)


class LightCycleArena(object):

    PLAYING = 0
    LOST = 1
    WINNER = 2

    def __init__(self, players, width=100, height=100):
        self.width = width
        self.height = height
        self.players = players
        self.match = LightCycleMatch(width, height, players)
        self.setup()

    def setup(self):
        self.arena = numpy.zeros(shape=(self.width, self.height), dtype=numpy.int8)
        for i, player in enumerate(self.players, 1):
            player.color = i
            player.status = self.PLAYING
            player._botproxy = RemoteInstance(player.bot, timeout=.02,
                    namespace={'LightCycleBaseBot':LightCycleBaseBot},
                    validator=lambda x: issubclass(x, LightCycleBaseBot) and x is not LightCycleBaseBot,
                    )
            x = self.width * i / (len(self.players) + 1)
            y = self.height * i / (len(self.players) + 1)
            self.move(player, x, y)

    def move(self, player, x, y, direction=None):
        #print player.username, '==>', x, y
        assert(player in self.players)
        assert(0 <= x < self.width)
        assert(0 <= y < self.height)
        player.x, player.y, player.direction = x, y, direction
        occupied = not self.arena[x, y]
        self.arena[player.x, player.y] = player.color
        self.match.log(player, player.x, player.y, direction)
        #print self.arena.T
        #print
        assert(occupied)

    def start(self):
        try:
            logging.info('Starting match "%s"' % (' vs '.join([player.username for player in self.players])))
            for step in xrange(self.width * self.height):
                playing = [player for player in self.players
                                    if player.status == self.PLAYING]
                # Check if there's just one player playing. That's the winner!
                if len(playing) == 0:
                    break  # A tie... Everybody loses :-(
                if len(playing) == 1:
                    self.match.winner(playing[0])
                    break  # There's one winner!! :-D
                for player in self.players:
                    arena_snapshot = self.arena.copy()
                    try:
                        movement = player._botproxy.get_next_step(arena_snapshot, player.x, player.y, player.direction)
                        if isinstance(movement, Exception):
                            logger.exception(movement)
                            self.match.lost(player, 'Exception (%s)' % movement)
                            continue
                        if movement not in DIRECTIONS:
                            raise RemoteInstance.InvalidOutput()
                        #print player.username, '==>', movement
                        x = player.x + DIRECTIONS[movement].x
                        y = player.y + DIRECTIONS[movement].y
                        self.move(player, x, y, movement)
                    except RemoteInstance.InvalidOutput:
                        logger.info('Invalid output! %s %s', player.username, movement)
                        self.match.lost(player, u'Invalid output')
                    except RemoteInstance.Timeout:
                        logger.info('TIME UP! %s', player.username)
                        self.match.lost(player, u'Timeout')
                    except:
                        logger.info('CRASHED! %s %s %s', player.username, player.x, player.y)
                        self.match.lost(player, u'Crashed')
        finally:
            self.match.end()
            #import json
            #print json.dumps(self.match.__json__())
            for player in self.players:
                player._botproxy.terminate()
            return self.match.__json__()


class LightCycleMatch(object):

    def __init__(self, width, height, players):
        self.width = width
        self.height = height
        self.players = players
        self.moves = []
        self.result = {}
        self.start_time = time.time()

    def log(self, player, x, y, direction=None):
        self.moves.append(dict(
            player=player.username,
            x=x,
            y=y,
            direction=direction,
        ))

    def winner(self, player):
        player.status = LightCycleArena.WINNER
        self.result['winner'] = player.username

    def lost(self, player, cause):
        player.status = LightCycleArena.LOST
        if 'lost' not in self.result:
            self.result['lost'] = {}
        self.result['lost'][player.username] = cause

    def end(self):
        self.end_time = time.time()

    def __json__(self):
        data = dict(
                width=self.width,
                height=self.height,
                players=[player.username for player in self.players],
                moves=self.moves,
                result=self.result,
                elapsed=self.end_time - self.start_time,
                )
        return data
