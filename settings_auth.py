
from anime.utils.config import random_string

AUTHENTICATION_BACKENDS = (
    #'social_auth.backends.twitter.TwitterBackend',
    #'social_auth.backends.facebook.FacebookBackend',
    #'social_auth.backends.google.GoogleOAuthBackend',
    #'social_auth.backends.google.GoogleOAuth2Backend',
    'social_auth.backends.google.GoogleBackend',
    'social_auth.backends.yahoo.YahooBackend',
    #'social_auth.backends.contrib.linkedin.LinkedinBackend',
    #'social_auth.backends.contrib.livejournal.LiveJournalBackend',
    #'social_auth.backends.contrib.orkut.OrkutBackend',
    #'social_auth.backends.contrib.foursquare.FoursquareBackend',
    'social_auth.backends.contrib.github.GithubBackend',
    'social_auth.backends.OpenIDBackend',
    'anime.backends.EmailLoginBackend',
    'django.contrib.auth.backends.ModelBackend',
)

SOCIAL_AUTH_ENABLED_BACKENDS = ('google', 'yahoo', 'openid')

TEMPLATE_CONTEXT_PROCESSORS = (
    'django.contrib.auth.context_processors.auth',
    'django.core.context_processors.debug',
    'django.core.context_processors.i18n',
    'django.core.context_processors.media',
    'django.core.context_processors.request',
    'django.contrib.messages.context_processors.messages',
    'social_auth.context_processors.social_auth_by_type_backends',
)



LOGIN_ERROR_URL = '/login/error/'
SOCIAL_AUTH_LOGIN_REDIRECT_URL = '/login/done/'

SOCIAL_AUTH_CREATE_USERS = True
SOCIAL_AUTH_FORCE_RANDOM_USERNAME = False
SOCIAL_AUTH_DEFAULT_USERNAME = random_string
SOCIAL_AUTH_COMPLETE_URL_NAME = 'socialauth_complete'
#SOCIAL_AUTH_USER_MODEL = 'app.CustomUser'
SOCIAL_AUTH_ERROR_KEY = 'socialauth_error'
