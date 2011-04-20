
import anime.user as userMethods

from django.contrib import auth
from django.http import HttpResponseRedirect
from annoying.decorators import render_to
from anime.forms import UserCreationFormMail


@render_to('anime/login.html')
def login(request):
    res = userMethods.login(request)
    if res.has_key('response') and res['response']: #logged
        return HttpResponseRedirect("/")
    else:
        return res

def logout(request):
    auth.logout(request)
    return HttpResponseRedirect("/")

@render_to('anime/register.html')
def register(request):
    if not request.user.is_authenticated() and request.method == 'POST':
        form = UserCreationFormMail(request.POST)
        if form.is_valid():
            user = form.save()
            user = auth.authenticate(username=user.username, password=form.cleaned_data['password1'])
            auth.login(request, user)
            return HttpResponseRedirect("/")
    else:
        form = UserCreationFormMail()
    return {'form': form}

@render_to('anime/settings.html')
def settings(request):
    mallist = userMethods.loadMalList(request)
    try:
        if mallist['mallist']['updated']:
            return HttpResponseRedirect('/settings/')
    except:
        pass
    return mallist