from __future__ import absolute_import

from celery import shared_task
import time
import subprocess
import tempfile
import os
import shutil
import json

ENGINE_LOCATION = os.path.abspath(os.path.join("game_engine", "arena.py"))
ENGINE_EXCEPS = os.path.abspath(os.path.join("game_engine", "exc.py"))

PYPYSANDBOX_EXE = os.path.join('/usr', 'bin', 'pypy-sandbox')


@shared_task
def run_match(challengue_id, players):
    from game.models import Challenge
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
    cmdargs = [PYPYSANDBOX_EXE, '--tmp={}'.format(match_dir), 'arena.py']
    cmdargs.extend(['bots/' + p + '.py' for p in players.keys()])
    print 'CMDARGS: ', cmdargs
    proc = subprocess.Popen(cmdargs, cwd=match_dir, stdin=subprocess.PIPE, stdout=subprocess.PIPE)
    stdo, stde = proc.communicate()
    print stdo, stde
    challng.elapsed_time = time.time() - start_time

    challng.played = True

    # Muy sucio.. pero es lo que hay.. :O
    r = eval(stdo)
    challng.result = json.dumps(r)
    challng.save()


@shared_task
def validate_bot(bot_id, bot_code):
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

    cmdargs = [PYPYSANDBOX_EXE,
               '--tmp={}'.format(match_dir),
               'arena.py',
               tmp_bot_filename, tmp_bot_filename]
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
