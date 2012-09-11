# Django settings for anicat project.

import os
import sys

try:
    from settings_secrets import *
except ImportError:
    pass

OUR_ROOT = os.path.realpath(os.path.dirname(__file__))

PROJECT_ROOT = OUR_ROOT

DEBUG = True
TEMPLATE_DEBUG = DEBUG
DEPLOY = False

TEST_RUNNER = "code_coverage.CoveragedRunner"
COVERAGE_REPORT_PATH = os.path.join(OUR_ROOT, 'coverage report')

ADMINS = (
    # ('Your Name', 'your_email@domain.com'),
)

DEFAULT_FROM_EMAIL = 'nobody@anicat.net'

if DEBUG:
    EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'


MANAGERS = ADMINS

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'catalogdev',
        'USER': 'catman',
        'PASSWORD': 'catpass',
        'HOST': '',
        'PORT': '',
    }
}

if 'test' in sys.argv:
    DATABASES['default'] = {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': 'test_database.sqlite'
    }

# Local time zone for this installation. Choices can be found here:
# http://en.wikipedia.org/wiki/List_of_tz_zones_by_name
# although not all choices may be available on all operating systems.
# On Unix systems, a value of None will cause Django to use the same
# timezone as the operating system.
# If running in a Windows environment this must be set to the same as your
# system time zone.
TIME_ZONE = 'America/Chicago'

# Language code for this installation. All choices can be found here:
# http://www.i18nguy.com/unicode/language-identifiers.html
LANGUAGE_CODE = 'en-us'

SITE_ID = 1

# If you set this to False, Django will make some optimizations so as not
# to load the internationalization machinery.
USE_I18N = True

# If you set this to False, Django will not format dates, numbers and
# calendars according to the current locale
USE_L10N = True

# Absolute path to the directory that holds media.
# Example: "/home/media/media.lawrence.com/media/"
MEDIA_ROOT = os.path.join(OUR_ROOT, 'files')

IMAGES_ROOT = os.path.join(OUR_ROOT, 'images')

FILE_UPLOAD_HANDLERS = (
    'django.core.files.uploadhandler.MemoryFileUploadHandler',
    'anime.upload.QuotaUploadHandler',
)

# URL that handles the media served from MEDIA_ROOT. Make sure to use a
# trailing slash if there is a path component (optional in other cases).
# Examples: "http://media.lawrence.com", "http://example.com/media/"
MEDIA_URL = '/media/'

# Absolute path to the directory that holds media.
# Example: "/home/media/media.lawrence.com/static/"
STATIC_ROOT = os.path.join(OUR_ROOT, 'static')


# URL that handles the static files served from STATICFILES_ROOT.
# Example: "http://static.lawrence.com/", "http://example.com/static/"
STATIC_URL = '/static/'

# URL prefix for admin media -- CSS, JavaScript and images.
# Make sure to use a trailing slash.
# Examples: "http://foo.com/static/admin/", "/static/admin/".
ADMIN_MEDIA_PREFIX = '/static/admin/'

# A list of locations of additional static files
STATICFILES_DIRS = ()


# List of finder classes that know how to find static files in
# various locations.
STATICFILES_FINDERS = (
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
#    'django.contrib.staticfiles.finders.DefaultStorageFinder',
    'compressor.finders.CompressorFinder',
)

# Make this unique, and don't share it with anybody.
SECRET_KEY = 'o7luz3fx^s7ub^s9t8w_s1s!o-6bn8zgyov_vffx0=&*xenokl'

# List of callables that know how to import templates from various sources.
TEMPLATE_LOADERS = (
    'django.template.loaders.filesystem.Loader',
    'django.template.loaders.app_directories.Loader',
#     'django.template.loaders.eggs.Loader',
)

MIDDLEWARE_CLASSES = (
    'django.middleware.common.CommonMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.middleware.gzip.GZipMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'debug_toolbar.middleware.DebugToolbarMiddleware',
    'audit_log.middleware.UserLoggingMiddleware',
)

ROOT_URLCONF = 'urls'

INTERNAL_IPS = ('127.0.0.1',)

TEMPLATE_DIRS = (
    os.path.join(os.getcwd(), 'html-design')
)

INSTALLED_APPS = (
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.sites',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.admin',
    'django.contrib.admindocs',
    'social_auth',
    'compressor',
    'anime',
    'south',
    'debug_toolbar',
    'django_extensions',
)

#~ COMPRESS_ENABLED = True

DEBUG_TOOLBAR_CONFIG = {
    'INTERCEPT_REDIRECTS': False,
    'SHOW_TOOLBAR_CALLBACK': lambda request: DEBUG and not request.path.startswith('/admin/'),
}

#~ DEBUG_TOOLBAR_PANELS = (
    #~ 'debug_toolbar.panels.version.VersionDebugPanel',
    #~ 'debug_toolbar.panels.timer.TimerDebugPanel',
    #~ 'debug_toolbar.panels.settings_vars.SettingsVarsDebugPanel',
    #~ 'debug_toolbar.panels.headers.HeaderDebugPanel',
    #~ 'debug_toolbar.panels.request_vars.RequestVarsDebugPanel',
    #~ 'debug_toolbar.panels.template.TemplateDebugPanel',
    #~ 'debug_toolbar.panels.sql.SQLDebugPanel',
    #~ 'debug_toolbar.panels.profiling.ProfilingDebugPanel',
    #~ 'debug_toolbar.panels.signals.SignalDebugPanel',
    #~ 'debug_toolbar.panels.logger.LoggingPanel',
#~ )

SESSION_ENGINE = 'django.contrib.sessions.backends.cache'

# A sample logging configuration. The only tangible logging
# performed by this configuration is to send an email to
# the site admins on every HTTP 500 error.
# See http://docs.djangoproject.com/en/dev/topics/logging for
# more details on how to customize your logging configuration.
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'mail_admins': {
            'level': 'ERROR',
            'class': 'django.utils.log.AdminEmailHandler'
        }
    },
    'loggers': {
        'django.request':{
            'handlers': ['mail_admins'],
            'level': 'ERROR',
            'propagate': True,
        },
    }
}

CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.memcached.MemcachedCache',
        'LOCATION': '127.0.0.1:11211',
        'TIMEOUT': 90000
    }
}

INDEX_PAGE_LIMIT = 100
REQUESTS_PAGE_LIMIT = 30
SEARCH_PAGE_LIMIT = 20
USER_PAGE_REQUEST_COUNT = 20
DAYS_BEFORE_EDIT = 15
if 'test' in sys.argv:
    INDEX_PAGE_LIMIT = 40
    REQUESTS_PAGE_LIMIT = 20
    USER_PAGE_REQUEST_COUNT = 4

try:
    from settings_auth import *
except ImportError, e:
    print e
