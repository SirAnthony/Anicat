from anime.forms import AnimeForm
from django import template

register = template.Library()

def addForm(parser, token):
    return AddFormNode() 

class AddFormNode(template.Node):
    def render(self, context):
        context['AddForm'] = AnimeForm()
        return ''

register.tag('addForm', addForm)
