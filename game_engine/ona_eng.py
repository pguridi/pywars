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

# Exit error codes
EXIT_ERROR_NUMBER_OF_PARAMS = 1
EXIT_ERROR_MODULE = 2
EXIT_ERROR_BOT_INSTANCE = 3

# Relation between our grid and the coordinates in [m]
SCALE = 60

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
# Map each firing result threshold with its feedback
HOT = 'HOT'
WARM = 'WARM'
COLD = 'COLD'


def _resolve_missing(distance):
    if distance <= 3:
        return HOT
    elif distance <= 8:
        return WARM
    else:
        return COLD


def _x_for_players(players, limit):
    """Given the list of players, return the numbers which will indicate the
    initial position of each one, according to the formula."""
    half = limit // 2
    m = len(''.join(p.username for p in players))
    n = sum(xrange(m))
    k = (n * m * 12832) % half
    return k, limit - k - 1


def shoot_projectile(speed, angle, starting_height=0.0, gravity=9.8,
                     x_limit=1000):
    '''
    returns a list of (x, y) projectile motion data points
    where:
    x axis is distance (or range) in meters
    y axis is height in meters
    :x_limit: Indicates if the trajectory is going out of the grid
    '''
    angle = math.radians(angle)
    distance = (speed ** 2) * math.sin(2*angle) / gravity
    return [(0, 0), (distance, 0)]


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


class PywarsContext(object):
    FEEDBACK = 1
    LIFE = 2

    def __init__(self, players):
        self.info = {player: {self.FEEDBACK: {},
                              self.LIFE: INITIAL_HEALTH} for player in players}
        self.affected_player = None

    def _feedback_template(self):
        return {'RESULT': None, 'POSITION': None, 'MISSING': None, }

    def feedback(self, player):
        return self.info[player][self.FEEDBACK]

    def provide_feedback(self, player, feedback):
        self.info[player][self.FEEDBACK] = feedback

    def move_feedback(self, player, ok=True):
        _tmp = self._feedback_template()
        _tmp['RESULT'] = SUCCESS if ok else FAILED
        _tmp['POSITION'] = (player.x, player.y) if ok else None
        _tmp['MISSING'] = None
        self.info[player][self.FEEDBACK] = _tmp

    def shoot_feedback(self, player, ok=True, difference=0):
        """:difference: How long the shoot was missed"""
        _tmp = self._feedback_template()
        _tmp['RESULT'] = SUCCESS if ok else FAILED
        _tmp['POSITION'] = None
        if not ok:
            _tmp['MISSING'] = _resolve_missing(difference)
        else:
            _tmp['MISSING'] = None
        self.info[player][self.FEEDBACK] = _tmp

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


def _check_allowed_modules():
    unallowed_modules = ('gc', )
    import sys;
    for mod in unallowed_modules:
        if mod in sys.modules:
            raise ImportError("Module %s is not allowed" % mod)


