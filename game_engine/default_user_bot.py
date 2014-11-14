# Example responses:
#
# Move forwards:
#   return {'ACTION': 'MOVE', 'WHERE': 1}
#
# Move backwards:
#   return {'ACTION': 'MOVE', 'WHERE': -1}
#
# Shooting projectile:
#   return {'ACTION': 'SHOOT', 'VEL': 100, 'ANGLE': 35}
#   # 'VEL' should be a value x, 0 < x < 150
#   # 'ANGLE' should be an x, 10 <= x < 90
#
#
# Do nothing:
#   return None
#
# For full API description and usage please visit the Rules section

class Bot(object):

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
        return None
