from anime.forms.ModelError import AnimeForm
from anime.forms.User import NotActiveAuthenticationForm, UserCreationFormMail
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
        context['LoginForm'] = NotActiveAuthenticationForm()
        context['RegisterForm'] = UserCreationFormMail()
        return ''

register.tag('addForm', addForm)
register.tag('loginForm', loginForm)

