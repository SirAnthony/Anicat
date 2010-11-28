from django.db import models
from django.forms import ModelForm

ANIME_TYPES = [
    (0, 'TV'),
    (1, 'Movie'),
    (2, 'OAV'),
    (3, 'TV-Sp'),
    (4, 'SMovie'),
    (5, 'ONA'),
    (6, 'AMV')
    ]

class AnimeGenre(models.Model):
    title = models.CharField(max_length=200)
    
    def __unicode__(self):
        return self.title

class AnimeStudio(models.Model):
    title = models.CharField(max_length=200)

    def __unicode__(self):
        return self.title

class AnimeItem(models.Model):
    slug  = models.CharField(max_length=200)
    title = models.CharField(max_length=200)
    genre = models.ForeignKey(AnimeGenre)
    creator = models.ForeignKey(AnimeStudio)
    releaseType = models.CharField(max_length=1, choices=ANIME_TYPES)
    episodesCount = models.IntegerField()
    duration = models.IntegerField()
    releasedAt = models.DateTimeField()
    endedAt = models.DateTimeField()
    
    def __unicode__(self):
        return '%s [%s]' % (self.title, self.releaseType)

class AnimeEpisode(models.Model):
    title = models.CharField(max_length=200)
    anime = models.ForeignKey(AnimeItem)
    
    def __unicode__(self):
        return '%s [%s]' % (self.title, self.anime.title)

class AnimeForm(ModelForm):
    class Meta():
        model = AnimeItem
