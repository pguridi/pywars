import json

from django.http import HttpResponse
from django.shortcuts import render
from django.utils.html import escape
from django.core.exceptions import ObjectDoesNotExist
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404
from django.views.decorators.cache import cache_page
from django.db.models import Q

from tournament.tools import compare_bots
from lightcycle.arena import LightCycleArena
from lightcycle.basebot import LightCycleRandomBot
from lightcycle.player import Player


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

    return render(request, 'my_bots.html',
        {'tab' : 'mybots',
         'my_buffer' : user_prof.my_buffer,
         'my_bots' : reversed(Bot.objects.filter(owner=user_prof))})

@login_required
@csrf_exempt
@require_POST
def save_buffer(request):
    if request.is_ajax():
        code_content = json.loads(request.body)['msg']
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
        user_prof.my_buffer = new_bot_code
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
        if not user_prof.current_bot:
            print "Can not challenge if does not have a bot!"
            return HttpResponse("Error")
        if challenge_bot.owner == user_prof:
            print "[CHEATING!] - wrong challenge bot!"
            return HttpResponse("Error")

        # challenged bot must be the owners current bot
        if not challenge_bot.is_current_bot:
            print "[CHEATING!] - wrong challenge bot!, must be the owners current bot!."
            return HttpResponse("Error")

        print "Got a challenge for bot: ", challenge_bot

        # Get pending challenges for this user
        challenges = Challenge.objects.filter(requested_by=user_prof, played=False)
        if challenges.count() > 0:
            # has pending challenges, must wait.
            return HttpResponse("Can not challenge more than one bot at a time")

        # Check if these bots haven't already played.
        played_challs = Challenge.objects.filter(challenger_bot=user_prof.current_bot,
            challenged_bot=challenge_bot, played=True)

        if played_challs.count() > 0:
            # has already played against this bot, must upload a new one
            return HttpResponse("Already played against this bot!. Upload a new one.")

        new_chall = Challenge()
        new_chall.requested_by = user_prof
        new_chall.challenger_bot = user_prof.current_bot
        new_chall.challenged_bot = challenge_bot
        new_chall.save()

        return HttpResponse(json.dumps({'success' : True}), mimetype='application/json')

@login_required
@cache_page(60)
def main_match(request):
    list_match = Challenge.objects.filter(played=True).order_by('-creation_date')[:50]
    res = [{'id': match.id,
            'player1': escape(match.challenger_bot.owner.user.username),
            'player2': escape(match.challenged_bot.owner.user.username),
            'title': escape(match.result_description()),
            'duration': match.duration(),
            'moves': match.move_count(),
           } for match in list_match]
    data = json.dumps(res)
    return HttpResponse(data, mimetype='application/json')

@login_required
def my_matches(request):
    matches = Challenge.objects.filter(Q(challenger_bot__owner=request.user) | Q(challenged_bot__owner=request.user)).order_by('-creation_date').select_related('challenger_bot__owner__user', 'challenged_bot__owner__user', 'winner_bot__owner__user')
    return render(request, 'mymatches.html', {'matches': matches})

@login_required
def get_match(request, match_id):
    match = get_object_or_404(Challenge, id=match_id)
    return HttpResponse(match.result, mimetype='application/json')

@login_required
def random_test_match(request):
    player1 = Player('Player 1', LightCycleRandomBot)
    player2 = Player('Player 2', LightCycleRandomBot)
    width = 50
    height = 50
    match = LightCycleArena((player1, player2), width, height).start()
    return HttpResponse( json.dumps(match) , mimetype='application/javascript')

@login_required
def bot_code(request, bot_pk):
    if bot_pk == "0":
        user_prof = UserProfile.objects.get(user=request.user)
        return HttpResponse(user_prof.my_buffer)

    bot_code = Bot.objects.get(pk=bot_pk, owner=request.user).code
    return HttpResponse(bot_code)
