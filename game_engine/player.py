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
