# encoding=utf-8

import sys
import time
import logging
import importlib

from exceptions import InvalidTurnOutput, BotTimeoutException

FREE = 0

logger = logging.getLogger(__name__)

ACTION_MOVE = 0


def resolve_move_action(player, action, arena):
    new_x = player.x + (player.x_factor * action)
    if 0 <= new_x <= arena.width:
        arena[player.x][player.y] = FREE
        player.x = new_x
        arena[player.x][player.y] = player.color
        arena.match.trace_action(dict(action="make_move",
                                      player=player.username,
                                      position=[player.x, player.y], ))

def resolve_shoot_action(context):
    pass

ACTION_HANDLERS = {ACTION_MOVE: resolve_move_action}



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

            x = i if i % 2 != 0 else self.width - i
            y = 0
            self.setup_new_player(player, x, y, width)
        return

    def setup_new_player(player, x, y, width):
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
        return

    def move(self, player, x, y, direction=None):
        player.x, player.y, player.direction = x, y, direction
        self.arena[player.x][player.y] = player.color
        self.match.log(player, player.x, player.y, direction)

    def start(self):
        try:
            logging.info('Starting match "%s"' % (' vs '.join([player.username for player in self.players])))
            context_info = {}
            for player in self.players:
                arena_snapshot = self.arena.copy()
                try:
                    action = player.evaluate_turn(arena_snapshot, context_info)
                    # Here the engine calculates the new status
                    # according to the response and updates all tables
                    #self.engine.resolve_action(arena_snapshot, player, action)
                    if action in (BACK, FORWARD):
                        ACTION_HANDLERS[ACTION_MOVE](arena_snapshot, player, action)
                    else:
                        ACTION_HANDLERS[action](arena_snapshot, player, action)
                except InvalidTurnOutput:
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
