class InvalidBotOutput(Exception):
    reason = u'Invalid output'
    pass


class BotTimeoutException(Exception):
    reason = u'Timeout'
    pass


class MissedTargetException(Exception):
    pass


class TankDestroyedException(Exception):
    reason = u'Tank Destroyed'
    pass


class GameOverException(Exception):
    pass
