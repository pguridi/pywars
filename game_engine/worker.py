from celery import Celery

app = Celery(broker='amqp://')

@app.task
def run_match(player_bots):
    # create the match temp dir

    # dump the bots file in bots dir

    # call the engine_match cli script

    # parse match results and update Django DB
    pass