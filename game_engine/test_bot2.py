class Bot(object):

    def __init__(self):
        self.name = "pepe bot"

    def evaluate_turn(self, distance, feedback, life):
        return {'ACTION': 'MOVE', 'WHERE': 1}
