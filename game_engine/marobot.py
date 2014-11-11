import math


class Bot(object):

    def evaluate_turn(self, feedback, life):
        '''
        :param feedback: the result of the previous turn, ie: for the move action 'SUCCESS' is returned when the enemy
            received a hit, or 'FAILED' when missed the shot.
        :param life: Current life level, An integer between between 0-100.
        :return: see the comments above
        '''
        g = 9.8
        ANGLE = 45
        distance = 40
        v0 = (distance * g) / (math.sin(2*ANGLE)) * 1.0
        return {'ACTION': 'SHOOT', 'VEL': 40, 'ANGLE': 45}
