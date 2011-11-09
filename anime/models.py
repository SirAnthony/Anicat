# -*- coding: utf-8 -*-
import collections
import os
from audit_log.models.managers import AuditLog
from django.db import models, IntegrityError
from django.contrib.auth.models import User
from settings import MEDIA_ROOT, IMAGES_ROOT

ANIME_TYPES = [
    (0, u'TV'),
    (1, u'Movie'),
    (2, u'OAV'),
    (3, u'TV-Sp'),
    (4, u'SMovie'),
    (5, u'ONA'),
    (6, u'AMV'),
    (7, u'Other')
]

LINKS_TYPES = [
    (0, u'Auto'),
    (1, u'AniDB'),
    (2, u'ANN'),
    (3, u'MAL'),
    (4, u'Wikipedia'),
    (6, u'Official page'),
    (15, u'Other')
]

USER_STATUS = [
    (0, u'none'),
    (1, u'want'),
    (2, u'now'),
    (3, u'done'),
    (4, u'dropped'),
    (5, u'partially watched'),
]

DATE_FORMATS = (
    "%d.%m.%Y", "??.%m.%Y", "%d.??.%Y",
    "??.??.%Y", "%d.%m.??", "??.%m.??",
    "%d.??.??", "??.??.??",
)

REQUEST_TYPE = [
    (0, u'Anime'),
    (1, u'Image'),
    (2, u'Feedback'),
]

REQUEST_STATUS = [
    (0, u'Opened'),
    (1, u'Rejected'),
    (2, u'Accepted'),
    (3, u'Done'),
]


class Genre(models.Model):
    name = models.CharField(max_length=200, db_index=True, unique=True)

    def __unicode__(self):
        return self.name

    class Meta:
        ordering = ["name"]


class Credit(models.Model):
    title = models.CharField(max_length=200, unique=True)

    def __unicode__(self):
        return self.title


class AnimeBundle(models.Model):

    def __setattr__(self, name, value):
        if name.find('bundle') == 0:
            if not hasattr(self, 'tied'):
                setattr(self, 'tied', [])
            if value and value not in self.tied:
                self.tied.append(value)
            return
        super(AnimeBundle, self).__setattr__(name, value)

    def loadOldItems(self):
        if not self.id:
            return
        for animeitem in self.animeitems.all():
            setattr(self, 'bundle', animeitem)

    def save(self):
        '''
        WARNING! This function removes bundles from all items
        which is not in tied array. For linking single items
        use tie classmethod instead.
        '''
        super(AnimeBundle, self).save()
        if not hasattr(self, 'tied') or not self.tied:
            return
        if self.id:
            for item in self.tied:
                bundle = item.bundle
                item.bundle = self
                item.save()
                self.removeLast(bundle)
        for animeitem in self.animeitems.all():
            if animeitem not in self.tied:
                animeitem.bundle = None
                animeitem.save()
        self.tied = []
        self.removeLast(self)

    @classmethod
    def tie(cls, one, two):
        if not one or not two:
            raise ValueError('Blank field.')
        if not one.bundle or not two.bundle or one.bundle != two.bundle:
            if isinstance(cls, AnimeBundle):
                bundle = cls
            else:
                bundle = one.bundle or two.bundle or cls()
            if not bundle.id:
                super(AnimeBundle, bundle).save()
            one.bundle = two.bundle = bundle
            one.save()
            two.save()

    @classmethod
    def untie(cls, item):
        if not item:
            return
        bundle = item.bundle
        if bundle:
            item.bundle = None
            item.save()
            removeLast(bundle)

    @classmethod
    def removeLast(cls, bundle):
        if not bundle or not bundle.id:
            return
        items = bundle.animeitems.all()
        if len(items) < 2:
            for item in items:
                item.bundle = None
                item.save()
            bundle.delete()


