import datetime
import re
from django.core.exceptions import ValidationError
from django.contrib.auth.models import User
from django.test import TestCase
from anime.forms import fields
from anime.forms.create import createFormFromModel
from anime.models import AnimeItem, UserStatusBundle, AnimeRequest, AnimeImageRequest, DATE_FORMATS
from anime.tests.functions import create_user, login, last_record



class FormsTest(TestCase):
    pass

class RequestsFormsTest(TestCase):

    fixtures = ['2trash.json']

    @create_user()
    def setUp(self):
        self.anime = AnimeItem.objects.get(id=1)

    def test_PureRequestForm(self):
        u = User.objects.get(id=1)
        r = AnimeRequest(anime=AnimeItem.objects.get(id=1), text="0",
                         requestType=1, status=2,)
        F = createFormFromModel(AnimeRequest)
        f = F({'status': 3}, instance=r, user=u)
        self.assertEquals(f.is_valid(), False)
        self.assertEquals(f.errors['status'][0], f.error_messages['notchangable'])

    def test_ImageRequestForm(self):
        F = createFormFromModel(AnimeImageRequest)
        try:
            F()
        except ValueError, e:
            if not unicode(F.error_messages['notexists']) == unicode(e.message):
                raise AssertionError
        self.assertRaisesRegexp(TypeError,
            unicode(F.error_messages['notanime']).format(type(UserStatusBundle).__name__),
            F, instance=UserStatusBundle.objects.get(id=1))
        anime = AnimeItem.objects.get(id=1)
        f = F(files={'text': 'file'}, instance=anime)
        self.assertEquals(f.is_valid(), False)
        f = F(files={'text': 'file'}, instance=anime)
        #self.assertEquals(f.errors['status'][0], f.error_messages['notchangable'])


class FormsErrorTests(TestCase):

    def test_ErrorForm(self):
        from anime.forms.Error import ErrorForm
        f = ErrorForm()
        f.addError(1)
        self.assertEquals(f.is_valid(), False)
        self.assertEquals(f.non_field_errors()[-1], 1)


class FormsModelErrorTests(TestCase):

    fixtures = ['2trash.json']

    def setUp(self):
        self.anime = AnimeItem.objects.get(id=1)

    @create_user()
    def test_ReadOnlyModelForm(self):
        r = AnimeRequest(user=User.objects.get(id=1), requestType=0, status=0, text="0")
        r.save()
        F = createFormFromModel(AnimeRequest)
        f = F({'status': 3})
        self.assertEquals(f.is_valid(), False)
        self.assertEquals(f.non_field_errors()[-1], 'This form is read-only for you.')
        f = F({'status': 3})
        f.writeable()
        self.assertEquals(f.is_valid(), True)

    def test_ErrorModelForm(self):
        F = createFormFromModel(AnimeItem, ['title'])
        f = F({'title': 'new'}, instance=self.anime)
        self.assertEquals(f.is_valid(), True)
        f.addError(1)
        self.assertEquals(f.is_valid(), False)
        self.assertEquals(f.non_field_errors()[-1], 1)

    def test_AnimeForm(self):
        F = createFormFromModel(AnimeItem, ['title', 'releasedAt'])
        f = F({'title': self.anime.title, 'releasedAt': self.anime.releasedAt.strftime(DATE_FORMATS[0])})
        self.assertEquals(f.is_valid(), False)
        self.assertEquals(f.non_field_errors()[-1],
            'Anime record already exists: "{0}" ({1}).'.format(
                self.anime.title, self.anime.id))

    @create_user()
    def test_UserStatusForm(self):
        #TODO: Nothing checked.
        F = createFormFromModel(UserStatusBundle)
        F()
        ub = UserStatusBundle.objects.get(id=1)
        ub.state = 2
        F(instance=ub)

