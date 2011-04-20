
import anime.user as userMethods

from django.contrib import auth
from django.http import HttpResponseRedirect
from django.core.cache import cache
from annoying.decorators import render_to
from anime.forms import UserCreationFormMail, UploadMalListForm
from anime.malconvert import passFile
from datetime import datetime

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
    lastLoad = cache.get('MalList:%s' % request.user.id)
    if request.method == 'POST':
        form = UploadMalListForm(request.POST, request.FILES)
        if form.is_valid():
            timeLeft = 0
            try:
                timeLeft = (18 - (datetime.now() - lastLoad['date']).seconds) / 60
            except TypeError:
                pass
            if lastLoad and timeLeft > 0:
                form.addError('You doing it too often. Try again in %s minutes.' % timeLeft)
            else:
                status, error = passFile(request.FILES['file'], request.user, form.cleaned_data['rewrite'])
                if status:
                    return HttpResponseRedirect('/settings/')
                else:
                    form.addError(error)
    else:
        form = UploadMalListForm()
    return {'mallistform': form, 'mallist': lastLoad}