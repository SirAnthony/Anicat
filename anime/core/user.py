
from datetime import datetime, timedelta
from django.conf import settings
from django.contrib import auth
from django.contrib.auth.models import User
from django.db.models import Q
from django.http import Http404
from django.utils.translation import ugettext_lazy as _
from anime.forms.Error import UploadMalListForm
from anime.forms.User import ( UserNamesForm, UserEmailForm,
        UserCreationFormMail, NotActiveAuthenticationForm, )
from anime.malconvert import passFile
from anime.models import AnimeItem, AnimeRequest, UserStatusBundle, USER_STATUS
from anime.utils import cache
from anime.utils.catalog import latest_status


ERROR_MESSAGES = {
    'login': {'logined': _('Already logged in.'),},
    'register': {'registred': _('Already registred.')},
    'mallist': {'fast': _('You doing it too often. Try again in {0} minutes.')},
    'user': {'bad': _('No such user.')}
}


def get_username(user):
    if getattr(user, 'first_name', None):
        if user.last_name:
            return u'{0} {1}'.format(user.first_name, user.last_name)
        else:
            return user.first_name
    return 'Anonymous'


def latest_status(request, user_id=0):
    try:
        if user_id:
            user = User.objects.get(id=user_id)
        else:
            user = request.user
        return UserStatusBundle.objects.filter(user=user).latest("changed").changed
    except:
        return


def login(request):
    response = {}
    if request.user.is_authenticated():
        response['text'] = ERROR_MESSAGES['login']['logined']
    else:
        form = NotActiveAuthenticationForm(data=request.POST or None)
        if form.is_valid():
            user = form.get_user()
            auth.login(request, user)
            response.update({'response': True,
                'text': {'name': get_username(user)}})
        else:
            response['form'] = form
    return response


def register(request):
    response = {}
    if request.user.is_authenticated():
        response['text'] = ERROR_MESSAGES['register']['registred']
    else:
        form = UserCreationFormMail(request.POST or None)
        if form.is_valid():
            user = form.save()
            user = auth.authenticate(username=user.username, password=form.cleaned_data['password1'])
            auth.login(request, user)
            response.update({'response': True, 'text': {'name': get_username(user)}})
        else:
            response['form'] = form
    return response


def load_settings(request):
    if not request.user.is_authenticated():
        raise Http404(ERROR_MESSAGES['user']['bad'])
    res = load_MalList(request)
    if 'usernames' in request.POST:
        res['usernames'] = form = UserNamesForm(request.POST or None, instance=request.user)
        if form.is_valid():
            form.save()
    else:
        res['usernames'] = UserNamesForm(instance=request.user)
    if 'emailform' in request.POST:
        res['emailform'] = form = UserEmailForm(request.POST or None, instance=request.user)
        if form.is_valid():
            form.save()
    else:
        res['emailform'] = UserEmailForm(instance=request.user)
    return res


def load_MalList(request):
    lastLoad = cache.get('MalList:%s' % request.user.id)
    if 'mallist' in request.POST:
        form = UploadMalListForm(request.POST or None, request.FILES)
    else:
        form = UploadMalListForm()
    if form.is_valid():
        timeLeft = 0
        try:
            timeLeft = (1800 - (datetime.now() - lastLoad['date']).seconds) / 60
        except TypeError:
            lastLoad = {}
        if lastLoad and timeLeft > 0:
            form.addError(ERROR_MESSAGES['mallist']['fast'].format(timeLeft))
        else:
            status, error = passFile(request.FILES['file'],
                    request.user, form.cleaned_data['rewrite'])
            if not status:
                form.addError(error)
            else:
                lastLoad['list'] = {'updated': True}
    return {'mallistform': form, 'mallist': lastLoad}


def get_requests(user, *keys):
    try:
        qs = AnimeRequest.objects.filter(user=user).order_by('status', '-id')
        qs = qs.exclude(Q(status__gt=2) & Q(changed__lte=datetime.now() - timedelta(days=20)))
        c = qs.filter(status__gt=2).count()
        if c > settings.USER_PAGE_REQUEST_COUNT:
            qs = qs[:qs.count() - (c - settings.USER_PAGE_REQUEST_COUNT/2)]
        if keys:
            qs = qs.values(*keys)
        types = AnimeRequest._meta.get_field('requestType').choices
        return {'requests': list(qs),
                'requestTypes': types}
    except:
        return {}


def get_statistics(request, user_id = 0):
    user = user_id or request.POST.get('user_id', 0) or request.user
    try:
        if isinstance(user, User):
            if not user.is_authenticated():
                raise User.DoesNotExist
        else:
            user = User.objects.get(id=user)
    except (User.DoesNotExist, ValueError, TypeError):
        raise Http404(ERROR_MESSAGES['user']['bad'])
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
                #TODO: we need only one anime__X value for django orm works
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
        cache.cset('Stat:%s' % uid, tuser)
    return {'userid': uid, 'stat': tuser}


def export_statistic(request):
    if not request.user.is_authenticated():
        raise Http404(ERROR_MESSAGES['user']['bad'])
    pk = latest_status(request.user)
    cachestr = 'statusexport:{0}'.format(request.user.id)
    cachename = 'statusexportdata:{0}'.format(request.user.id)
    data = cache.get(cachename)
    if not data or not cache.latest('StatisticExport',
                    cachestr, {'UserStatusBundle': pk}):
        data = AnimeItem.objects.filter(statusbundles__user=request.user,
                                        statusbundles__state__gt=0).\
                extra(select={
                        'names': """SELECT GROUP_CONCAT(`anime_animename`.`title` SEPARATOR "||")
                FROM `anime_animename` WHERE `anime_animename`.`anime_id` = `anime_animeitem`.`id`""",
                        'my_state': 'anime_userstatusbundle.state',
                        'my_count': 'anime_userstatusbundle.count',
                        'my_rating': 'anime_userstatusbundle.rating',
                        'my_changed': 'anime_userstatusbundle.changed',
                }).values('id', 'releasedAt', 'episodesCount', 'endedAt',
                'title', 'releaseType', 'air', 'duration', 'names',
                'my_state', 'my_count', 'my_rating', 'my_changed')
        for item in data:
            item['names'] = item['names'].split('||')
        cache.cset(cachename, data)
        cache.update_named_cache(cachestr)
    update = cache.get(cachestr)
    return {'response': 'export', 'text': {'last_update': update, 'data': data}}


def get_styles(user):
    if not user or not getattr(user, 'id', None):
        return None
    uid = user.id
    styles = cache.get('userCss:%s' % uid)
    if not styles:
        styles = [[] for i in range(0,len(USER_STATUS))]
        if user.is_authenticated():
            statuses = UserStatusBundle.objects.filter(user=user).exclude(state=0).values('anime','state')
            for status in statuses:
                styles[status['state']].append(unicode(status['anime']))
            styles = [[',.r'.join(style), ',.a'.join(style), ',.s'.join(style)] for style in styles]
        cache.cset('userCss:%s' % uid, styles)
    return styles
