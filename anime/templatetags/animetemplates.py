from anime.forms import AnimeForm
from django.contrib.auth.forms import AuthenticationForm
from django import template

register = template.Library()

def addForm(parser, token):
    return AddFormNode() 

class AddFormNode(template.Node):
    def render(self, context):
        context['AddForm'] = AnimeForm()
        return ''

def loginForm(parser, token):
    return loginFormNode() 

class loginFormNode(template.Node):
    def render(self, context):
        context['LoginForm'] = AuthenticationForm()
        return ''

register.tag('addForm', addForm)
register.tag('loginForm', loginForm)