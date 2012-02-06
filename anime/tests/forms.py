import datetime
import re
import os
from django.conf import settings
from django.core.files.uploadedfile import SimpleUploadedFile, TemporaryUploadedFile
from django.core.exceptions import ValidationError
from django.contrib.auth.models import User
from django.test import TestCase
from anime.forms import fields
from anime.forms import json
from anime.forms.create import createFormFromModel
from anime.models import ( AnimeItem, AnimeBundle, AnimeName, AnimeLink,
    UserStatusBundle, AnimeRequest, AnimeImageRequest, DATE_FORMATS, )
from anime.tests.functions import create_user, login, last_record



class FormsTest(TestCase):

    #remove in 1.4
    def assertRaisesMessage(self, expected_exception, expected_message,
                            callable_obj=None, *args, **kwargs):
        return self.assertRaisesRegexp(expected_exception,
            re.escape(expected_message), callable_obj, *args, **kwargs)

class RequestsFormsTest(FormsTest):

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
        self.assertRaisesMessage(ValueError, F.error_messages['notexists'], F)
        self.assertRaisesMessage(TypeError,
            unicode(F.error_messages['notanime']).format(type(UserStatusBundle).__name__),
            F, instance=UserStatusBundle.objects.get(id=1))
        anime = AnimeItem.objects.get(id=1)
        f = F(files={'text': 'file'}, instance=anime)
        self.assertEquals(f.is_valid(), False)
        filename = os.path.join(settings.MEDIA_ROOT, 'test', '1px.png')
        resultname = os.path.join(settings.MEDIA_ROOT, '1619e0741c0526b10c74eda382595812bd6679adf84.png')
        if os.path.exists(resultname):
            os.unlink(resultname)
        with open(filename, 'r') as fl:
            f = F(files={'text': SimpleUploadedFile(filename, fl.read())}, instance=anime)
            self.assertEquals(f.is_valid(), True)
            fl.seek(0)
            f = F(files={'text': SimpleUploadedFile(filename, fl.read())}, instance=anime)
            self.assertEquals(f.is_valid(), False)
            self.assertEquals(f.errors['text'][0], F.error_messages['loaded'])
            os.unlink(resultname)
            # Emulate system problems
            mode = (os.stat(settings.MEDIA_ROOT).st_mode & 0777)
            try:
                os.chmod(settings.MEDIA_ROOT, 444)
                fl.seek(0)
                f = F(files={'text': SimpleUploadedFile(filename, fl.read())}, instance=anime)
                self.assertEquals(f.is_valid(), False)
                self.assertEquals(f.errors['text'][0],
                    "[Errno 13] Permission denied: u'{0}'".format(resultname))
            except:
                raise
            finally:
                os.chmod(settings.MEDIA_ROOT, mode)

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


