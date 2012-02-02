
from django.conf import settings
from django.contrib import auth
from django.core.cache import cache
from django.db.models import Q
from anime.forms.Error import UploadMalListForm
from anime.forms.User import ( UserNamesForm, UserEmailForm,
        UserCreationFormMail, NotActiveAuthenticationForm, )
from anime.malconvert import passFile
from anime.models import AnimeRequest
from datetime import datetime, timedelta

def get_username(user):
    username = 'Anonymous'
    if user and user.first_name:
        username = user.first_name
        if user.last_name:
            username += u' ' + user.last_name
    return username

def login(request):
    response = {}
    form = None
    if request.method != 'POST':
        response['text'] = 'Only POST method allowed.'
    elif request.user.is_authenticated():
        response['text'] = 'Already logged in.'
    else:
        form = NotActiveAuthenticationForm(data=request.POST)
        if form.is_valid():
            user = form.get_user()
            auth.login(request, user)
            response.update({'response': True,
                'text': {'name': get_username(user)}})
    response['form'] = form or NotActiveAuthenticationForm()
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
            response.update({'response': True, 'text': {'name': get_username(user)}})
    response['form'] = form or UserCreationFormMail()
    return response


def set_usernames(request):
    response = {}
    form = UserNamesForm(request.POST or None)
    if form.is_valid():
        form.save()
        response.update({'response': True, 'text': {'name': get_username(user)}})


def load_settings(request):
    res = {}
    if 'mallist' in request.POST:
        res.update(loadMalList(request))
    else:
        res['mallistform'] = UploadMalListForm()
    if 'usernames' in request.POST:
        res['usernames'] = form = UserNamesForm(request.POST or None, instance=request.user)
        if form.is_valid():
            form.save()
    else:
        res['usernames'] = UserNamesForm(instance=request.user)
    if 'emailform' in request.POST:
        res['emailForm'] = form = UserEmailForm(request.POST or None, instance=request.user)
        if form.is_valid():
            form.save()
    else:
        res['emailForm'] = UserEmailForm(instance=request.user)
    return res


def loadMalList(request):
    lastLoad = cache.get('MalList:%s' % request.user.id)
    form = UploadMalListForm(request.POST or None, request.FILES)
    if form.is_valid():
        timeLeft = 0
        try:
            timeLeft = (1800 - (datetime.now() - lastLoad['date']).seconds) / 60
        except TypeError:
            lastLoad = {}
        if lastLoad and timeLeft > 0:
            form.addError('You doing it too often. Try again in %s minutes.' % timeLeft)
        else:
            status, error = passFile(request.FILES['file'],
                    request.user, form.cleaned_data['rewrite'])
            if not status:
                form.addError(error)
            else:
                lastLoad['updated'] = True
    return {'mallistform': form, 'mallist': lastLoad}


def getRequests(user, *keys):
    try:
        qs = AnimeRequest.objects.filter(user=user).order_by('status', '-id')
        qs = qs.exclude(Q(status__gt=2) & Q(changed__lte=datetime.now() - timedelta(days=20)))
        c = qs.filter(status__gt=2).count()
        if c > settings.USER_PAGE_REQUEST_COUNT:
            qs = qs[:qs.count() - (c - settings.USER_PAGE_REQUEST_COUNT/2)]
        if keys:
            qs = qs.values(*keys)
        try:
            types = AnimeRequest._meta.get_field('requestType').choices
        except:
            types = None
        return {'requests': list(qs),
                'requestTypes': types}
    except:
        return {}
