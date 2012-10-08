
import datetime
from decimal import Decimal
from django.forms import fields, ModelMultipleChoiceField
from anime.forms import fields as afields


class MultiType(object):
    def __init__(self, *args):
        self.types = args

    def __unicode__(self):
        return u' or '.join([arg.__name__ for arg in self.types])
    __name__ = property(__unicode__)


class FileType(object):

    def __unicode__(self):
        return u'file'
    __name__ = property(__unicode__)


fieldTypes = {
    fields.CharField: unicode,
    fields.IntegerField: int,
    fields.FloatField: float,
    fields.DecimalField: Decimal,
    fields.DateField: MultiType(datetime.date, unicode),
    fields.TimeField: MultiType(datetime.time, unicode),
    fields.DateTimeField: MultiType(datetime.datetime, unicode),
    fields.RegexField: unicode,
    fields.EmailField: unicode,
    fields.FileField: FileType(),
    fields.ImageField: FileType(),
    fields.URLField: unicode,
    fields.BooleanField: bool,
    fields.ChoiceField: int,
    fields.TypedChoiceField: list,
    fields.MultipleChoiceField: list,
    fields.MultiValueField: unicode,
    ModelMultipleChoiceField: list,
    afields.UnknownDateField: MultiType(datetime.datetime, unicode),
    afields.FilterIntegerField: int,
    afields.FilterUnknownDateField: MultiType(datetime.datetime, unicode),
}


def guess_type(field):
    tp = type(field)
    for item, value in fieldTypes.items():
        if tp == item:
            return value
    return unicode

