# encoding=utf-8

import time
#import numpy
import logging

from .basebot import (
    BattleGroundBot,
    HIT,
    GROUND,
    ACTIONS,
)
#from .worker import RemoteInstance

logger = logging.getLogger(__name__)


class BattleGroundArena(object):
    """The game being preformed."""

    PLAYING = 0
    LOST = 1
    WINNER = 2

    def __init__(self, players, width=100, height=100):
        self.width = width
        self.height = height
        self.players = players
        self.match = BattleGroundMatch(width, height, players)
        self.setup()

    def setup(self):
        self.arena = [0 for _ in self.width for __ in self.height]
        self.match.trace_action(dict(action="new_arena",
                                     width=self.width,
                                     height=self.height,))
        for i, player in enumerate(self.players, 1):
            player.color = i
            player.status = self.PLAYING
            # TODO: review
            player._botproxy = RemoteInstance(player.bot, timeout=.02,
                    namespace={'LightCycleBaseBot':LightCycleBaseBot},
                    validator=lambda x: issubclass(x, LightCycleBaseBot) and x is not LightCycleBaseBot,
                    )
            x = self.width * i / (len(self.players) + 1)
            y = self.height * i / (len(self.players) + 1)
            self.setup_new_player(player, x, y)
        return

    def setup_new_player(player, x, y):
        """Register the new player at the (x, y) position on the arena."""
        assert(player in self.players)
        assert(0 <= x < self.width)
        assert(0 <= y < self.height)
        player.x, player.y = x, y
        self.arena[x][y] = player.color
        self.match.trace_action(dict(action="new_player",
                                     name=player.username,
                                     position=[x, y],
                                     tank=player.bot.__class__.__name__,
                                     ))
        return

    def move(self, player, x, y, direction=None):
        #print player.username, '==>', x, y
        assert(player in self.players)
        assert(0 <= x < self.width)
        assert(0 <= y < self.height)
        player.x, player.y, player.direction = x, y, direction
        occupied = not self.arena[x][y]
        self.arena[player.x][player.y] = player.color
        self.match.log(player, player.x, player.y, direction)
        assert(occupied)

    def start(self):
        try:
            logging.info('Starting match "%s"' % (' vs '.join([player.username for player in self.players])))
            context = {}
            # Track the feedback we need to provide to every player
            feedbacks = {p: None for p in self.players if p.status == self.PLAYING}
            damages = {p: GROUND for p in self.players if p.status == self.PLAYING}
            for step in xrange(self.width * self.height):
                playing = [player for player in self.players
                                    if player.status == self.PLAYING]
                """
                # Check if there's just one player playing. That's the winner!
                if len(playing) == 0:
                    break  # A tie... Everybody loses :-(
                if len(playing) == 1:
                    self.match.winner(playing[0])
                    break  # There's one winner!! :-D
                """
                for player in self.players:
                    arena_snapshot = self.arena.copy()
                    try:
                        action = player._botproxy.get_next_step(arena_snapshot,
                                                                feedback=feedbacks[player],
                                                                damage=damages[player], )
                        # TODO: Here the engine calculates the new status
                        # according to the response and updates all tables
                        if isinstance(action, Exception):
                            logger.exception(action)
                            self.match.lost(player, 'Exception (%s)' % action)
                            continue
                        if movement not in ACTIONS:
                            raise RemoteInstance.InvalidOutput()
                        # TODO: update the context
                        #self.move(player, x, y, movement)
                    except RemoteInstance.InvalidOutput:
                        logger.info('Invalid output! %s %s', player.username, movement)
                        self.match.lost(player, u'Invalid output')
                    except RemoteInstance.Timeout:
                        logger.info('TIME UP! %s', player.username)
                        self.match.lost(player, u'Timeout')
                    # TODO: catch the event of Tank killed
                    except:
                        logger.info('CRASHED! %s %s %s', player.username, player.x, player.y)
                        self.match.lost(player, u'Crashed')
        finally:
            self.match.end()
            # TODO: self.match.trace_action(GAME OVER)
            for player in self.players:
                player._botproxy.terminate()
            return self.match.__json__()


class BattleGroundMatch(object):
    """Represents the match among players, the entire game."""

    def __init__(self, width, height, players):
        self.width = width
        self.height = height
        self.players = players
        self.trace = []   # All actions performed during the match
        self.result = {}
        self.start_time = time.time()

    def trace_action(self, arena_action):
        """Receive an action performed on the arena, and log it as a part of
        the match."""
        # TODO: review
        self.trace.append(arena_action)
        return

    def winner(self, player):
        player.status = BattleGroundArena.WINNER
        self.result['winner'] = player.username

    def lost(self, player, cause):
        player.status = BattleGroundArena.LOST
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
                actions=self.trace,
                result=self.result,
                elapsed=self.end_time - self.start_time,
                )
        return data
