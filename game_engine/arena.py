# encoding=utf-8

import sys
import importlib
import math
from exc import (
    InvalidBotOutput,
    BotTimeoutException,
    MissedTargetException,
)

#Exit error codes
EXIT_ERROR_NUMBER_OF_PARAMS  = 1
EXIT_ERROR_MODULE = 2
EXIT_ERROR_BOT_INSTANCE = 3


FREE = 0
DAMAGE_DELTA = 5
INITIAL_HEALTH = 100
MISSED_TARGED = 'FAILED'
TARGET_HIT = 'SUCCESS'
LOSER = 'loser'
WINNER = 'winner'
DRAW = 'draw'
RESULT = 'result'
ACTION = 'action'

def shoot_projectile(speed, angle, starting_height=0.0, gravity=9.8):
    '''
    returns a list of (x, y) projectile motion data points
    where:
    x axis is distance (or range) in meters
    y axis is height in meters
    '''
    data_xy = []
    t = 0.0
    angle = math.radians(angle)
    while True:
        # now calculate the height y
        y = starting_height + (t * speed * math.sin(angle)) - (gravity * t * t)/2
        # projectile has hit ground level
        if y < 0:
            break
        # calculate the distance x
        x = speed * math.cos(angle) * t
        # append the (x, y) tuple to the list
        data_xy.append((x, y))
        # use the time in increments of 0.1 seconds
        t += 0.1
    # TODO: match every (x, y) (or at least the last one), with our grid.
    return data_xy


class ArenaGrid(object):
    """The grid that represents the arena over which the players are playing.
    """
    def __init__(self, width, height):
        self.width = width
        self.height = height
        # TODO: we only need the X axis, not the whole matrix
        self.arena = [[FREE for _ in xrange(self.height)] for __ in xrange(self.width)]

    def copy_for_player(self):
        """Return just a copy of the portion we provide to the player."""
        return [self.arena[i][0] for i in xrange(self.width)]

    def __getitem__(self, (x, y)):
        return self.arena[x][y]

    def __setitem__(self, (x, y), value):
        self.arena[x][y] = value


class Context(object):
    FEEDBACK = 1
    LIFE = 2

    def __init__(self, players):
        self.info = {player: {self.FEEDBACK: None,
                              self.LIFE: INITIAL_HEALTH} for player in players}

    def feedback(self, player):
        return self.info[player][self.FEEDBACK]

    def provide_feedback(self, player, feedback):
        self.info[player][self.FEEDBACK] = feedback

    def decrease_life(self, player, amount):
        self.info[player][self.LIFE] -= amount

    def life(self, player):
        return self.info[player][self.LIFE]


