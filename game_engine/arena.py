# encoding=utf-8

import sys
import importlib
import math
from exc import (
    InvalidBotOutput,
    BotTimeoutException,
    MissedTargetException,
    TankDestroyedException,
    GameOverException,
)

#Exit error codes
EXIT_ERROR_NUMBER_OF_PARAMS  = 1
EXIT_ERROR_MODULE = 2
EXIT_ERROR_BOT_INSTANCE = 3

# Constants we use in the game
FREE = 0
DAMAGE_DELTA = 25
REPAIR_DELTA = 10
INITIAL_HEALTH = 100
FAILED = 'FAILED'
SUCCESS = 'SUCCESS'
LOSER = 'loser'
WINNER = 'winner'
DRAW = 'draw'
RESULT = 'result'
ACTION = 'action'
TANK_LENGTH = 3


def shoot_projectile(speed, angle, starting_height=0.0, gravity=9.8,
                     x_limit=1000):
    '''
    returns a list of (x, y) projectile motion data points
    where:
    x axis is distance (or range) in meters
    y axis is height in meters
    :x_limit: Indicates if the trajectory is going out of the grid
    '''
    x = 0.0
    data_xy = []
    t = 0.0
    angle = math.radians(angle)
    while True:
        # now calculate the height y
        y = starting_height + (t * speed * math.sin(angle)) - (gravity * t * t)/2
        # projectile has hit ground level
        if y < 0 or x > x_limit:
            break
        # calculate the distance x
        x = speed * math.cos(angle) * t
        # append the (x, y) tuple to the list
        data_xy.append((x, y))
        # use the time in increments of 0.1 seconds
        t += 0.1
    return data_xy


class ArenaGrid(object):
    """The grid that represents the arena over which the players are playing.
    """
    def __init__(self, width, height):
        self.width = width
        self.height = height
        self.arena = [FREE for _ in xrange(self.width)]

    def copy_for_player(self):
        """Return just a copy of the portion we provide to the player."""
        return self.arena[:]

    def players_distance(self):
        """Return the distance between the bots. Only two players."""
        p1, p2 = [i for i in xrange(self.width) if self.arena[i] != FREE]
        return p2 - p1

    def __getitem__(self, (x, y)):
        return self.arena[x]

    def __setitem__(self, (x, y), value):
        self.arena[x] = value


class Context(object):
    FEEDBACK = 1
    LIFE = 2

    def __init__(self, players):
        self.info = {player: {self.FEEDBACK: None,
                              self.LIFE: INITIAL_HEALTH} for player in players}
        self.affected_player = None

    def feedback(self, player):
        return self.info[player][self.FEEDBACK]

    def provide_feedback(self, player, feedback):
        self.info[player][self.FEEDBACK] = feedback

    def decrease_life(self, player, amount):
        self.info[player][self.LIFE] -= amount
        if self.info[player][self.LIFE] <= 0:
            self.affected_player = player  # whose tank was just destroyed
            raise TankDestroyedException()

    def repair_tank(self, player):
        """If a player action returns None, it repairs its tank."""
        if self.info[player][self.LIFE] + REPAIR_DELTA <= INITIAL_HEALTH:
            self.info[player][self.LIFE] += REPAIR_DELTA
        else:
            self.info[player][self.LIFE] = INITIAL_HEALTH

    def life(self, player):
        return self.info[player][self.LIFE]

    def current_points(self):
        """Returns the current points per player, mapping
        player:life"""
        return {p: d.get(self.LIFE) for p, d in self.info.iteritems()}


