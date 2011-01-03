from django.db import models
from django.forms import ModelForm

ANIME_TYPES = [
    (u'0', u'TV'),
    (u'1', u'Movie'),
    (u'2', u'OAV'),
    (u'3', u'TV-Sp'),
    (u'4', u'SMovie'),
    (u'5', u'ONA'),
    (u'6', u'AMV')
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
    slug  = models.CharField(max_length=200, db_index=True)
    title = models.CharField(max_length=200)
    genre = models.ForeignKey(AnimeGenre)
    creator = models.ForeignKey(AnimeStudio)
    releaseType = models.CharField(max_length=1, choices=ANIME_TYPES)
    episodesCount = models.IntegerField()
    duration = models.IntegerField()
    releasedAt = models.DateTimeField()
    endedAt = models.DateTimeField()
    anipic = models.ImageField(upload_to='animes')
    
    def __unicode__(self):
        return '%s [%s]' % (self.title, dict(ANIME_TYPES)[self.releaseType])

class AnimeEpisode(models.Model):
    title = models.CharField(max_length=200)
    anime = models.ForeignKey(AnimeItem)
    
    def __unicode__(self):
        return '%s [%s]' % (self.title, self.anime.title)

class AnimeForm(ModelForm):
    class Meta():
        model = AnimeItem
        exclude = ('slug',)

