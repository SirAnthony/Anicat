from anime.forms.ModelError import AnimeForm, FilterForm
from anime.forms.User import NotActiveAuthenticationForm, UserCreationFormMail
from anime.models import Genre, ANIME_TYPES, USER_STATUS
from anime.core.user import get_username
from django import template

register = template.Library()


class AddFormNode(template.Node):
    def render(self, context):
        context['AddForm'] = AnimeForm()
        return ''


class LoginFormNode(template.Node):
    def render(self, context):
        context['LoginForm'] = NotActiveAuthenticationForm()
        context['RegisterForm'] = UserCreationFormMail()
        return ''


class FilterFormNode(template.Node):
    def render(self, context):
        context['FilterForm'] = FilterForm
        return ''


register.tag('addForm', lambda parser, token: AddFormNode())
register.tag('loginForm', lambda parser, token: LoginFormNode())
register.tag('filterForm', lambda parser, token: FilterFormNode())



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

register.tag('username', username)
register.tag('statusname', statusname)


