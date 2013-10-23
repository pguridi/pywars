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

    challenged_bots = [ c.challenged_bot for c in challenges ]

    return render(request, 'scoreboard.html', { 'tab' : 'score',
                'bots' : bots,
                'pending_challenges' : pending_challenges,
                'challenged_bots' : challenged_bots})

@login_required
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
        code_content = json.loads(request.body)['msg']
#        if len(code_content.strip('')) == 0:
#            return HttpResponse("Can not save an empty bot")

        user_prof = UserProfile.objects.get(user=request.user)
        user_prof.my_buffer = code_content
        user_prof.save()
    return HttpResponse(json.dumps({'success' : True}), 
        mimetype='application/json')

@login_required
@csrf_exempt
@require_POST
def publish_bot(request):
    if request.is_ajax():
        user_prof = UserProfile.objects.get(user=request.user)
        new_bot_code = json.loads(request.body)['msg']
        
        if len(new_bot_code.strip('')) == 0:
            return HttpResponse("Can not publish an empty bot")
        

        # Get the last bot, and check delta
        try:
            latest_bot = Bot.objects.filter(owner=user_prof).latest('creation_date')
            if compare_bots(latest_bot.code, new_bot_code):
                error = "Can not publish this bot, looks like the previous one!"
                return HttpResponse(error)

        except ObjectDoesNotExist:
            # This is the first bot for this user
            pass

        bot = Bot()
        bot.owner = user_prof
        bot.code = new_bot_code
        bot.save()
        user_prof.current_bot = bot
        user_prof.save()
    return HttpResponse(json.dumps({'success' : True}), 
        mimetype='application/json')

@login_required
@csrf_exempt
@require_POST
def challenge(request):
    if request.is_ajax():
        challenge_bot_id = json.loads(request.body)['msg']
        challenge_bot = Bot.objects.get(pk=challenge_bot_id)    
        
        # get the user current bot
        user_prof = UserProfile.objects.get(user=request.user)
        if challenge_bot.owner == user_prof:
            print "[CHEATING!] - wrong challenge bot!"
            return HttpResponse("Error")

        print "Got a challenge for bot: ", challenge_bot        
        challenges = Challenge.objects.filter(requested_by=user_prof, played=False)
        if challenges.count() > 0:
            # has pending challenges, must wait.
            return HttpResponse("Can not challenge more than one bot at a time")

        
        new_chall = Challenge()
        new_chall.requested_by = user_prof
        new_chall.challenger_bot = user_prof.current_bot
        new_chall.challenged_bot = challenge_bot
        new_chall.save()
        
        return HttpResponse(json.dumps({'success' : True}), 
        mimetype='application/json')
