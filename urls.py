from django.conf.urls import *

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
from django.db.models.loading import get_models, get_app
admin.autodiscover()

for m in get_models(get_app('anime')):
    try:
        admin.site.register(m)
    except Exception, e:
        print e

urlpatterns = patterns('',
    # Example:
    (r'^', include('anime.urls')),

    # Uncomment the admin/doc line below to enable admin documentation:
    (r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    (r'^admin/', include(admin.site.urls)),
)
