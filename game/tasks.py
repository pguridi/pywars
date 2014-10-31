from __future__ import absolute_import

from celery import shared_task

@shared_task
def run_match(player_bots):
    # create the match temp dir

    # dump the bots file in bots dir

    # call the engine_match cli script

    # parse match results and update Django DB
    return