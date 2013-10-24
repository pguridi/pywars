import json
import random
import logging

from django.conf import settings
from django.core.management.base import BaseCommand, CommandError
from django.db import transaction

from tournament.models import Challenge
from lightcycle.arena import LightCycleArena
from lightcycle.player import Player

logger = logging.getLogger(__name__)


class Command(BaseCommand):

    help = "Run queued matches."

    def handle(self, *args, **options):

      with transaction.commit_on_success():
        if len(args) > 0:
            raise CommandError('Too many arguments.')

        count = 0
        for count, challenge in enumerate(Challenge.objects.filter(played=False).order_by('creation_date'), 1):
            try:
                logger.info('Running Challenge "%s".' % challenge.pk)
                player1 = Player(name=challenge.challenger_bot.owner.user.username, bot=challenge.challenger_bot.code, bot_instance=challenge.challenger_bot)
                player2 = Player(name=challenge.challenged_bot.owner.user.username, bot=challenge.challenged_bot.code, bot_instance=challenge.challenged_bot)
                players = [player1, player2]
                random.shuffle(players)
                logger.info('Challenge "%s": "%s" vs "%s"' % (challenge.pk, players[0].username, players[1].username))
                arena = LightCycleArena(players, settings.ARENA_WIDTH, settings.ARENA_HEIGHT)
                result = arena.start()
                challenge.played = True
                challenge.result = json.dumps(result)
                if 'winner' in result['result']:
                    challenge.winner_bot = [player.bot_instance for player in players if player.username == result['result']['winner']][0]
                challenge.save()

                # Assign scores
                from tournament.score import calc_score
                challenger_score, challenged_score = calc_score(
                                    challenge.challenger_bot.owner.user,
                                    challenge.challenged_bot.owner.user,
                                     challenge.winner_bot and challenge.winner_bot.owner.user)
                challenge.challenger_bot.owner.score += challenger_score
                challenge.challenged_bot.owner.score += challenged_score
                challenge.challenger_bot.owner.save()
                challenge.challenged_bot.owner.save()
                logger.info('Challenge "%s" winner: %s' % (challenge.pk, challenge.winner_bot))

            except Exception as ex:
                msg = 'Error running Challenge "%s" ("%s")' % (challenge.pk, ex)
                logger.error(msg)
                raise CommandError(msg)
        print 'Finished running %d matches.' % count
        logger.info('Finished running %d matches.' % count)
