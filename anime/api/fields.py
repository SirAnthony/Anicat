
import datetime
from decimal import Decimal
from django.forms import fields, ModelMultipleChoiceField
from anime.api.types import MultiType, FileType, WidgetFieldType, Noneable
from anime.forms import fields as afields


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
    fields.TypedChoiceField: int,
    fields.MultipleChoiceField: list,
    fields.MultiValueField: unicode,
    ModelMultipleChoiceField: list,
    afields.UnknownDateField: MultiType(datetime.datetime, unicode),
    afields.FilterIntegerField: WidgetFieldType,
    afields.FilterUnknownDateField: MultiType(datetime.datetime, unicode),
}


widgetTypes = {
    afields.FilterWidget: ((0, int), (1, Noneable(int)), (2, Noneable(bool)))
}


def guess_type(field):
    tp = type(field)
    for item, value in fieldTypes.items():
        if tp == item:
            return value
    return unicode


def guess_by_widget(name, field):
    tp = type(field.widget)
    for item, value in widgetTypes.items():
        if tp == item:
            return dict([('{0}_{1}'.format(name, index), t) for index, t in value])
    return unicode
