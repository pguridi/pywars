# encoding=utf-8

import sys
import os
import time
import logging
import subprocess
import shutil

FREE = 0

logger = logging.getLogger(__name__)


class Engine(object):  # FIXME: rename

    def resolve_action(self, arena, player, action, feedbacks, damages):
        """Given an <action> performed by <player>, determine its result in
        the context of the game."""
        if action in (BACK, FORWARD):
            new_x = player.x + (player.x_factor * action)
            if 0 <= new_x <= arena.width:
                arena[player.x][player.y] = FREE
                player.x = new_x
                arena[player.x][player.y] = player.color
                arena.match.trace_action(dict(action="make_move",
                                              player=player.username,
                                              position=[player.x, player.y], ))
        elif action == FIRE:
            pass
        else:
            assert 0, "Invalid action"  # TODO: raise exception
        return


class BattleGroundArena(object):
    """The game being preformed."""

    PLAYING = 0
    LOST = 1
    WINNER = 2

    def __init__(self, players, width=100, height=50):
        self.width = width
        self.height = height
        self.players = players
        self.match = BattleGroundMatch(width, height, players)
        self.engine = Engine()
        self.setup()

    def setup(self):
        self.arena = [FREE for _ in self.width for __ in self.height]
        self.match.trace_action(dict(action="new_arena",
                                     width=self.width,
                                     height=self.height,))
        for i, player in enumerate(self.players, start=1):
            player.color = i
            player.status = self.PLAYING
            # TODO: review
            player._botproxy = RemoteInstance(player.bot, timeout=.02,
                    namespace={'LightCycleBaseBot':LightCycleBaseBot},
                    validator=lambda x: issubclass(x, LightCycleBaseBot) and x is not LightCycleBaseBot,
                    )
            x = i if i % 2 != 0 else self.width - i
            y = 0
            self.setup_new_player(player, x, y, width)
        return

    def setup_new_player(player, x, y, width):
        """Register the new player at the (x, y) position on the arena."""
        assert(player in self.players)
        assert(0 <= x < self.width)
        assert(0 <= y < self.height)
        player.x, player.y = x, y
        self.arena[x][y] = player.color
        x_factor = 1 if x <= width // 2 else -1
        player.assign_team(x_factor)
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
                # Check if there's just one player playing. That's the winner!
                if len(playing) == 0:
                    break  # A tie... Everybody loses :-(
                if len(playing) == 1:
                    self.match.winner(playing[0])
                    break  # There's one winner!! :-D
                for player in self.players:
                    arena_snapshot = self.arena.copy()
                    try:
                        action = player._botproxy.get_next_step(arena_snapshot,
                                                                feedback=feedbacks[player],
                                                                damage=damages[player], )
                        # Here the engine calculates the new status
                        # according to the response and updates all tables
                        self.engine.resolve_action(arena_snapshot,
                                                   player,
                                                   action,
                                                   feedbacks,
                                                   damages, )
                        if isinstance(action, Exception):
                            logger.exception(action)
                            self.match.lost(player, 'Exception (%s)' % action)
                            continue
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


PYPYSANDBOX_EXE = os.path.join('/usr', 'bin', 'pypy-sandbox')


class BotPlayer(object):

    def __init__(self, bot_filename):
        self.bot_filename = bot_filename
        self._process = None
        self.run()

    def run(self):
        sandboxdir = os.path.join("/tmp", 'pyval_sandbox')
        if not os.path.exists(sandboxdir):
            os.mkdir(sandboxdir)

        shutil.copy2(os.path.abspath('bot_wrapper.py'), os.path.join(sandboxdir, "bot_wrapper.py"))
        shutil.copy2(os.path.abspath(self.bot_filename), os.path.join(sandboxdir, self.bot_filename))

        cmdargs = [PYPYSANDBOX_EXE,
                       '--tmp={}'.format(sandboxdir),
                       'bot_wrapper.py',
                       self.bot_filename]

        self._process = subprocess.Popen(cmdargs,
                                    cwd=sandboxdir,
                                    stdin=subprocess.PIPE,
                                    stdout=subprocess.PIPE)

    def execute(self, cmd):
        print "<< sending cmd: %s >>>" % cmd
        self._process.stdin.write(cmd)
        "reading.."
        return self._process.stdout.readline()


def main(argv):
    player1_file = argv[0]
    #player2_file = argv[1]

    bot1 = BotPlayer(player1_file)
    #bot2 = BotWrapper(player2_file)

    for i in xrange(0, 3):
        ret = bot1.execute("SHOOT %s,y" % str(i))
        print "[ENGINE] bot1: ", ret

    bot1.execute("END")
    #bot2.execute("END")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Please specify a bot file")
        sys.exit(1)

    main(sys.argv[1:])
