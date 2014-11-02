# encoding=utf-8

class Player(object):
    '''A basic player with a name and a Bot.
    bot may be a subclass of LightCycleBaseBot or a string with its Python
    source code.
    '''
    def __init__(self, name, bot, **kwargs):
        for attr, value in kwargs.items():
            if not hasattr(self, attr):
                setattr(self, attr, value)
        self.username = name
        self.bot = bot  # LightCycleBaseBot subclass or source code string
        self.x_factor = None

    def assign_team(self, x_factor):
        """Depending on which part of the field, the player is assigned, it
        requires a factor to modify the <x> coordinates.
        x_factor -> 1 | -1"""
        self.x_factor = x_factor
        return
