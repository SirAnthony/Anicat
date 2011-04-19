
from django.contrib import auth
from django.http import HttpResponseRedirect
from django.core.cache import cache
from annoying.decorators import render_to
from anime.forms import UserCreationFormMail, UploadFileForm
from anime.malconvert import passFile
from datetime import datetime

#FIXME: Do normal page if fail
def login(request):
    response = {}
    if request.method != 'POST':
        response['text'] = 'Only POST method allowed.'
    elif request.user.is_authenticated():
        response['text'] = 'Already logined.'
    else:
        username = request.POST.get('name', None)
        password = request.POST.get('pass', None)
        user = auth.authenticate(username=username, password=password)
        if user is not None and user.is_active:
            auth.login(request, user)
            response.update({'response': 'logok', 'text': {'name': user.username}})
        else:
            response.update({'response': 'logfail', 'text': 'Bad username or password'})
    return HttpResponseRedirect("/")

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
        form = UploadFileForm(request.POST, request.FILES)
        if form.is_valid():
            timeLeft = 0
            try:
                timeLeft = (18 - (datetime.now() - lastLoad['date']).seconds) / 60
            except TypeError:
                pass
            if lastLoad and timeLeft > 0:
                form.addError('You doing it too often. Try again in %s minutes.' % timeLeft)
            else:
                status, error = passFile(request.FILES['file'], request.user)
                if status:
                    return HttpResponseRedirect('/settings/')
                else:
                    form.addError(error)
    else:
        form = UploadFileForm()
    return {'mallistform': form, 'mallist': lastLoad}