class AnimeItem(models.Model):
    title = models.CharField(max_length=200,
            db_index=True, unique_for_date='releasedAt')
    genre = models.ManyToManyField(Genre)
    releaseType = models.IntegerField(choices=ANIME_TYPES)
    episodesCount = models.IntegerField()
    duration = models.IntegerField()
    releasedAt = models.DateTimeField()
    releasedKnown = models.SmallIntegerField(blank=True, default=0)
    endedAt = models.DateTimeField(blank=True, null=True)
    endedKnown = models.SmallIntegerField(blank=True, default=0)
    bundle = models.ForeignKey('AnimeBundle',
            related_name='animeitems', null=True, blank=True)
    air = models.BooleanField()
    audit_log = AuditLog()

    class Meta:
        ordering = ["title"]

    def __unicode__(self):
        if self.id:
            return '%s [%s]' % (self.title, ANIME_TYPES[self.releaseType][1])
        return ''

    def _getReleaseTypeString(self):
        return ANIME_TYPES[self.releaseType][1]

    def _getRelease(self):
        #FIXME ЧЗХ
        try:
            if self.endedAt:
                return ' - '.join([
                    self.releasedAt.strftime(DATE_FORMATS[self.releasedKnown]) if self.releasedKnown != 7 else '?',
                    self.endedAt.strftime(DATE_FORMATS[self.endedKnown]) if self.endedKnown != 7 else '?'
                ])
            return self.releasedAt.strftime(DATE_FORMATS[self.releasedKnown]) if self.releasedKnown != 7 else '?'
        except ValueError:
            return 'Bad value'

    releaseTypeS = property(_getReleaseTypeString)
    release = property(_getRelease)

    def save(self, *args, **kwargs):
        try:
            last = self.audit_log.latest('action_date')
        except:
            last = None
        super(AnimeItem, self).save(*args, **kwargs)
        if not last or last.title != self.title:
            if last:
                title = last.title
            else:
                title = self.title
            name, created = AnimeName.objects.get_or_create(
                                        anime=self, title=title)
            if not created:
                name.title = self.title
            try:
                name.save()
            except IntegrityError:
                # Already exists
                pass


class AnimeEpisode(models.Model):
    title = models.CharField(max_length=200, db_index=True)
    anime = models.ForeignKey(AnimeItem, related_name="animeepisodes")
    audit_log = AuditLog()

    class Meta:
        unique_together = ("title", "anime")

    def __unicode__(self):
        return '%s [%s]' % (self.title, self.anime.title)


class AnimeName(models.Model):
    title = models.CharField(max_length=200)
    anime = models.ForeignKey(AnimeItem, related_name="animenames")
    audit_log = AuditLog()

    class Meta:
        ordering = ["title"]
        unique_together = ("title", "anime")

    def __unicode__(self):
        return self.title


class AnimeLink(models.Model):
    anime = models.ForeignKey(AnimeItem, related_name="links")
    link = models.URLField(max_length=100)
    linkType = models.IntegerField(choices=LINKS_TYPES)
    audit_log = AuditLog()

    class Meta:
        unique_together = ("link", "anime")

    def save(self, *args, **kwargs):
        if self.linkType == 0:
            self.linkType = LINKS_TYPES[-1][0]
        super(AnimeLink, self).save(*args, **kwargs)


class AnimeLinks(models.Model):
    anime = models.ForeignKey(AnimeItem, related_name="links1")
    AniDB = models.IntegerField(blank=True, null=True)
    ANN = models.IntegerField(blank=True, null=True)
    MAL = models.IntegerField(unique=True, blank=True, null=True)
    audit_log = AuditLog()


class Organisation(models.Model):
    name = models.CharField(max_length=200, unique=True)
    audit_log = AuditLog()

    def __unicode__(self):
        return self.name


class OrganisationBundle(models.Model):
    anime = models.ForeignKey(AnimeItem, related_name="organisationbundles")
    organisation = models.ForeignKey(Organisation,
            related_name="organisationbundles")
    job = models.ForeignKey(Credit)
    role = models.CharField(max_length=30, blank=True)
    comment = models.CharField(max_length=100, blank=True)
    audit_log = AuditLog()

    class Meta:
        unique_together = ("anime", "organisation", "job", "role")


class People(models.Model):
    name = models.CharField(max_length=200, unique=True)
    audit_log = AuditLog()

    def __unicode__(self):
        return self.name


