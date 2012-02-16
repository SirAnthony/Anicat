
import anime.user as userMethods

from django.contrib import auth
from django.contrib.auth.models import User
from django.contrib.messages.api import get_messages
from django.http import Http404, HttpResponseRedirect
from django.views.decorators.http import condition
from django.views.decorators.cache import cache_control
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
    if not request.user.is_authenticated():
        raise Http404
    response = userMethods.load_settings(request)
    response.update(userMethods.getRequests(request.user))
    return response


@condition(last_modified_func=userMethods.latest_status)
@render_to('anime/stat.html')
def statistics(request, user_id=0):
    if user_id:
        try:
            user = User.objects.get(id=user_id)
        except User.DoesNotExist:
            raise Http404
    elif request.user.is_authenticated():
        user = request.user
    else:
        raise Http404
    res = userMethods.getStatistics(user)
    return {'userid': getattr(user, 'id', None), 'stat': res}


@cache_control(private=True, no_cache=True)
@condition(last_modified_func=userMethods.latest_status)
@render_to('anime/user.css', 'text/css')
def generate_css(request):
    return {'style': userMethods.getStyles(request.user)}

