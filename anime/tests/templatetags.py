
from django.template import Template, Context, TemplateSyntaxError

from anime.forms.ModelError import AnimeForm
from anime.forms.User import NotActiveAuthenticationForm, UserCreationFormMail
from anime.models import USER_STATUS
from anime.tests._classes import CleanTestCase as TestCase
from anime.templatetags import animefilters


class AnimeFiltersTest(TestCase):

    def test_hash(self):
        self.assertEquals(animefilters.hash({1: True}, True), True)


class AnimeTemplatesTest(TestCase):

    def test_animeform_loginform(self):
        c = Context()
        self.assertEquals(Template(
            '{% load animetemplates %}{% addForm %}').render(c), '')
        self.assertEquals(type(c['AddForm']), AnimeForm)
        self.assertEquals(Template(
            '{% load animetemplates %}{% loginForm %}').render(c), '')
        self.assertEquals(type(c['LoginForm']), NotActiveAuthenticationForm)
        self.assertEquals(type(c['RegisterForm']), UserCreationFormMail)

    def test_username(self):
        c = Context({'a': None})
        self.assertEquals(Template(
            '{% load animetemplates %}{% username a %}').render(c), 'Anonymous')
        self.assertRaises(TemplateSyntaxError, Template,
            '{% load animetemplates %}{% username %}')

    def test_userstatus(self):
        c = Context({'a': None})
        self.assertEquals(Template(
            '{% load animetemplates %}{% statusname 1 %}').render(c), USER_STATUS[1][-1])
        self.assertEquals(Template(
            '{% load animetemplates %}{% statusname 9d %}').render(c), 'Bad status')
        self.assertRaises(TemplateSyntaxError, Template,
            '{% load animetemplates %}{% statusname %}')