class PeopleBundle(models.Model):
    anime = models.ForeignKey(AnimeItem, related_name="peoplebundles")
    person = models.ForeignKey(People, related_name="peoplebundles")
    job = models.ForeignKey(Credit)
    role = models.CharField(max_length=30, blank=True)
    comment = models.CharField(max_length=100, blank=True)
    audit_log = AuditLog()

    class Meta:
        unique_together = ("anime", "person", "job", "role")


class StatusManager(models.Manager):
    def get_for_user(self, items, user):
        #TODO: Think about .values()
        statuses = self.filter(
                anime__in=[anime.id for anime in items], user=user)
        status_dict = collections.defaultdict(lambda: None)
        for status in statuses:
            status_dict[status.anime_id] = status
        return status_dict


class UserStatusBundle(models.Model):
    anime = models.ForeignKey(AnimeItem, related_name="statusbundles")
    user = models.ForeignKey(User)
    state = models.IntegerField(choices=USER_STATUS)
    count = models.IntegerField(blank=True, null=True)
    changed = models.DateTimeField(auto_now=True)

    objects = StatusManager()

    class Meta:
        unique_together = ("anime", "user")

    def save(self, *args, **kwargs):
        if self.state in (2, 4):
            if self.count < 1:
                self.count = 1
            else:
                limit = self.anime.episodesCount
                if self.count > self.anime.episodesCount:
                    self.count = self.anime.episodesCount
        else:
            self.count = None
        super(UserStatusBundle, self).save(*args, **kwargs)


class AnimeRequest(models.Model):
    user = models.ForeignKey(User)
    anime = models.ForeignKey(AnimeItem,
            related_name="requests", blank=True, null=True)
    requestType = models.IntegerField(choices=REQUEST_TYPE)
    text = models.CharField(max_length=5000)
    status = models.IntegerField(choices=REQUEST_STATUS)
    reason = models.CharField(max_length=1000, blank=True, null=True)
    changed = models.DateTimeField(auto_now=True)

    def __init__(self, *args, **kwargs):
        if 'status' not in kwargs:
            kwargs['status'] = 0
        super(AnimeRequest, self).__init__(*args, **kwargs)

    def save(self, *args, **kwargs):
        if self.requestType == 1 and self.status and self.text != "0.png":
            if not self.anime:
                raise IntegrityError("Anime name cannot be null for image request.")
            filename = os.path.join(MEDIA_ROOT, self.text)
            if not os.path.exists(filename):
                raise OSError('File does not exists.')
            if self.status > 1:
                ext = filename.rsplit('.', 1)[-1]
                os.rename(filename,
                        os.path.join(IMAGES_ROOT,
                            '%s.%s' % (self.anime_id, ext)))
                self.status = 3
            else:
                os.unlink(filename)
            self.text = "0.png"
        super(AnimeRequest, self).save(*args, **kwargs)


class AnimeItemRequest(AnimeRequest):

    class Meta:
        proxy = True

    def __init__(self, *args, **kwargs):
        kwargs['requestType'] = 0
        super(AnimeItemRequest, self).__init__(*args, **kwargs)


class AnimeImageRequest(AnimeRequest):

    class Meta:
        proxy = True

    def __init__(self, *args, **kwargs):
        kwargs['requestType'] = 1
        super(AnimeImageRequest, self).__init__(*args, **kwargs)


class AnimeFeedbackRequest(AnimeRequest):

    class Meta:
        proxy = True

    def __init__(self, *args, **kwargs):
        kwargs['requestType'] = 2
        super(AnimeFeedbackRequest, self).__init__(*args, **kwargs)


EDIT_MODELS = {
    'anime': AnimeItem,
    #'episode': AnimeEpisode,
    'bundle': AnimeBundle,
    'name': AnimeName,
    'links': AnimeLink,
    #'organisation': Organisation,
    #'organisationbundle': OrganisationBundle,
    #'people': People,
    #'peoplebundle': PeopleBundle,
    'state': UserStatusBundle,
    'request': AnimeRequest,
    'animerequest': AnimeItemRequest,
    'image': AnimeImageRequest,
    'feedback': AnimeFeedbackRequest,
}
