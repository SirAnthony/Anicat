from anime.forms.ModelError import AnimeForm
from anime.forms.User import NotActiveAuthenticationForm, UserCreationFormMail
from anime.user import get_username
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

def username(parser, token):
    try:
        tag_name, user = token.split_contents()
    except ValueError:
        raise template.TemplateSyntaxError("%r tag requires exactly one argument" % token.contents.split()[0])

    return UsernameNode(user)

class UsernameNode(template.Node):
    def __init__(self, user):
        self.name = template.Variable(user)
    def render(self, context):
        return get_username(self.name.resolve(context))


register.tag('addForm', addForm)
register.tag('loginForm', loginForm)
register.tag('username', username)

