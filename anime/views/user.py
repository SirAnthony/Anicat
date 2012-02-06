
import anime.user as userMethods

from django.contrib import auth
from django.contrib.messages.api import get_messages
from django.http import HttpResponseRedirect
from annoying.decorators import render_to


@render_to('anime/user/login.html')
def login(request):
    res = userMethods.login(request)
    return HttpResponseRedirect('/') if 'response' in res else res


@render_to('anime/user/social-error.html')
def social_error(request):
    messages = get_messages(request)
    return {'messages': messages}


def logout(request):
    auth.logout(request)
    return HttpResponseRedirect('/')


@render_to('anime/user/register.html')
def register(request):
    res = userMethods.register(request)
    return HttpResponseRedirect('/') if 'response' in res else res


@render_to('anime/settings.html')
def settings(request):
    response = userMethods.load_settings(request)
    response.update(userMethods.getRequests(request.user))
    return response
