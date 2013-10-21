from django.http import HttpResponse
from django.shortcuts import render, get_object_or_404

def index(request):
    return render(request, 'home.html', {})

def scoreboard(request):
    return render(request, 'scoreboard.html', {})

def upload(request):
    return render(request, 'upload.html', {})

def about(request):
    return render(request, 'about.html', {})