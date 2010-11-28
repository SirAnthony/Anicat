from django.conf.urls.defaults import *

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()

from anime.models import AnimeGenre, AnimeItem, AnimeStudio

admin.site.register(AnimeGenre)
admin.site.register(AnimeItem)
admin.site.register(AnimeStudio)

urlpatterns = patterns('',
    # Example:
    (r'^anime/', include('anime.urls')),

    # Uncomment the admin/doc line below to enable admin documentation:
    (r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    (r'^admin/', include(admin.site.urls)),
)