class FormsDynamicTests(FormsTest):

    fixtures = ['2trash.json']

    def setUp(self):
        pass

    def test_AnimeBundleForm(self):
        F = createFormFromModel(AnimeBundle)
        self.assertRaisesMessage(ValueError,
            F.error_messages['noinstance'], F)
        self.assertRaisesMessage(TypeError,
            F.error_messages['badinstance'].format(
                AnimeRequest.__name__, AnimeBundle.__name__), F,
                instance=AnimeRequest(anime=AnimeItem.objects.get(id=1),
                    text="0", requestType=1, status=2,))
        self.assertRaisesMessage(AttributeError,
                    "'bool' object has no attribute 'keys'", F, True,
                    instance=AnimeBundle())
        f = F(instance=AnimeBundle())
        self.assertEquals(f.is_valid(), False)
        #One item
        f = F({'Bundle 0': u'1'}, instance=AnimeBundle())
        self.assertEquals(f.is_valid(), False)
        self.assertEquals(f.non_field_errors()[-1],
                          f.error_messages['one_item'])
        #Similar items and wrong field number
        f = F({'Bundle 0': u'1', 'Bundle 69': u'1'}, instance=AnimeBundle())
        self.assertEquals(f.is_valid(), False)
        self.assertEquals(f.errors['Bundle 0'][-1],
                          f.error_messages['not_unique'])
        self.assertEquals(f.errors['Bundle 69'][-1],
                          f.error_messages['equal_item'])
        #Currentid for item not in form
        f = F({'Bundle 0': u'1', 'Bundle 2': u'2', 'currentid': u'3'}, instance=AnimeBundle())
        self.assertEquals(f.is_valid(), False)
        self.assertEquals(f.non_field_errors()[-1],
                          f.error_messages['no_item'])
        #Currentid without data
        f = F({'currentid': '1'}, instance=AnimeBundle.objects.get(id=1))
        self.assertEquals(f.is_valid(), False)
        #Bad data
        #TODO: Add more getDataCount tests
        self.assertEquals(f.getDataCount({},'Bundle ', None), (1, []))
        #Test setFields
        f.setFields({'f': 1, 's': 1})
        self.assertEquals((f.fields['f'], f.fields['s']), (1, 1))

    def test_AnimeNameForm(self):
        F = createFormFromModel(AnimeName)
        self.assertRaisesMessage(ValueError,
                F.error_messages['notexist'], F,
                instance=AnimeItem(releasedAt="1987-9-30 00:00",
                episodesCount=230, title='d', releasedKnown=0,
                releaseType=5, endedKnown=0, duration=17))
        f = F(instance=AnimeItem.objects.get(id=1))
        self.assertEquals(f.is_valid(), False)
        f = F({'Name 0': 'd'}, instance=AnimeItem.objects.get(id=1))
        self.assertEquals(f.is_valid(), True)

    def test_AnimeLinksForm(self):
        F = createFormFromModel(AnimeLink)
        f = F(instance=AnimeItem.objects.get(id=1))
        self.assertEquals(f.is_valid(), False)
        f = F({'Link 0': 'a'}, instance=AnimeItem.objects.get(id=1))
        self.assertEquals(f.is_valid(), False)
        self.assertEquals(f.errors['Link 0'][-1],
                    f.fields['Link 0'].error_messages['notype'])
        self.assertEquals(f.errors['Link type 0'][-1],
                    f.fields['Link type 0'].error_messages['required'])
        f = F({'Link 0': 'a', 'Link type 0': '1'},
                instance=AnimeItem.objects.get(id=1))
        self.assertEquals(f.is_valid(), False)
        self.assertEquals(f.errors['Link 0'][-1],
                    f.fields['Link 0'].error_messages['badlink'])
        #One of links is bad
        f = F({'Link 0': u'www.example.com', 'Link type 0': u'0',
               'Link 1': u'www.example.com', 'Link type 1': u'1'},
                instance=AnimeItem.objects.get(id=1))
        self.assertEquals(f.is_valid(), False)
        self.assertEquals(f.errors['Link 1'][-1],
                    f.fields['Link 1'].error_messages['badlink'])
        #Test for clean_<field>
        f = F({'Link 0': u'www.example.com', 'Link type 0': u'0'},
                instance=AnimeItem.objects.get(id=1))
        def tmp(s):
            raise ValidationError('Clean failed')
        setattr(f, 'clean_Link 0', tmp)
        self.assertEquals(f.is_valid(), False)
        self.assertEquals(f.errors['Link 0'][-1], 'Clean failed')
        f = F({'Link 0': u'www.example.com', 'Link type 0': u'0'},
                instance=AnimeItem.objects.get(id=1))
        def tmp(s):
            return 'Clean success'
        setattr(f, 'clean_Link 0', tmp)
        self.assertEquals(f.is_valid(), True)
        #All ok
        f = F({'Link 0': u'www.example.com', 'Link type 0': u'0'},
                    instance=AnimeItem.objects.get(id=1))
        self.assertEquals(f.is_valid(), True)


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


class FormsFieldsTests(FormsTest):

    fixtures = ['2trash.json']

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
        filename = os.path.join(settings.MEDIA_ROOT, 'test', '1px.png')
        with open(filename, 'r') as fl:
            data = SimpleUploadedFile(filename, fl.read())
            self.assertEquals(f.to_python(data), data)
        filename = os.path.join(settings.MEDIA_ROOT, 'test', '1px.tga')
        with open(filename, 'r') as fl:
            data = SimpleUploadedFile(filename, fl.read())
            self.assertRaisesMessage(ValidationError,
                f.error_messages['invalid_image'].format(
                f.error_messages['bad_format']), f.to_python, data)
        filename = os.path.join(settings.MEDIA_ROOT, 'test', '801px.png')
        with open(filename, 'r') as fl:
            data = SimpleUploadedFile(filename, fl.read())
            self.assertRaisesMessage(ValidationError,
                f.error_messages['invalid_image'].format(
                f.error_messages['big_image']), f.to_python, data)
        filename = os.path.join(settings.MEDIA_ROOT, 'test', 'random.jpg')
        with open(filename, 'r') as fl:
            data = TemporaryUploadedFile(filename, 'image/jpeg', 1024, None)
            self.assertRaisesMessage(ValidationError,
                f.error_messages['invalid_image'].format(
                u'Cannot identify image file'), f.to_python, data)

class FormsJSONTests(FormsTest):

    fixtures = ['2trash.json']

    def test_is_iterator(self):
        from itertools import chain
        for item in (list(), tuple(), chain()):
            self.assertEquals(json.is_iterator(item), True)
        self.assertEquals(json.is_iterator(True), False)

    def test_prepare_data(self):
        from datetime import datetime, date
        from django.utils.functional import lazy
        self.assertEquals(json.prepare_data('a', -1), u'a')
        for item in [u'a', 1, 1.0, 1+1j, True, None]:
            self.assertEquals(json.prepare_data(item), item)
        now = datetime.now()
        today = date.today()
        self.assertEquals(json.prepare_data(now), now.strftime(fields.DATE_FORMATS[0]))
        self.assertEquals(json.prepare_data(today), today.strftime(fields.DATE_FORMATS[0]))
        self.assertEquals(json.prepare_data([1]), [1])
        self.assertEquals(json.prepare_data({1: 1}), {1: 1})
        o = object()
        self.assertEquals(json.prepare_data(o), unicode(o))

    def test_FormSerializer(self):
        self.assertRaisesMessage(TypeError,
            'Form instance has bad type.', json.FormSerializer, None)
        f = createFormFromModel(AnimeItem)(instance=AnimeItem.objects.get(id=1))
        json.FormSerializer(f)
        #TODO: full test

