# encoding=utf-8

import random


BACK = -1
FORWARD = 1
FIRE = 0  # FIXME: should be a string with the params

ACTIONS = {
  BACK: 'back',
  FORWARD : 'forward',
  FIRE : 'fire',
}

HIT = 1
GROUND = 0


class BattleGroundBot(object):

    def get_next_step(self, arena, feedback, damage):
        """arena: A copy of the battlefield
        feedback: The result of my last action: HIT | GROUND
        damage (:int:): Indicates if other player attacked me or 0 if not.
        """
        raise NotImplementedError('Should return one valid action.')


class LightCycleRandomBot(BattleGroundBot):

    def get_next_step(self, arena, feedback, damage):
        return random.choice([ACTIONS.keys()])
