from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse


def home(request):
    return render(request, 'core/home.html')


def login_gitlab(request):
    return HttpResponseRedirect(reverse('social:begin', args=('gitlab',)))
