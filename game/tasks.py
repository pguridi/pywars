from __future__ import absolute_import

from celery import shared_task
from celery.exceptions import SoftTimeLimitExceeded

import time
import threading
from subprocess import Popen, PIPE
import signal
import subprocess
import tempfile
import os
import shutil
import json
import random


ENGINE_NAME = "ona_eng.py"

ENGINE_LOCATION = os.path.abspath(os.path.join("game_engine", ENGINE_NAME))
ENGINE_EXCEPS = os.path.abspath(os.path.join("game_engine", "exc.py"))

PYPYSANDBOX_EXE = os.path.join('/usr', 'bin', 'pypy-sandbox')
PYTHON_EXE = os.path.join('/usr', 'bin', 'python')

HARD_TIME_LIMIT = 20
SOFT_TIME_LIMIT = 15
GRID_LIMIT = 30


def run_popen_with_timeout(command_string, timeout, cwd):
    """
    Run a sub-program in subprocess.Popen, pass it the input_data,
    kill it if the specified timeout has passed.
    returns a tuple of success, stdout, stderr
    """
    kill_check = threading.Event()
    def _kill_process_after_a_timeout(pid):
        os.kill(pid, signal.SIGTERM)
        kill_check.set() # tell the main routine that we had to kill
        # use SIGKILL if hard to kill...
        return
    print "RUNNING: ", command_string
    p = Popen(command_string, bufsize=1, cwd=cwd,
              stdin=PIPE, stdout=PIPE, stderr=PIPE)
    pid = p.pid
    watchdog = threading.Timer(timeout, _kill_process_after_a_timeout, args=(pid, ))
    watchdog.start()
    (stdout, stderr) = p.communicate()
    watchdog.cancel() # if it's still waiting to run
    success = not kill_check.isSet()
    kill_check.clear()
    return (success, stdout, stderr)


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
            bot_code = players[player].replace('gc.', '')
            f.write(bot_code)

    start_time = time.time()
    # call the engine_match cli script
    if os.path.exists(PYPYSANDBOX_EXE):
        cmdargs = [PYPYSANDBOX_EXE, '--tmp={}'.format(match_dir), ENGINE_NAME]
    else:
        cmdargs = [PYTHON_EXE, ENGINE_NAME]

    cmdargs.extend(['bots/' + p + '.py' for p in players.keys()])
    randoms = [random.choice(range(GRID_LIMIT // 2)),
               random.choice(range(GRID_LIMIT // 2, GRID_LIMIT))]
    cmdargs.extend(map(str, randoms))
    #print 'CMDARGS: ', cmdargs
    success, stdo, stde = run_popen_with_timeout(cmdargs, HARD_TIME_LIMIT, match_dir)
    
    print "OUTPUT: ", stdo, stde
    challng.played = True
    challng.elapsed_time = time.time() - start_time
    
    if not success:
        # proc was killed by timeout
        print "KILLED BY TIMEOUT"
        challng.canceled = True
        challng.information = "Timeout"
        challng.save()
        return
        
    challng.canceled = False
    
    try:
        r = eval(stdo)  # Muy sucio.. pero es lo que hay.. :O
        LOSER = 'loser'
        WINNER = 'winner'
        DRAW = 'draw'
        result = r['actions'][-1]
        winner_username = result.get(WINNER)
        loser_username = result.get(LOSER)
        draw = result.get(DRAW, False)

        challng.result = json.dumps(r)

        if draw:
            challng.draw_player1 = challng.challenger_bot.owner
            challng.draw_player2 = challng.challenged_bot.owner
        else:
            winner = UserProfile.objects.get(user__username=winner_username)
            loser = UserProfile.objects.get(user__username=loser_username)
            challng.winner_player = winner
            challng.loser_player = loser
        challng.save()
    except Exception, e:
        challng.played = True
        challng.canceled = True
        challng.information = str(e)
        challng.save()
        raise e


def _validate_bot(bot_id, bot_code):
    """Returns a <bool> indicating if :bot_code: is valid or not.
    Modify Bot.valid according to the result.
    """
    from game.models import Bot
    bot = Bot.objects.get(pk=bot_id)

    # create temp dir and dump :bot_code: in a temp file
    match_dir = tempfile.mkdtemp()
    tmp_bot_filename = 'testing.py'
    with open(os.path.join(match_dir, tmp_bot_filename), 'w') as f:
        bot_code = bot_code.replace('gc.', '')
        f.write(bot_code)

    cmdargs = [PYTHON_EXE, '-m', 'py_compile', tmp_bot_filename]

    print "CMD: ", cmdargs
    proc = subprocess.Popen(cmdargs,
                            cwd=match_dir,
                            stdin=subprocess.PIPE,
                            stdout=subprocess.PIPE,
                            stderr=subprocess.PIPE, )
    stdout, stderr = proc.communicate()
    valid = proc.returncode == 0
    key = 'SyntaxError'
    invalid_reason = ''
    if not valid and key in (stderr or ''):
        i = stderr.index(key)
        invalid_reason = ', '.join(stderr[i:].splitlines()[-2:])
        invalid_reason = invalid_reason.replace(ENGINE_NAME, '*****')

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
        result = _validate_bot(bot_id, bot_code)
    except SoftTimeLimitExceeded:
        _bot_validation_time_outed(bot_id)
    else:
        return result


def _match_has_timeouted(challengue_id):
    from game.models import Challenge
    challng = Challenge.objects.get(pk=challengue_id)
    challng.elapsed_time = SOFT_TIME_LIMIT
    challng.played = True
    challng.canceled = True
    challng.information = "Timeout"
    challng.save()


@shared_task(time_limit=HARD_TIME_LIMIT, soft_time_limit=SOFT_TIME_LIMIT)
def run_match(challengue_id, players):
    from game.models import Challenge
    try:
        _run_match(challengue_id, players)
    except SoftTimeLimitExceeded:
        _match_has_timeouted(challengue_id)
    except Exception, e:
        challng = Challenge.objects.get(pk=challengue_id)
        challng.played = True
        challng.canceled = True
        challng.information = str(e)
        challng.save()
        raise e
