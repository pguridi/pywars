# encoding=utf-8
import unittest
import json
from django.contrib.auth.models import User
from django.db import IntegrityError
from django.test.utils import override_settings
import game_engine.arena
from game.tasks import run_match
from game.models import Challenge
from game.models import Bot
from game.models import UserProfile
from game import admin


#class Bot(object):
#    def evaluate_turn(self, feedback, life):
#        return None

NULL_BOT_CODE = '''
class Bot(object):
    def evaluate_turn(self, feedback, life):
        return None
'''

SLOW_BOT_CODE = '''
class Bot(object):
    def evaluate_turn(self, feedback, life):
        LARGE_NUMBER = 100000
        for _ in xrange(LARGE_NUMBER):
            for __ in xrange(LARGE_NUMBER):
                for ___ in xrange(LARGE_NUMBER):
                    x = 5
                    x += 100
        return None
'''

USER1_NAME = 'Magnus Carlsen'
USER2_NAME = 'Vishy Anand'

def get_or_create_user(username, email, password):
    try:
        new_user = User.objects.create_user(username, email, password)
        return new_user
    except IntegrityError:
        return User.objects.get(username=username, email=email)

def get_or_create_user_profile(aUser):
    try:
        new_profile = UserProfile.objects.create(user=aUser)
        return new_profile
    except IntegrityError:
        return UserProfile.objects.get(user=aUser)

class TasksProgramTestCase(unittest.TestCase):

    def setUp(self):
        unittest.TestCase.setUp(self)
        # Initial settings
        self.user1 = get_or_create_user(USER1_NAME, 'user1@user1.com', 'user1pass')
        self.user1_profile = get_or_create_user_profile(self.user1)
        self.user2 = get_or_create_user(USER2_NAME, 'user2@user2.com', 'user2pass')
        self.user2_profile = get_or_create_user_profile(self.user2)

    def tearDown(self):
        # Final cleaning
        #TODO GERVA: remove users
        unittest.TestCase.tearDown(self)

    @override_settings(CELERY_EAGER_PROPAGATES_EXCEPTIONS=True,
                       CELERY_ALWAYS_EAGER=True,
                       BROKER_BACKEND='memory')
    #Test is breaking
    #FIXME: at least in "testing mode", time_limits are being ingored
    #TODO: Mock post_save.connect to do nothing
    def FIXME_test_slow_bot_cancels(self):
        def check_is_canceled(aChallenge):
            #No result necessary for canceled
            self.assertFalse(aChallenge.result)
            self.assertEqual(aChallenge.canceled, True)

        self._test_run_match(SLOW_BOT_CODE, NULL_BOT_CODE, check_is_canceled)

    @override_settings(CELERY_EAGER_PROPAGATES_EXCEPTIONS=True,
                       CELERY_ALWAYS_EAGER=True,
                       BROKER_BACKEND='memory')
    def test_null_bot_draws(self):
        def check_is_draw(aChallenge):
            result_dict = json.loads(aChallenge.result)
            match_result_dict = result_dict['actions'][-1]
            self.assertEqual(match_result_dict[game_engine.arena.ACTION], game_engine.arena.RESULT)
            self.assertIsNone(match_result_dict[game_engine.arena.WINNER])
            self.assertIsNone(match_result_dict[game_engine.arena.LOSER])
            self.assertTrue(match_result_dict[game_engine.arena.DRAW])
            #If drawn -> not canceled
            self.assertEqual(aChallenge.canceled, False)

        self._test_run_match(NULL_BOT_CODE, NULL_BOT_CODE, check_is_draw)

    def _test_run_match(self, bot1_code, bot2_code, checkChallenge):
        def save_bot(user_profile, bot_code):
            aBot = Bot()
            aBot.owner = user_profile
            aBot.code = bot_code
            aBot.save()
            return aBot

        bot1 = save_bot(self.user1_profile, bot1_code)
        bot2 = save_bot(self.user2_profile, bot2_code)

        aChallenge = Challenge()
        aChallenge.challenger_bot = bot1
        aChallenge.challenged_bot = bot2
        aChallenge.requested_by = self.user1_profile
        aChallenge.save()

        players = {'bot1': aChallenge.challenger_bot.code,
                   'bot2': aChallenge.challenged_bot.code}

        run_match.delay(aChallenge.id, players)

        #Refresh challenge
        aChallenge = Challenge.objects.get(pk=aChallenge.id)
        checkChallenge(aChallenge)

if __name__ == '__main__':
    unittest.main()
