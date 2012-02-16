
from datetime import datetime, timedelta
from django.conf import settings
from django.contrib import auth
from django.core.cache import cache
from django.db.models import Q
from django.utils.translation import ugettext_lazy as _
from anime.forms.Error import UploadMalListForm
from anime.forms.User import ( UserNamesForm, UserEmailForm,
        UserCreationFormMail, NotActiveAuthenticationForm, )
from anime.malconvert import passFile
from anime.models import AnimeRequest, UserStatusBundle, USER_STATUS


def get_username(user):
    username = 'Anonymous'
    if getattr(user, 'first_name', None):
        username = user.first_name
        if user.last_name:
            username += u' ' + user.last_name
    return username


def latest_status(request, user_id=0):
    try:
        if user_id:
            return UserStatusBundle.objects.filter(user=User.objects.get(id=user_id)).latest("changed").changed
        return UserStatusBundle.objects.filter(user=request.user).latest("changed").changed
    except:
        return



def login(request):
    response = {}
    form = None
    if request.user.is_authenticated():
        response['text'] = _('Already logged in.')
    else:
        form = NotActiveAuthenticationForm(data=request.POST or None)
        if form.is_valid():
            user = form.get_user()
            auth.login(request, user)
            response.update({'response': True,
                'text': {'name': get_username(user)}})
        response['form'] = form
    return response


def register(request):
    response = {}
    form = None
    if request.user.is_authenticated():
        response['text'] = _('Already registred.')
    else:
        form = UserCreationFormMail(request.POST or None)
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


def getStatistics(user):
    if not user or not hasattr(user, 'id'):
        return None
    uid = user.id
    tuser = cache.get('Stat:%s' % uid)
    if not tuser:
        tuser = []
        total = {'name': 'Total', 'full': 0, 'count': 0, 'custom': 0}
        for status in USER_STATUS[1::]:
            arr = UserStatusBundle.objects.filter(user=uid, state=status[0]).extra(
                select = {'full': 'SUM(anime_animeitem.episodesCount*anime_animeitem.duration)',
                          'custom': 'SUM(anime_animeitem.duration*anime_userstatusbundle.count)',
                          'count': 'COUNT(*)'}
                ).values('anime__episodesCount', 'anime__duration', 'full', 'custom',
                'count').select_related('anime__episodesCount', 'anime__duration').get()
            arr['name'] = status[1]
            if status[0] == 3:
                arr['custom'] = arr['full']
            #FUUU
            total['full'] += arr['full'] or 0
            total['count'] += arr['count'] or 0
            total['custom'] += arr['custom'] or 0
            tuser.append(arr)
        tuser.append(total)
        cache.set('Stat:%s' % uid, tuser)
    return tuser


def getStyles(user):
    uid = user.id
    styles = cache.get('userCss:%s' % uid)
    if not styles:
        styles = [[] for i in range(0,len(USER_STATUS))]
        if user.is_authenticated():
            statuses = UserStatusBundle.objects.filter(user=user).exclude(state=0).values('anime','state')
            for status in statuses:
                styles[status['state']].append(unicode(status['anime']))
            styles = [[',.r'.join(style), ',.a'.join(style), ',.s'.join(style)] for style in styles]
        cache.set('userCss:%s' % uid, styles)
    return styles