class FormsUserTests(TestCase):

    @create_user()
    def setUp(self):
        pass

    def test_UserCreationFormMail(self):
        from anime.forms.User import UserCreationFormMail
        f = UserCreationFormMail({'register-email': User.objects.get(id=1).email})
        self.assertEquals(f.is_valid(), False)
        self.assertEquals(f.errors['email'][-1], f.error_messages['duplicate_email'])
        f = UserCreationFormMail({'register-email': 'new@example.com'})
        self.assertEquals(f.is_valid(), True)
        c = last_record(User)
        f.save()
        self.assertEquals(last_record(User), c+1)

    def test_NotActivePasswordResetForm(self):
        from anime.forms.User import NotActivePasswordResetForm, UNUSABLE_PASSWORD
        f = NotActivePasswordResetForm({'email': User.objects.get(id=1).email})
        self.assertEquals(f.is_valid(), True)
        f = NotActivePasswordResetForm({'email': 'b@bb.bb'})
        self.assertEquals(f.is_valid(), False)
        self.assertEquals(f.errors['email'][0], f.error_messages['unknown'])
        u = User.objects.get(id=1)
        u.password = UNUSABLE_PASSWORD
        u.save()
        f = NotActivePasswordResetForm({'email': u.email})
        self.assertEquals(f.is_valid(), False)
        self.assertEquals(f.errors['email'][0], f.error_messages['unusable'])

    def test_NotActiveAuthenticationForm(self):
        from anime.forms.User import NotActiveAuthenticationForm
        from anime.tests.functions import email, passwd
        f = NotActiveAuthenticationForm(data={'username': email, 'password': passwd})
        self.assertEquals(f.is_valid(), True)
        f = NotActiveAuthenticationForm(data={'username': 'a', 'password': 'b'})
        self.assertEquals(f.is_valid(), False)
        self.assertEquals(f.non_field_errors()[-1], f.error_messages['wrong'])


class FormsFieldsTests(TestCase):

    fixtures = ['2trash.json']

    #remove in 1.4
    def assertRaisesMessage(self, expected_exception, expected_message,
                            callable_obj=None, *args, **kwargs):
        return self.assertRaisesRegexp(expected_exception,
            re.escape(expected_message), callable_obj, *args, **kwargs)

    def test_TextToAnimeItemField(self):
        f = fields.TextToAnimeItemField()
        self.assertEquals(f.to_python(''), None)
        self.assertEquals(f.to_python('1'), AnimeItem.objects.get(id=1))
        self.assertRaisesMessage(ValidationError,
            u'AnimeItem matching query does not exist.',
            f.to_python, 'a')
        AnimeItem(releasedAt="1987-9-30 00:00", episodesCount=230,
                  title='dwkydani zjrq mj', releasedKnown=0,
                  releaseType=5, endedKnown=0, duration=17).save()
        self.assertRaisesMessage(ValidationError,
            f.error_messages['multiple'], f.to_python, 'dwkydani zjrq mj')

    def test_TextToAnimeNameField(self):
        f = fields.TextToAnimeNameField()
        self.assertEquals(f.to_python(''), None)
        self.assertRaisesMessage(ValidationError,
            f.error_messages['noname'], f.to_python, 'dwkydani zjrq mj')
        f._animeobject = 1
        self.assertRaisesRegexp(ValidationError,
            u'Cannot assign "1": "AnimeName.anime" must be a "AnimeItem" instance.',
            f.to_python, 'dwkydani zjrq mj')
        f._animeobject = AnimeItem.objects.get(id=1)
        self.assertEquals(f.to_python('dwkydani zjrq mj').anime, f._animeobject)

    def test_TextToAnimeLinkField(self):
        f = fields.TextToAnimeLinkField()
        self.assertRaisesMessage(ValidationError,
            f.error_messages['notype'], f.to_python, '')
        f._linktype = 0
        self.assertEquals(f.to_python(' '), None)
        #
        self.assertRaisesMessage(ValidationError,
            f.error_messages['badtype'], f.to_python, u'1')
        self.assertEquals(f._linktype, 15)
        for link in fields.LINKS_URLS:
            if link[1] and link[2]:
                #Check for all links types have correct suggestion
                f._linktype = 0
                self.assertEquals(f.to_python(link[2].format(1)),
                                    link[2].format(1))
                self.assertEquals(f._linktype, link[0])
                #Check for bad link for type
                f._linktype = link[0]
                self.assertRaisesMessage(ValidationError,
                    f.error_messages['badlink'], f.to_python, link[2])

    def test_CalendarWidget(self):
        #TODO: write complete test
        f = fields.CalendarWidget()
        f.render('calendar', datetime.date.today())
        f._known = 9
        f.render('calendar', datetime.date.today())

    def test_UnknownDateField(self):
        f = fields.UnknownDateField()
        self.assertEquals(f.to_python(' '), None)
        self.assertEquals(f.to_python(datetime.datetime.now()), datetime.date.today())
        self.assertEquals(f.to_python(datetime.date.today()), datetime.date.today())
        f.label = 'ended'
        for frmt in f.input_formats:
            f.to_python(datetime.date.today().strftime(frmt))
        self.assertRaisesMessage(ValidationError,
                f.error_messages['invalid'], f.to_python, 'notadate')

    def test_CardImageField(self):
        f = fields.CardImageField()
        self.assertEquals(f.to_python(None), None)
