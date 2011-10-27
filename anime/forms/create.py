
from anime.models import AnimeBundle, AnimeItem, AnimeName, UserStatusBundle, AnimeLink, \
                         AnimeRequest, AnimeItemRequest, AnimeImageRequest, AnimeFeedbackRequest
from anime.forms.ModelError import ErrorModelForm, AnimeForm, UserStatusForm
from anime.forms.Dynamic import AnimeBundleForm, AnimeNameForm, AnimeLinksForm
from anime.forms.Request import PureRequestForm, AnimeItemRequestForm, ImageRequestForm, FeedbackForm

__all__ = ['createFormFromModel']

EDIT_FORMS = {
    AnimeBundle: AnimeBundleForm,
    AnimeItem: AnimeForm,
    AnimeName: AnimeNameForm,
    AnimeLink: AnimeLinksForm,
    UserStatusBundle: UserStatusForm,
    AnimeRequest: PureRequestForm,
    AnimeItemRequest: AnimeItemRequestForm,
    AnimeImageRequest: ImageRequestForm,
    AnimeFeedbackRequest: FeedbackForm,
}

def createFormFromModel(model, fields=None):
    parent = ErrorModelForm
    if model in EDIT_FORMS:
        parent = EDIT_FORMS[model]
    m = model
    f = fields
    #raise Exception
    class _ModelForm(parent):
        __fields = f
        def __init__(self, *args, **kwargs):
            super(_ModelForm, self).__init__(*args, **kwargs)
            if self.__fields:
                for fieldname in self.fields.keys():
                    if fieldname not in self.__fields:
                        del self.fields[fieldname]

        class Meta(parent.Meta):
            model = m
            fields = f
    return _ModelForm
