from anime.forms.ModelError import AnimeForm
from anime.forms.User import NotActiveAuthenticationForm, UserCreationFormMail
from anime.models import USER_STATUS
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
        self.user = template.Variable(user)
    def render(self, context):
        return get_username(self.user.resolve(context))


def statusname(parser, token):
    try:
        tag_name, status = token.split_contents()
    except ValueError:
        raise template.TemplateSyntaxError("%r tag requires exactly one argument" % token.contents.split()[0])
    return StatusNameNode(status)


class StatusNameNode(template.Node):
    def __init__(self, status):
        self.status = template.Variable(status)
    def render(self, context):
        try:
            return USER_STATUS[int(self.status.resolve(context))][1]
        except:
            return u"Bad status"


register.tag('addForm', addForm)
register.tag('loginForm', loginForm)
register.tag('username', username)
register.tag('statusname', statusname)


