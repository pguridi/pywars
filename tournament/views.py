from django.http import HttpResponse
from django.shortcuts import render
from django.http import HttpResponse
from django.core.exceptions import ObjectDoesNotExist
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from django.core import serializers
from django.contrib.auth.decorators import login_required
import json

from lightcycle.arena import LightCycleArena
from lightcycle.basebot import LightCycleBaseBot, LightCycleRandomBot
from lightcycle.player import Player


from models import Challenge, Bot

def index(request):
    return render(request, 'home.html', {'tab' : 'arena'})

@login_required
def scoreboard(request):
    bots = Bot.objects.all().order_by('-points')
    challenges = Challenge.objects.filter(requested_by=request.user, played=False)
    if challenges.count() > 0:
        pending_challenges = True
    else:
        pending_challenges = False
    return render(request, 'scoreboard.html', { 'tab' : 'score',
                'bots' : bots,
                'pending_challenges' : pending_challenges})

@login_required
def upload(request):
    try:
        # get the bot for this guy
        bot = Bot.objects.get(owner=request.user)
    except ObjectDoesNotExist:
        print "creating first bot for user"
        bot = Bot()
        bot.owner = request.user
        bot.code = open('tournament/base_bot.py', 'r').read()
        bot.save()
    return render(request, 'upload.html',
        {'tab' : 'upload',
         'bot' : bot})

def about(request):
    return render(request, 'about.html', {'tab' : 'about'})

@login_required
@csrf_exempt
@require_POST
def update_bot(request):
    if request.is_ajax():
        try:
            bot = Bot.objects.get(owner=request.user)
            print "data: ", json.loads(request.body)
        except ObjectDoesNotExist:
            print "creating first bot for user"
            bot = Bot()
            bot.owner = request.user
        bot.code = json.loads(request.body)['code']
        bot.save()
    return HttpResponse('/about')

@login_required
def main_match(request):
    player1 = Player('Player 1', LightCycleRandomBot)
    player2 = Player('Player 2', LightCycleRandomBot)
    width = 50
    height = 50
    match = LightCycleArena((player1, player2), width, height).start()
    return HttpResponse( json.dumps(match) , mimetype='application/javascript')
