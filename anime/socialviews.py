
from django.contrib import messages
from django.contrib.auth import login
from django.http import HttpResponseRedirect, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from social_auth.views import dsa_view, auth_complete, \
    REDIRECT_FIELD_NAME, SESSION_EXPIRATION, SOCIAL_AUTH_LAST_LOGIN, \
    NEW_USER_REDIRECT, DEFAULT_REDIRECT, INACTIVE_USER_URL, \
    LOGIN_ERROR_URL, ERROR_MESSAGE



@csrf_exempt
@dsa_view()
def complete(request, backend, *args, **kwargs):
    """Authentication complete view, override this view if transaction
    management doesn't suit your needs."""
    return complete_process(request, backend, *args, **kwargs)


def complete_process(request, backend, *args, **kwargs):
    """Authentication complete process"""
    # pop redirect value before the session is trashed on login()
    redirect_value = request.session.get(REDIRECT_FIELD_NAME, '')
    user = auth_complete(request, backend, *args, **kwargs)

    if isinstance(user, HttpResponse):
        return user

    if user:
        login(request, user)
        # user.social_user is the used UserSocialAuth instance defined
        # in authenticate process
        social_user = user.social_user

        if SESSION_EXPIRATION:
            # Set session expiration date if present and not disabled by
            # setting. Use last social-auth instance for current provider,
            # users can associate several accounts with a same provider.
            if social_user.expiration_delta():
                request.session.set_expiry(social_user.expiration_delta())

        # store last login backend name in session
        request.session[SOCIAL_AUTH_LAST_LOGIN] = social_user.provider

        # Remove possible redirect URL from session, if this is a new
        # account, send him to the new-users-page if defined.
        if NEW_USER_REDIRECT and getattr(user, 'is_new', False):
            url = NEW_USER_REDIRECT
        else:
            url = redirect_value or DEFAULT_REDIRECT
    else:
        if ERROR_MESSAGE:
            messages.error(request, ERROR_MESSAGE)
        url = LOGIN_ERROR_URL
    return HttpResponseRedirect(url)
