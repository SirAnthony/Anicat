
from django.contrib import auth
from django.contrib.auth.forms import AuthenticationForm
from django.core.cache import cache
from anime.forms import UploadMalListForm, UserCreationFormMail
from anime.malconvert import passFile
from datetime import datetime

def login(request):
    response = {}
    form = None
    if request.method != 'POST':
        response['text'] = 'Only POST method allowed.'
    elif request.user.is_authenticated():
        response['text'] = 'Already logged in.'
    else:
        form = AuthenticationForm(data=request.POST)
        if form.is_valid():
            user = form.get_user()
            auth.login(request, user)
            response.update({'response': True, 'text': {'name': user.username}})
    response['form'] = form or AuthenticationForm()
    return response

def register(request):
    response = {}
    form = None
    if request.method != 'POST':
        response['text'] = 'Only POST method allowed.'
    elif request.user.is_authenticated():
        response['text'] = 'Already registred.'
    else:
        form = UserCreationFormMail(request.POST)
        if form.is_valid():        
            user = form.save()
            user = auth.authenticate(username=user.username, password=form.cleaned_data['password1'])
            auth.login(request, user)
            response.update({'response': True, 'text': {'name': user.username}})
    response['form'] = form or UserCreationFormMail()
    return response

def loadMalList(request):
    lastLoad = cache.get('MalList:%s' % request.user.id)
    if request.method == 'POST':
        form = UploadMalListForm(request.POST, request.FILES)
        if form.is_valid():
            timeLeft = 0
            try:
                timeLeft = (18 - (datetime.now() - lastLoad['date']).seconds) / 60
            except TypeError:
                lastLoad = {}
                pass
            if lastLoad and timeLeft > 0:
                form.addError('You doing it too often. Try again in %s minutes.' % timeLeft)
            else:
                status, error = passFile(request.FILES['file'], request.user, form.cleaned_data['rewrite'])
                if not status:
                    form.addError(error)
                else:
                    lastLoad['updated'] = True
    else:
        form = UploadMalListForm()
    return {'mallistform': form, 'mallist': lastLoad}
