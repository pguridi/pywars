from __future__ import absolute_import

from celery import shared_task
from celery.exceptions import SoftTimeLimitExceeded
import time
import subprocess
import tempfile
import os
import shutil
import json



ENGINE_LOCATION = os.path.abspath(os.path.join("game_engine", "arena.py"))
ENGINE_EXCEPS = os.path.abspath(os.path.join("game_engine", "exc.py"))

PYPYSANDBOX_EXE = os.path.join('/usr', 'bin', 'pypy-sandbox')
PYTHON_EXE = os.path.join('/usr', 'bin', 'python')

HARD_TIME_LIMIT = 40
SOFT_TIME_LIMIT = 30


def _run_match(challengue_id, players):
    from game.models import Challenge, UserProfile
    challng = Challenge.objects.get(pk=challengue_id)

    # create the match temp dir
    match_dir = tempfile.mkdtemp()
    bots_dir = os.path.join(match_dir, 'bots')
    os.mkdir(bots_dir)
    with open(os.path.join(bots_dir, "__init__.py"), 'w') as f:
        f.write('')

    print "MATCH DIR: ", match_dir

    # dump the engine and bots file in temp dir
    shutil.copy2(ENGINE_LOCATION, match_dir)
    shutil.copy2(ENGINE_EXCEPS, match_dir)

    for player in players.keys():
        with open(os.path.join(bots_dir, player + '.py'), 'w') as f:
            f.write(players[player])

    start_time = time.time()
    # call the engine_match cli script

    if os.path.exists(PYPYSANDBOX_EXE):
        cmdargs = [PYPYSANDBOX_EXE, '--tmp={}'.format(match_dir), 'arena.py']
    else:
        cmdargs = [PYTHON_EXE, 'arena.py']

    cmdargs.extend(['bots/' + p + '.py' for p in players.keys()])
    print 'CMDARGS: ', cmdargs
    proc = subprocess.Popen(cmdargs, cwd=match_dir, stdin=subprocess.PIPE, stdout=subprocess.PIPE)
    stdo, stde = proc.communicate()
    print stdo, stde
    challng.elapsed_time = time.time() - start_time

    challng.played = True
    challng.canceled = False

    try:
        r = eval(stdo) # Muy sucio.. pero es lo que hay.. :O
        LOSER = 'loser'
        WINNER = 'winner'
        DRAW = 'draw'
        RESULT = 'result'
        ACTION = 'action'
        result = r['actions'][-1]
        winner_username = result.get(WINNER)
        loser_username = result.get(WINNER)
        draw = result.get(DRAW, False)

        challng.result = json.dumps(r)
        if draw:
            challng.draw_player1 = challng.challenger_bot.owner
            challng.draw_player2 = challng.challenged_bot.owner
        else:
            winner = UserProfile.objects.get(user__username=winner_username)
            loser = UserProfile.objects.get(user__username=loser_username)
            challng.winner_player = winner_username
            challng.loser_player = loser_player
    except Exception:
        challng.played = True
        challng.canceled = True
        challng.save()

def _validate_bot(bot_id, bot_code):
    from game.models import Bot
    bot = Bot.objects.get(pk=bot_id)

    # create temp dir and dump :bot_code: in a temp file
    match_dir = tempfile.mkdtemp()
    bots_dir = os.path.join(match_dir, 'bots')
    os.mkdir(bots_dir)
    tmp_bot_filename = 'testing.py'
    with open(os.path.join(match_dir, tmp_bot_filename), 'w') as f:
        f.write(bot_code)

    # dump the engine and bots file in temp dir
    shutil.copy2(ENGINE_LOCATION, match_dir)
    shutil.copy2(ENGINE_EXCEPS, match_dir)

    if os.path.exists(PYPYSANDBOX_EXE):
        cmdargs = [PYPYSANDBOX_EXE, '--tmp={}'.format(match_dir), 'arena.py']
    else:
        cmdargs = [PYTHON_EXE, 'arena.py']

    cmdargs.extend([tmp_bot_filename, tmp_bot_filename])

    print "CMD: ", cmdargs
    proc = subprocess.Popen(cmdargs,
                            cwd=match_dir,
                            stdin=subprocess.PIPE,
                            stdout=subprocess.PIPE,
                            stderr=subprocess.PIPE, )
    stdout, stderr = proc.communicate()
    valid = True
    key = 'Traceback'
    invalid_reason = ''
    if stderr:
        if key in stderr:
            valid = False
            i = stderr.index(key)
            invalid_reason = stderr[i:]

    bot.valid = Bot.READY if valid else Bot.INVALID
    bot.invalid_reason = invalid_reason
    bot.save()
    return valid


def _bot_validation_time_outed(bot_id):
    from game.models import Bot
    bot = Bot.objects.get(pk=bot_id)
    bot.valid = Bot.INVALID
    bot.invalid_reason = "Bot code timeouts"
    bot.save()
    return False


@shared_task(time_limit=HARD_TIME_LIMIT, soft_time_limit=SOFT_TIME_LIMIT)
def validate_bot(bot_id, bot_code):
    try:
        _validate_bot(bot_id, bot_code)
    except SoftTimeLimitExceeded:
        _bot_validation_time_outed(bot_id)


def _match_has_timeouted(challengue_id):
    from game.models import Challenge
    challng = Challenge.objects.get(pk=challengue_id)
    challng.elapsed_time = SOFT_TIME_LIMIT
    challng.played = True
    challng.canceled = True
    challng.save()


@shared_task(time_limit=HARD_TIME_LIMIT, soft_time_limit=SOFT_TIME_LIMIT)
def run_match(challengue_id, players):
    from game.models import Challenge
    try:
        _run_match(challengue_id, players)
    except SoftTimeLimitExceeded:
        _match_has_timeouted(challengue_id)
    except Exception as e:
        challng = Challenge.objects.get(pk=challengue_id)
        challng.played = True
        challng.canceled = True
        challng.save()