class BattleGroundArena(object):
    """The game arena."""

    PLAYING = 0
    LOST = 1
    WINNER = 2

    def __init__(self, players, width=80, height=50):
        self.width = width
        self.height = height
        self.rounds = xrange(100)
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
                # velocity must be an integer between 1 and 150
                #if not (1 <= int(bot_output['VEL']) <= 150):
                    #raise InvalidBotOutput("Velocity not in range [1, 150].")
                # angle must be an integer between 10 and 89
                if not (10 <= int(bot_output['ANGLE']) <= 89):
                    raise InvalidBotOutput("Angle must be between 10 and 89")
        except Exception as e:
            raise InvalidBotOutput(str(e))

    def start(self):
        for _ in self.rounds:
            try:
                for player in self.players:
                    try:
                        bot_response = player.evaluate_turn(self.context.feedback(player),
                                                            self.context.life(player))
                        self._validate_bot_output(bot_response)
                        if bot_response is None:
                            self.context.repair_tank(player)
                            self.match.trace_action(dict(
                                action="idle",
                                player=player.username,
                                position=[player.x, player.y],
                                health=self.context.life(player),
                                ))
                            continue
                        # Here the engine calculates the new status
                        # according to the response and updates all tables
                        if bot_response['ACTION'] == 'MOVE':
                            self.resolve_move_action(player, bot_response['WHERE'])
                        elif bot_response['ACTION'] == 'SHOOT':
                            self.resolve_shoot_action(player,
                                                      bot_response['VEL'],
                                                      bot_response['ANGLE'])
                    except (InvalidBotOutput,
                            BotTimeoutException,
                            TankDestroyedException) as e:
                        self.match.lost(self.context.affected_player or player,
                                        e.reason)
                        raise GameOverException(str(e))
                    except Exception as e:
                        self.match.lost(player, u'Crashed')
                        raise GameOverException(str(e))
            except GameOverException as e:
                #print e
                break
        else:  # for-else, if all rounds are over
            table = self.context.current_points()
            points = {}
            #print(table)
            for p, life in table.iteritems():
                points[life] = points.get(life, []) + [p]
            top = max(points)
            if len(points[top]) > 1:  # draw
                self.match.draw()
            else:  # The player with more resistence wins
                self.match.winner(points[top][0])
        return self.match.__json__()

    def _check_player_boundaries(self, player, new_x):
        half = self.width // 2
        if player.x_factor == 1:
            return 0 <= new_x <= half
        elif player.x_factor == -1:
            return half <= new_x <= self.width
        else:
            raise Exception("Invalid player location")

    def resolve_move_action(self, player, where):
        new_x = player.x + (player.x_factor * where)
        if self._check_player_boundaries(player, new_x):
            self.arena[player.x, player.y] = FREE
            player.x = new_x
            self.arena[player.x, player.y] = player.color
            # Trace what just happened in the match
            self.match.trace_action(dict(action="make_move",
                                         player=player.username,
                                         position=[player.x, player.y], ))
            # Tell the user it moved successfully
            self.context.provide_feedback(player, SUCCESS)
        else:
            self.context.provide_feedback(player, FAILED)

    def adjust_player_shoot_trajectory(self, player, trajectory):
        """Depending on which side of the arena :player: is, we need or not to
        reverse the x coordinates.
        Calibrate according to the position of :player:"""
        if player.x_factor == -1:  # Side B, symetric x
            trajectory = trajectory[::-1]
        initial_x = trajectory[0][0]  #  x of the first coord
        delta_x = player.x - initial_x
        trajectory = [(x + delta_x, y) for x, y in trajectory]
        x_off = lambda i: round(i, 1) if player.x_factor == -1 else int(i)
        return [(x_off(x), round(y, 1)) for x, y in trajectory]

    def _scale_coords(self, (x, y)):
        """Given impact coords (x, y), translate their numbers to our arena
        grid.
        Current Scale: 1m² per grid cell"""
        if y <= 3:
            y = 0
        return int(round(x)), int(round(y))

    def resolve_shoot_action(self, player, speed, angle):
        trajectory = shoot_projectile(speed, angle, x_limit=self.width)
        trajectory = self.adjust_player_shoot_trajectory(player, trajectory)
        # Log the shoot made by the player
        self.match.trace_action(dict(action="make_shoot",
                                     player=player.username,
                                     angle=angle,
                                     speed=speed,
                                     trajectory=trajectory))
        # Get the impact coordinates
        x_imp, y_imp = self._scale_coords(trajectory[-1])
        try:
            affected_players = [p for p in self.players
                                if p.x == x_imp and p.y == y_imp]
            if not affected_players:
                raise MissedTargetException
        except MissedTargetException:
            self.context.provide_feedback(player, FAILED)
        else:
            self.context.provide_feedback(player, SUCCESS)
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
        self.game_over_template = {'action': 'game_over',
                                   'winner': '',
                                   'loser': '',
                                   'draw': False,
                                   'reason': ''}

    def trace_action(self, arena_action):
        """Receive an action performed on the arena, and log it as a part of
        the match."""
        self.trace.append(arena_action)

    def draw(self):
        self.game_over_template['draw'] = True
        self.trace_action(self.game_over_template)

    def winner(self, player):
        player.status = BattleGroundArena.WINNER
        self._trace_game_over('winner', 'loser', player, 'Max points')

    def lost(self, player, cause):
        player.status = BattleGroundArena.LOST
        self._trace_game_over('loser', 'winner', player, cause)

    def _trace_game_over(self, k1, k2, player, cause):
        self.game_over_template[k1] = player.username
        self.game_over_template['reason'] = cause
        others = ','.join(p.username for p in self.players if p is not player)
        self.game_over_template[k2] = others
        self.trace_action(self.game_over_template)

    def print_trace(self):
        for i, log in enumerate(self.trace, start=1):
            print("{} - {}".format(i, log))

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
        self.x = 0
        self.y = 0

    @property
    def bot(self):
        return self._bot

    def evaluate_turn(self, feedback, life):
        # Ask bot what to do this turn
        return self._bot.evaluate_turn(feedback, life)

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
    bot2_username = bot_mod2.split("/")[-1]
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
