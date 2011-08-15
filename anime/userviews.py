
import anime.user as userMethods

from django.contrib import auth
from django.http import HttpResponseRedirect
from annoying.decorators import render_to
from anime.forms import UserCreationFormMail


@render_to('anime/login.html')
def login(request):
    res = userMethods.login(request)
    return HttpResponseRedirect('/') if res.has_key('response') else res

def logout(request):
    auth.logout(request)
    return HttpResponseRedirect("/")

@render_to('anime/register.html')
def register(request):
    res = userMethods.register(request)
    return HttpResponseRedirect('/') if res.has_key('response') else res

@render_to('anime/settings.html')
def settings(request):
    response = userMethods.loadMalList(request)
    try:
        if response['mallist']['updated']:
            return HttpResponseRedirect('/settings/')
    except:
        pass
    response.update(userMethods.getRequests(request.user))
    #many other things here later
    return response
