import collections
from django.db import models
from django.forms import ModelForm
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm

ANIME_TYPES = [
    (0, u'TV'),
    (1, u'Movie'),
    (2, u'OAV'),
    (3, u'TV-Sp'),
    (4, u'SMovie'),
    (5, u'ONA'),
    (6, u'AMV')
    ]

USER_STATUS = [
    (0, u'none'),
    (1, u'want'),
    (2, u'now'),
    (3, u'ok'),
    (4, u'dropped'),
    (5, u'partially watched'),
]

class Genre(models.Model):
    name = models.CharField(max_length=200, db_index=True, unique=True)
    
    def __unicode__(self):
        return self.name

class AnimeBundle(models.Model):
    
    @classmethod
    def tie(cls, one, two):
        try:
            bundle = one.bundle or two.bundle
            if not bundle:
                bundle = cls()
                bundle.save()
            one.bundle = two.bundle = bundle
            one.save()
            two.save()
        except Exception, e:
            raise Exception, e

class AnimeItem(models.Model):
    title = models.CharField(max_length=200, db_index=True, unique_for_date='releasedAt')
    genre = models.ManyToManyField(Genre)
    releaseType = models.IntegerField(choices=ANIME_TYPES)
    episodesCount = models.IntegerField()
    duration = models.IntegerField()
    releasedAt = models.DateTimeField()
    endedAt = models.DateTimeField(blank=True, null=True)
    bundle = models.ForeignKey(AnimeBundle, related_name='animeitems', null=True, blank=True)
    air = models.BooleanField()
    
    def __unicode__(self):
        return '%s [%s]' % (self.title, ANIME_TYPES[self.releaseType][1])

    def releaseTypeS(self):
        return ANIME_TYPES[self.releaseType][1]
    
    def translation(self):
        if self.endedAt:
            return ' - '.join([self.releasedAt.strftime("%d.%m.%Y"), self.endedAt.strftime("%d.%m.%Y")])
        return self.releasedAt.strftime("%d.%m.%Y")
    
    class Meta:
        ordering = ["title"]

class AnimeEpisode(models.Model):
    title = models.CharField(max_length=200)
    anime = models.ForeignKey(AnimeItem, related_name="animeepisodes")
    
    def __unicode__(self):
        return '%s [%s]' % (self.title, self.anime.title)
    
    class Meta:
        unique_together = ("title", "anime")


class AnimeName(models.Model):
    title = models.CharField(max_length=200)
    anime = models.ForeignKey(AnimeItem, related_name="animenames")
    
    def __unicode__(self):
        return self.title
    
    class Meta:
        ordering = ["title"]
        unique_together = ("title", "anime")

class AnimeForm(ModelForm):
    class Meta():
        model = AnimeItem
        exclude = ('air',)

class Credit(models.Model):
    title = models.CharField(max_length=200, unique=True)
    
    def __unicode__(self):
        return self.title
    
class Organisation(models.Model):
    name = models.CharField(max_length=200, unique=True)
    
    def __unicode__(self):
        return self.name

class OrganisationBundle(models.Model):
    anime = models.ForeignKey(AnimeItem, related_name="organisationbundles")
    organisation = models.ForeignKey(Organisation, related_name="organisationbundles")
    job = models.ForeignKey(Credit)
    role = models.CharField(max_length=30, blank=True)
    comment = models.CharField(max_length=100, blank=True)

    class Meta:
        unique_together = ("anime", "organisation", "job", "role")

class People(models.Model):
    name = models.CharField(max_length=200, unique=True)
    
    def __unicode__(self):
        return self.name

class PeopleBundle(models.Model):
    anime = models.ForeignKey(AnimeItem, related_name="peoplebundles")
    person = models.ForeignKey(People, related_name="peoplebundles")
    job = models.ForeignKey(Credit)
    role = models.CharField(max_length=30, blank=True)
    comment = models.CharField(max_length=100, blank=True)

    class Meta:
        unique_together = ("anime", "person", "job", "role")


class StatusManager(models.Manager):
    def get_for_user(self, items, user):
        statuses = self.filter(anime__in=[anime.id for anime in items], user=user)
        status_dict = collections.defaultdict(lambda: None)
        for status in statuses:
            status_dict[status.anime_id] = status
        return status_dict

class UserStatusBundle(models.Model):
    anime = models.ForeignKey(AnimeItem, related_name="statusbundles")
    user = models.ForeignKey(User)
    status = models.IntegerField(choices=USER_STATUS)
    count = models.IntegerField(blank=True)
    changed = models.DateTimeField(auto_now=True)
    
    objects = StatusManager()

    class Meta:
        unique_together = ("anime", "user")

class UserCreationFormMail(UserCreationForm):
    def __init__(self, *args, **kwargs):
        super(UserCreationFormMail, self).__init__(*args, **kwargs)
        self.fields['email'].required = True

    class Meta:
        model = User
        fields = ('username', 'email') 