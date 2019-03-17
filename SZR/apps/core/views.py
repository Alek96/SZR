from django.http import HttpResponseRedirect
from django.urls import reverse


def login_gitlab(request):
    return HttpResponseRedirect(reverse('social:begin', args=('gitlab',)))
