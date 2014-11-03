# Example responses:
#
# Move to the right:
#   return {'ACTION': 'MOVE', 'WHERE': 1}
#
# Move to the left:
#   return {'ACTION': 'MOVE', 'WHERE': -1}
#
# Shooting projectile:
#   return {'ACTION': 'SHOOT', 'VEL': 100, 'ANGLE': 35}
#   # 'VEL' should be an integer > 0 and < 100
#   # 'ANGLE' should be an integer > 0 and < 90
#
#
# Do nothing:
#   return None

class Bot(object):

    def __init__(self):
        self.name = "pepe bot"

    def evaluate_turn(self, context_info):
        my_action = {"action": "move"}
        return "Executed: ", context_info