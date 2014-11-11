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
