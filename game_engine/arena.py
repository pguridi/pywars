# encoding=utf-8

import sys
import time
import logging
import importlib
import math
from exceptions import InvalidBotOutput, BotTimeoutException

logger = logging.getLogger(__name__)


FREE = 0

def shoot_projectile(speed, angle, starting_height=0.0, gravity=9.8):
    '''
    returns a list of (x, y) projectile motion data points
    where:
    x axis is distance (or range) in meters
    y axis is height in meters
    '''
    data_xy = []
    t = 0.0
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
    return data_xy

def resolve_move_action(arena, player, where):
    new_x = player.x + (player.x_factor * where)
    if 0 <= new_x <= arena.width:
        arena[player.x][player.y] = FREE
        player.x = new_x
        arena[player.x][player.y] = player.color
        arena.match.trace_action(dict(action="make_move",
                                      player=player.username,
                                      position=[player.x, player.y], ))

def resolve_shoot_action(arena, player, speed, angle):
    trajectory = shoot_projectile(speed, angle)


# class Engine(object):  # FIXME: rename
#
#     def resolve_action(self, arena, player, action, feedbacks, damages):
#         """Given an <action> performed by <player>, determine its result in
#         the context of the game."""
#         if action in (BACK, FORWARD):
#             new_x = player.x + (player.x_factor * action)
#             if 0 <= new_x <= arena.width:
#                 arena[player.x][player.y] = FREE
#                 player.x = new_x
#                 arena[player.x][player.y] = player.color
#                 arena.match.trace_action(dict(action="make_move",
#                                               player=player.username,
#                                               position=[player.x, player.y], ))
#         elif action == FIRE:
#             pass
#         else:
#             assert 0, "Invalid action"  # TODO: raise exception
#         return


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
        self.setup()

    def setup(self):
        self.arena = [FREE for _ in self.width for __ in self.height]
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
        self.arena[x][y] = player.color
        x_factor = 1 if x <= width // 2 else -1
        player.assign_team(x_factor)
        self.match.trace_action(dict(action="new_player",
                                     name=player.username,
                                     position=[x, y],
                                     tank=player.bot.__class__.__name__,
                                     ))

    def move(self, player, x, y, direction=None):
        player.x, player.y, player.direction = x, y, direction
        self.arena[player.x][player.y] = player.color
        self.match.log(player, player.x, player.y, direction)

    def _validate_bot_output(self, bot_output):
        try:
            if bot_output == None:
                # None is a valid command, do nothing
                return
            if bot_output['ACTION'] == 'MOVE':
                if int(bot_output['WHERE']) not in [-1, 1]:
                    # for moving, valid integers are: -1 or 1
                    raise InvalidBotOutput()
            elif bot_output['ACTION'] == 'SHOOT':
                if int(bot_output['VEL']) not in range(1, 151):
                    # velocity must be an integer between 1 and 150
                    raise InvalidBotOutput()
                if int(bot_output['ANGLE']) not in range(10, 90):
                    # angle must be an integer between 10 and 89
                    raise InvalidBotOutput()
        except:
            raise InvalidBotOutput()

    def start(self):
        try:
            logging.info('Starting match "%s"' % (' vs '.join([player.username for player in self.players])))
            context_info = {}
            for player in self.players:
                arena_snapshot = self.arena.copy()
                try:
                    bot_response = player.evaluate_turn(arena_snapshot, context_info)
                    self._validate_bot_output(bot_response)
                    # Here the engine calculates the new status
                    # according to the response and updates all tables
                    if bot_response['ACTION'] == 'MOVE':
                        resolve_move_action(arena_snapshot, player, bot_response['WHERE'])
                    elif bot_response['ACTION'] == 'SHOOT':
                        resolve_shoot_action(arena_snapshot, player, bot_response['VEL'], bot_response['ANGLE'])
                except InvalidBotOutput:
                    logger.info('Invalid output! %s', player.username)
                    self.match.lost(player, u'Invalid output')
                except BotTimeoutException:
                    logger.info('TIME UP! %s', player.username)
                    self.match.lost(player, u'Timeout')
                except Exception as e:
                    logger.info('CRASHED! %s %s %s', player.username, player.x, player.y)
                    self.match.lost(player, u'Crashed')
        finally:
            self.match.end()
            # TODO: self.match.trace_action(GAME OVER)
            return self.match.__json__()


class BattleGroundMatchLog(object):
    """Represents the match log among players, the entire game."""

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


class BotPlayer(object):

    def __init__(self, bot_filename):
        bot_file = bot_filename.replace(".py", "")
        i = importlib.import_module(bot_file)
        self._bot = i.Bot()

    def evaluate_turn(self, context_info):
        # Ask bot what to do this turn
        return self._bot.evaluate_turn(context_info)


def main(argv):
    player1_file = argv[0]
    player2_file = argv[1]

    bot1 = BotPlayer(player1_file)
    bot2 = BotPlayer(player2_file)

    engine = BattleGroundArena(players=[bot1, bot2])
    game_result = engine.start()
    print game_result
    sys.exit(0)


if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Please specify 2 bot files")
        sys.exit(1)

    main(sys.argv[1:])
