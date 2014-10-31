# encoding=utf-8

import random
from collections import namedtuple


Point = namedtuple('Point', 'x y')

DIRECTIONS = {
    'N': Point(0, -1),
    'E': Point(1, 0),
    'S': Point(0, 1),
    'W': Point(-1, 0),
}


class LightCycleBaseBot(object):

    def get_next_step(self, arena, x, y, direction):
        raise NotImplementedError('Should return one Direction.')


class LightCycleRandomBot(LightCycleBaseBot):

    def get_next_step(self, arena, x, y, direction):
        possible_movements = [key for key, value in DIRECTIONS.items()
                               if 0 <= x + value.x < arena.shape[0]
                               and 0 <= y + value.y < arena.shape[1]
                               and not arena[x + value.x, y + value.y]]
        #print possible_directions
        if direction in possible_movements:
            return direction
        else:
            return random.choice(possible_movements or DIRECTIONS.keys())