class BattleGroundArena(object):
    """The game arena."""

    PLAYING = 0
    LOST = 1
    WINNER = 2

    def __init__(self, players, width=100, height=50):
        self.width = width
        self.height = height
        self.players = players
        self.match = BattleGroundMatchLog(width, height, players)
        self.arena = ArenaGrid(self.width, self.height)
        self.context = Context(players)
        self.setup()

    def setup(self):
        self.match.trace_action(dict(action="new_arena",
                                     width=self.width,
                                     height=self.height,))
        for i, player in enumerate(self.players, start=1):
            player.color = i
            player.status = self.PLAYING

            x = i if i % 2 != 0 else self.width - i
            y = 0
            self.setup_new_player(player, x, y, self.width)

    def setup_new_player(self, player, x, y, width):
        """Register the new player at the (x, y) position on the arena."""
        player.x, player.y = x, y
        self.arena[x, y] = player.color
        x_factor = 1 if x <= (width // 2) else -1
        player.assign_team(x_factor)
        self.match.trace_action(dict(action="new_player",
                                     name=player.username,
                                     position=[x, y],
                                     tank=player.bot.__class__.__name__,
                                     ))

    def _validate_bot_output(self, bot_output):
        try:
            if bot_output is None:
                # None is a valid command, do nothing
                return
            if bot_output['ACTION'] == 'MOVE':
                if int(bot_output['WHERE']) not in (-1, 1):
                    # for moving, valid integers are: -1 or 1
                    raise InvalidBotOutput("Moving must be -1 or 1.")
            elif bot_output['ACTION'] == 'SHOOT':
                if int(bot_output['VEL']) not in range(1, 151):
                    # velocity must be an integer between 1 and 150
                    raise InvalidBotOutput("Velocity not in range [1, 150].")
                if int(bot_output['ANGLE']) not in range(10, 90):
                    # angle must be an integer between 10 and 89
                    raise InvalidBotOutput("Angle must be between 10 and 89")
        except:
            raise InvalidBotOutput()

    def start(self):
        try:
            for player in self.players:
                arena_snapshot = self.arena.copy_for_player()
                try:
                    bot_response = player.evaluate_turn(arena_snapshot,
                                                        self.context.feedback(player),
                                                        self.context.life(player))
                    self._validate_bot_output(bot_response)
                    # Here the engine calculates the new status
                    # according to the response and updates all tables
                    if bot_response['ACTION'] == 'MOVE':
                        self.resolve_move_action(player, bot_response['WHERE'])
                    elif bot_response['ACTION'] == 'SHOOT':
                        self.resolve_shoot_action(player,
                                                  bot_response['VEL'],
                                                  bot_response['ANGLE'])
                except InvalidBotOutput:
                    self.match.lost(player, u'Invalid output')
                except BotTimeoutException:
                    self.match.lost(player, u'Timeout')
                except Exception as e:
                    self.match.lost(player, u'Crashed')
        finally:
            # TODO: self.match.trace_action(GAME OVER)
            return self.match.__json__()

    def resolve_move_action(self, player, where):
        new_x = player.x + (player.x_factor * where)
        if 0 <= new_x <= self.arena.width:
            self.arena[player.x, player.y] = FREE
            player.x = new_x
            self.arena[player.x, player.y] = player.color
            # Trace what just happened in the match
            self.match.trace_action(dict(action="make_move",
                                         player=player.username,
                                         position=[player.x, player.y], ))

    def resolve_shoot_action(self, player, speed, angle):
        trajectory = shoot_projectile(speed, angle)
        # Log the shoot made by the player
        self.match.trace_action(dict(action="make_shoot",
                                     player=player.username,
                                     angle=angle,
                                     trajectory=trajectory))
        # Get the impact coordinates
        x_imp, y_imp = trajectory[-1]
        try:
            affected_players = [p for p in self.players
                                if p.x == x_imp and p.y == y_imp]
            if not affected_players:
                raise MissedTargetException
        except MissedTargetException:
            self.context.provide_feedback(player, MISSED_TARGED)
        else:
            self.context.provide_feedback(player, TARGET_HIT)
            for p in affected_players:
                self.context.decrease_life(p, DAMAGE_DELTA)
                self.match.trace_action(dict(action="health_status",
                                             player=p.username,
                                             health=self.context.life(p)))


class BattleGroundMatchLog(object):
    """Represents the match log among players, the entire game."""

    def __init__(self, width, height, players):
        self.width = width
        self.height = height
        self.players = players
        self.trace = []   # All actions performed during the match
        self.result = {}

    def trace_action(self, arena_action):
        """Receive an action performed on the arena, and log it as a part of
        the match."""
        # TODO: review
        self.trace.append(arena_action)

    def winner(self, player):  # FIXME
        player.status = BattleGroundArena.WINNER
        self.result['winner'] = player.username

    def lost(self, player, cause): # FIXME
        player.status = BattleGroundArena.LOST
        if 'lost' not in self.result:
            self.result['lost'] = {}
        self.result['lost'][player.username] = cause

    def __json__(self):
        data = dict(
                width=self.width,
                height=self.height,
                players=[player.username for player in self.players],
                actions=self.trace,
                result=self.result,
                )
        return data


class BotPlayer(object):

    def __init__(self, bot_name, bot):
        self._bot = bot
        self.x_factor = None
        self.username = bot_name

    @property
    def bot(self):
        return self._bot

    def evaluate_turn(self, arena_array, feedback, life):
        # Ask bot what to do this turn
        return self._bot.evaluate_turn(arena_array, feedback, life)

    def assign_team(self, x_factor):
        """Assign team depending on which side is allocated
        x_factor -> -1 | 1"""
        self.x_factor = x_factor


def usage():
    print "Usage: python %s player1.py player2.py. Make sure both files are valid Python scripts, importable, and implement a Bot class." % sys.argv[0]


def main(argv):
    bot_mod1 = argv[0].replace(".py", "")
    bot1_username = bot_mod1.split("/")[-1]
    bot_mod1 = bot_mod1.replace('/', '.')

    bot_mod2 = argv[1].replace(".py", "")
    bot2_username = bot_mod1.split("/")[-1]
    bot_mod2 = bot_mod2.replace('/', '.')
    try:
        bot_module1 = importlib.import_module(bot_mod1, package='bots')
        bot_module2 = importlib.import_module(bot_mod2, package='bots')
        bot1 = bot_module1.Bot()
        bot2 = bot_module2.Bot()
    except ImportError, e:
        print "Error importing bot scripts: %s." % str(e)
        usage()
        sys.exit(EXIT_ERROR_MODULE)
    except AttributeError, e:
        print "Error instancing Bot : %s." % str(e)
        usage()
        sys.exit(EXIT_ERROR_BOT_INSTANCE)

    bot1 = BotPlayer(bot1_username, bot1)
    bot2 = BotPlayer(bot2_username, bot2)

    engine = BattleGroundArena(players=[bot1, bot2])
    game_result = engine.start()
    print game_result
    sys.exit(0)

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Please specify 2 bot files")
        usage()
        sys.exit(EXIT_ERROR_NUMBER_OF_PARAMS)

    main(sys.argv[1:])
