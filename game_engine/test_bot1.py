class Bot(object):

    def __init__(self):
        self.name = "pepe bot"

    def evaluate_turn(self, context_info):
        my_action = {"action": "move"}
        return "Executed: ", context_info