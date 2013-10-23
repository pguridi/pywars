from django.http import HttpResponse
from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse
from django.core.exceptions import ObjectDoesNotExist
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from django.core import serializers
from django.contrib.auth.decorators import login_required
import json

from models import *
from tournament.tools import *


def index(request):
    return render(request, 'home.html', {'tab' : 'arena'})

def about(request):
    return render(request, 'about.html', {'tab' : 'about'})


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

def mybots(request):
#    try:
    # get the profile for this guy
    user_prof = UserProfile.objects.get(user=request.user)
#    except ObjectDoesNotExist:
#        print "creating first bot for user"
#        bot = Bot()
#        bot.owner = UserProfile.objects.get(user=request.user)
#        bot.code = open('tournament/base_bot.py', 'r').read()
#        bot.save()
    return render(request, 'my_bots.html', 
        {'tab' : 'mybots',
         'my_buffer' : user_prof.my_buffer,
         'my_bots' : Bot.objects.filter(owner=user_prof)})

@login_required
@csrf_exempt
@require_POST
def save_buffer(request):
    if request.is_ajax():
        user_prof = UserProfile.objects.get(user=request.user)
        user_prof.my_buffer = json.loads(request.body)['code']
        user_prof.save()
    return HttpResponse(json.dumps({'success' : True}), 
        mimetype='application/json')



@login_required
@csrf_exempt
@require_POST
def publish_bot(request):
    if request.is_ajax():
        user_prof = UserProfile.objects.get(user=request.user)
        new_bot_code = json.loads(request.body)['code']

        # Get the last bot, and check delta
        try:
            latest_bot = Bot.objects.filter(owner=user_prof).latest('creation_date')
            if compare_bots(latest_bot.code, new_bot_code):
                print "can not add this bot, looks the same as previous one!"
                return HttpResponse("Bad bot")

        except ObjectDoesNotExist:
            # This is the first bot for this user
            pass

        bot = Bot()
        bot.owner = user_prof
        bot.code = new_bot_code

        bot.save()
    return HttpResponse(json.dumps({'success' : True}), 
        mimetype='application/json')
