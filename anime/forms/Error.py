
from django.forms import Form, BooleanField, FileField, \
                         MultipleChoiceField, ModelMultipleChoiceField
from django.forms.widgets import SelectMultiple
from anime.forms.fields import FilterWidget, FilterIntegerField, \
                               FilterUnknownDateField
from anime.models import Genre, ANIME_TYPES, USER_STATUS


class ErrorForm(Form):
    def addError(self, text):
        self.errors['__all__'] = self.error_class([text])


class UploadMalListForm(ErrorForm):
    file = FileField(max_length=200)
    rewrite = BooleanField(label='Overwrite existing data', required=False)


class FilterForm(ErrorForm):
    episodesCount = FilterIntegerField(label="Episodes", required=False,
                        widget=FilterWidget)
    duration = FilterIntegerField(label="Duration", required=False,
                        widget=FilterWidget)
    releasedAt = FilterUnknownDateField(label='Released', required=False)
    endedAt = FilterUnknownDateField(label='Ended', required=False)
    releaseType = MultipleChoiceField(label="Type", required=False,
        choices=ANIME_TYPES, widget=SelectMultiple(attrs={
            'id': 'id_filter_releaseType', 'class': 'scrollcontent'}))
    state = MultipleChoiceField(label="State", required=False,
        choices=USER_STATUS, widget=SelectMultiple(attrs={
            'id': 'id_filter_state', 'class': 'scrollcontent'}))
    genre = ModelMultipleChoiceField(label="Type", required=False,
        queryset=Genre.objects.all(),
        widget=SelectMultiple(attrs={'id': 'id_filter_genre', 'class': 'scrollcontent'}))
