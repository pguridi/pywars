import json
from django.http import HttpResponse, JsonResponse
from django.shortcuts import render, redirect
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from django.contrib.auth.decorators import login_required
from django.views.decorators.cache import cache_page
from django.db.models import Q
from django.core import serializers
from django.core.exceptions import ObjectDoesNotExist
from .forms import BotBufferForm
from models import Challenge, Bot, UserProfile
from game.tasks import validate_bot


def index(request, match_id=None):
    return render(request, 'home.html', {'tab': 'arena', 'match_id': match_id})


def about(request):
    return render(request, 'about.html', {'tab': 'about'})


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

    pending_challenged_bots = [c.challenged_bot for c in challenges]

    played_challenges = Challenge.objects.filter(requested_by=request.user.profile, played=True)
    challenged_bots = [c.challenged_bot for c in played_challenges]

    return render(request, 'scoreboard.html', {'tab': 'score',
                'users': users,
                'challenged_bots': challenged_bots,
                'pending_challenged_bots': pending_challenged_bots})


@login_required
def tournament(request):
    users = UserProfile.objects.filter(current_bot__isnull=False).order_by('-score')

    return render(request, 'tournament.html', {'tab': 'tournament', 'users': users})


@login_required
def mybots(request):
    user_prof = UserProfile.objects.get(user=request.user)
    if request.method == 'POST':
        form = BotBufferForm(request.POST)
        if not form.is_valid():
            print "ERROR in form!"
            return
        new_code = form.cleaned_data['code']
        user_prof.code = new_code

        if 'publish_buffer' in request.POST:
            bot = Bot()
            bot.owner = user_prof
            bot.code = new_code
            bot.save()
            validate_bot.delay(bot.id, new_code)
            user_prof.current_bot = bot

        user_prof.save()
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
        #played_challs = Challenge.objects.filter(challenger_bot=user_prof.current_bot,
        #    challenged_bot=challenge_bot, played=True)

        #if played_challs.count() > 0:
        #    # has already played against this bot, must upload a new one
        #    return HttpResponse("Already played against this bot!. Upload a new one.")
        if (user_prof.current_bot.valid != Bot.READY
                or challenge_bot.valid != Bot.READY):
            return JsonResponse({'success': False, 'msg': 'One of the bot is not READY' })

        new_challengue = Challenge()
        new_challengue.requested_by = user_prof
        new_challengue.challenger_bot = user_prof.current_bot
        new_challengue.challenged_bot = challenge_bot
        new_challengue.save()

        return JsonResponse({'success': True})


@login_required
@cache_page(60)
def main_match(request):
    return HttpResponse(None)


@login_required
def my_matches(request):
    matches = Challenge.objects.filter(Q(challenger_bot__owner=request.user) | Q(challenged_bot__owner=request.user)).order_by('-creation_date').select_related('challenger_bot__owner__user', 'challenged_bot__owner__user', 'winner_bot__owner__user')
    return render(request, 'mymatches.html', {'matches': matches, 'tab': 'my-matches'})


@login_required
def get_match(request, match_id):
    try:
        challenge = Challenge.objects.get(pk=match_id)
        return JsonResponse({'success': True, 'data': json.loads(challenge.result)})
    except ObjectDoesNotExist:
        return JsonResponse({'success': False})

@login_required
def get_bot_status(request, bot_id):
    try:
        bot = Bot.objects.get(pk=bot_id)
        return JsonResponse({'success': True, 'status': bot.valid, 'code': bot.code ,'reason': bot.invalid_reason})
    except ObjectDoesNotExist:
        return JsonResponse({'success': False})


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


@login_required
def get_playlist(request):
    challenges = Challenge.objects.filter(played=True)[:25]
    if not challenges:
        return JsonResponse({'success': False, 'data': []})
    data = json.loads(serializers.serialize('json', challenges))
    for d in data:
        del d['fields']['result']
    return JsonResponse({'success': True, 'data': data})
