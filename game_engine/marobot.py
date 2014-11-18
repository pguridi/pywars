import math


class Bot(object):

    def __init__(self):
        self.prev = None
        self.next = 1
        self.life = None
        self.FORWARD = 1
        self.BACK = -1
        self.SHOOT = 2
        self.angle = 45
        self.speed = 35
        self.prev_adj = 1

    def evaluate_turn(self, feedback, life):
        '''
        :param feedback: (dict) the result of the previous turn,
            ie: for the move action 'SUCCESS' is returned when the enemy
            received a hit, or 'FAILED' when missed the shot.
        {'RESULT': 'SUCCESS' | 'FAILED', Result of the action
         'POSITION': (x, y) | None, In case of move success, or at start
         'MISSING': 'HOT' | 'WARM' | 'COLD' | None, Depending how close the last
         impact was, if applicable }
        :param life: Current life level, An integer between between 0-100.
        :return: see the comments above
        '''
        self.life = self.life or life
        if self.life > life:  # being hitted
            self.life = life
            next = self.BACK if self.prev == self.FORWARD else self.FORWARD
            self.prev = next
            return {'ACTION': 'MOVE', 'WHERE': next}
        if self.prev == self.SHOOT:
            if feedback['RESULT'] == 'SUCCESS':
                self.prev = self.SHOOT
                return {'ACTION': 'SHOOT', 
                        'VEL': self.speed, 
                        'ANGLE': self.angle}
            else:
                if feedback['MISSING'] == 'COLD':  # way too far  
                    self.angle += self.prev_adj * 10
                elif feedback['MISSING'] == 'WARM':
                    self.angle += 5 * self.prev_adj
                else:
                    self.angle += 1 * self.prev_adj
                self.prev_adj *= -2
                return {'ACTION': 'SHOOT', 'VEL': self.speed, 'ANGLE': self.angle}
        elif self.prev in (self.BACK, self.FORWARD) or self.prev is None:
            self.prev = self.SHOOT
            return {'ACTION': 'SHOOT', 'VEL': self.speed, 'ANGLE': self.angle}