class PywarsArena(object):
    """The game arena."""

    PLAYING = 0
    LOST = 1
    WINNER = 2

    def __init__(self, players, width=30, height=50, randoms=None):
        self.width = width
        self.height = height
        self.rounds = xrange(100)
        self.players = players
        self.match = PywarsGroundMatchLog(width, height, players)
        self.arena = ArenaGrid(self.width, self.height)
        self.context = PywarsContext(players)
        self.randoms = randoms if randoms else []
        self.setup()

    def setup(self):
        #_check_allowed_modules()
        self.match.trace_action(dict(action="new_arena",
                                     width=self.width,
                                     height=self.height,))
        if self.randoms:
            x1, x2 = map(int, self.randoms)
        else:
            x1, x2 = _x_for_players(self.players, limit=self.width)
        for i, player in enumerate(self.players, start=1):
            player.color = i
            player.status = self.PLAYING
            # Initial position
            x = x1 if i % 2 != 0 else x2
            y = 0
            self.setup_new_player(player, x, y, self.width)

    def setup_new_player(self, player, x, y, width):
        """Register the new player at the (x, y) position on the arena."""
        player.x, player.y = x, y
        self.arena[x, y] = player.color
        x_factor = 1 if x <= (width // 2) else -1
        player.assign_team(x_factor)
        self.context.move_feedback(player, ok=True)
        self.match.trace_action(dict(action="new_player",
                                     name=player.username,
                                     position=[x * SCALE, y],
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
                # angle must be an integer between 10 and 89
                if not (10 <= int(bot_output['ANGLE']) < 90):
                    raise InvalidBotOutput("Angle must be between 10 and 89")

                if int(bot_output['VEL']) >= 132:
                    bot_output['VEL'] = 132
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
                            self.resolve_move_action(player,
                                                     bot_response['WHERE'])
                        elif bot_response['ACTION'] == 'SHOOT':
                            self.resolve_shoot_action(player,
                                                      bot_response['VEL'],
                                                      bot_response['ANGLE'])
                    except (InvalidBotOutput,
                            BotTimeoutException,
                            TankDestroyedException) as e:
                        p = self.context.affected_player or player
                        self.match.trace_action(dict(action="make_healthy",
                                                     player=p.username,
                                                     health_value=self.context.life(p)))
                        self.match.lost(self.context.affected_player or player,
                                        e.reason)
                        raise GameOverException(str(e))
                    except Exception as e:
                        self.match.lost(player, u'Crashed')
                        raise GameOverException(str(e))
            except GameOverException as e:
                break
        else:  # for-else, if all rounds are over
            table = self.context.current_points()
            points = {}
            for p, life in table.iteritems():
                points[life] = points.get(life, []) + [p]
            top = max(points)
            if len(points[top]) > 1:  # draw
                self.match.draw()
            else:  # The player with more resistence wins
                self.match.winner(points[top][0])
        from pprint import pprint
        pprint(self.match.__json__())
        return ''

    def _check_player_boundaries(self, player, new_x):
        assert player.x_factor in [-1, 1]
        half = self.width // 2
        if player.x_factor == 1:
            #Do not include half for ANY player, to avoid crashes
            return 0 <= new_x < half
        #player.x_factor == -1, idem: half is not valid location:
        return half < new_x < self.width

    def resolve_move_action(self, player, where):
        new_x = player.x + (player.x_factor * where)
        if self._check_player_boundaries(player, new_x):
            self.arena[player.x, player.y] = FREE
            player.x = new_x
            self.arena[player.x, player.y] = player.color
            # Tell the user it moved successfully
            self.context.move_feedback(player, ok=True)
        else:
            self.context.move_feedback(player, ok=False)
        # Trace what just happened in the match
        self.match.trace_action(dict(action="make_move",
                                     player=player.username,
                                     position=[player.x * SCALE, player.y], ))

    def adjust_player_shoot_trajectory(self, player, trajectory):
        """Depending on which side of the arena :player: is, we need or not to
        reverse the x coordinates.
        Calibrate according to the position of :player:"""
        if player.x_factor == -1:  # Side B, symetric x
            trajectory = trajectory[::-1]
        initial_x = trajectory[0][0]  # x of the first coord
        delta_x = player.x - initial_x
        trajectory = [(x + delta_x, y) for x, y in trajectory]
        #x_off = lambda i: int(i) if player.x_factor == -1 else int(i)
        #return [(int(x), int(y)) for x, y in trajectory]
        initial_x = player.x
        shoot_x = initial_x + int((trajectory[1][0] )/SCALE)

        shoot = [(initial_x,0) ,( shoot_x,0)]
     #   print("SHOOT %s Factor %s Trajectory %s" % (shoot, player.x_factor, trajectory[1][0]))
        return shoot


    def _scale_coords(self, (x, y)):
        """Given impact coords (x, y), translate their numbers to our arena
        grid.
        Current Scale: 1m² per grid cell"""
        if y <= 3:
            y = 0
        return int(round(x)), int(round(y))

    def get_adjusted_angle(self, player, angle):
        if (player.x_factor == -1):
            return angle + 90
        return angle

    def resolve_shoot_action(self, player, speed, angle):
        trajectory = shoot_projectile(speed, angle, x_limit=self.width)
        trajectory = self.adjust_player_shoot_trajectory(player, trajectory)
        x_m_origen, x_m_destino = trajectory[0][0], trajectory[1][0]

        # Log the shoot made by the player
        self.match.trace_action(dict(action="make_shoot",
                                     player=player.username,
                                     angle=self.get_adjusted_angle(player, angle),
                                     speed=speed,
                                     trajectory=trajectory,
                                     ))
        # Get the impact coordinates
        #x_imp, y_imp = self._scale_coords(trajectory[-1])
        # Correct x_imp according to our scale
        x_imp = x_m_destino
        try:
            affected_players = [p for p in self.players if p.x == x_imp]
            if not affected_players:
                raise MissedTargetException
        except MissedTargetException:
            other_x = [p.x for p in self.players if p is not player][0]
            difference = (x_imp - other_x) * player.x_factor
            self.context.shoot_feedback(player, ok=False,
                                        difference=difference)
        else:

            self.context.shoot_feedback(player, ok=True)
            for p in affected_players:
                #print "affected players found"
                self.context.decrease_life(p, DAMAGE_DELTA)
                self.match.trace_action(dict(action="make_healthy",
                                             player=p.username,
                                             health_value=self.context.life(p)))


class PywarsGroundMatchLog(object):
    """Represents the match log among players, the entire game."""

    def __init__(self, width, height, players):
        self.width = width
        self.height = height
        self.players = players
        self.trace = []   # All actions performed during the match
        self.game_over_template = {ACTION: RESULT,
                                   WINNER: None,
                                   LOSER: None,
                                   DRAW: False,
                                   'reason': ''}

    def trace_action(self, arena_action):
        """Receive an action performed on the arena, and log it as a part of
        the match."""
        self.trace.append(arena_action)

    def draw(self):
        self.game_over_template[DRAW] = True
        self.trace_action(self.game_over_template)

    def winner(self, player):
        player.status = PywarsArena.WINNER
        self._trace_game_over(WINNER, LOSER, player, 'Max points')

    def lost(self, player, cause):
        player.status = PywarsArena.LOST
        self._trace_game_over(LOSER, WINNER, player, cause)

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
        data = dict(width=self.width,
                    height=self.height,
                    players=[player.username for player in self.players],
                    actions=self.trace,
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
    randoms = argv[2:]
    try:
        bot_module1 = importlib.import_module(bot_mod1, package='bots')
        bot_module2 = importlib.import_module(bot_mod2, package='bots')
        bot1 = bot_module1.Bot()
        bot2 = bot_module2.Bot()
    except ImportError, e:
        print "Error importing bot scripts: %s." % str(e)
        usage()
        raise e
    except AttributeError, e:
        print "Error instancing Bot : %s." % str(e)
        usage()
        sys.exit(EXIT_ERROR_BOT_INSTANCE)

    bot1 = BotPlayer(bot1_username, bot1)
    bot2 = BotPlayer(bot2_username, bot2)

    engine = PywarsArena(players=[bot1, bot2], randoms=randoms)
    game_result = engine.start()
    print game_result
    sys.exit(0)


if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Please specify 2 bot files")
        usage()
        sys.exit(EXIT_ERROR_NUMBER_OF_PARAMS)

    main(sys.argv[1:])
