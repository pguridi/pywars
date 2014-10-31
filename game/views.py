import json

from django.http import HttpResponse, JsonResponse
from django.shortcuts import render, redirect
from django.utils.html import escape
from django.core.exceptions import ObjectDoesNotExist
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404
from django.views.decorators.cache import cache_page
from django.db.models import Q

from .forms import BotBufferForm
#from tournament.tools import compare_bots
#from game_engine.arena import LightCycleArena
#from game_engine.basebot import LightCycleRandomBot
#from game_engine.player import Player


from models import Challenge, Bot, UserProfile


def index(request, match_id=None):
    return render(request, 'home.html', {'tab' : 'arena', 'match_id': match_id})

def about(request):
    return render(request, 'about.html', {'tab' : 'about'})


@login_required
def scoreboard(request):
    #bots = Bot.objects.all().order_by('-points')
    users = UserProfile.objects.filter(current_bot__isnull=False).order_by('-score')
    users = ((user, request.user.profile.latest_match_id(user)) for user in users)
    challenges = Challenge.objects.filter(requested_by=request.user.profile, challenger_bot=request.user.profile.current_bot, played=False)
#    if challenges.count() > 0:
#        pending_challenges = True
#    else:
#        pending_challenges = False

    pending_challenged_bots = [ c.challenged_bot for c in challenges ]

    played_challenges = Challenge.objects.filter(requested_by=request.user.profile, played=True)
    challenged_bots = [ c.challenged_bot for c in played_challenges ]

    return render(request, 'scoreboard.html', { 'tab' : 'score',
                'users' : users,
                'challenged_bots' : challenged_bots,
                'pending_challenged_bots' : pending_challenged_bots})

@login_required
def mybots(request):
    user_prof = UserProfile.objects.get(user=request.user)
    if request.method == 'POST':
        form = BotBufferForm(request.POST)
        if not form.is_valid():
            print "ERROR in form!"
        new_code = form.cleaned_data['code']
        user_prof.code = new_code
        user_prof.save()

        if 'publish_buffer' in request.POST:
            bot = Bot()
            bot.owner = user_prof
            bot.code = new_code
            bot.save()
        return redirect('/mybots')
    else:
        form = BotBufferForm(instance=user_prof)

    return render(request, "my_bots.html", {
        'form': form,
        'user_prof': user_prof,
        'tab': 'mybots',
        'my_bots': reversed(Bot.objects.filter(owner=user_prof))
    })


@login_required
@csrf_exempt
@require_POST
def challenge(request):
    return HttpResponse(None)

@login_required
@cache_page(60)
def main_match(request):
    return HttpResponse(None)

@login_required
def my_matches(request):
    matches = Challenge.objects.filter(Q(challenger_bot__owner=request.user) | Q(challenged_bot__owner=request.user)).order_by('-creation_date').select_related('challenger_bot__owner__user', 'challenged_bot__owner__user', 'winner_bot__owner__user')
    return render(request, 'mymatches.html', {'matches': matches})

@login_required
def get_match(request, match_id):
    return HttpResponse(None)

@login_required
def random_test_match(request):
    return HttpResponse(None)

@login_required
def bot_code(request, bot_pk):
    if bot_pk == "0":
        user_prof = UserProfile.objects.get(user=request.user)
        return HttpResponse(user_prof.my_buffer)

    bot_code = Bot.objects.get(pk=bot_pk, owner=request.user).code
    return HttpResponse(bot_code)