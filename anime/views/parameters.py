
from django.contrib.auth.models import User
from django.db.models.fields import FieldDoesNotExist
from django.http import Http404
from anime.models import USER_STATUS


class ParametrizedView(object):

    parameters = []

    def check_field(self, model, field, fn=None):
        try:
            model._meta.get_field(field)
        except (FieldDoesNotExist, TypeError, AttributeError):
            if not fn or not fn(field):
                raise AttributeError

    def check_additional(self, field):
        return field in self.ADDITIONAL_FIELDS

    def check_user(self, request, user):
        if user is None or int(user) == request.user.id:
            user = request.user
        else:
            user = User.objects.get(id=user)
        return user

    def check_status(self, request, status):
        try:
            status = int(status)
            USER_STATUS[status]
            if not self.user.is_authenticated():
                raise Exception
        except:
            status = None
        return status

    def check_order(self, request, order):
        fn = None
        if getattr(self, 'ADDITIONAL_FIELDS', None):
            fn = self.check_additional

        order_field = order[1:] if order.startswith('-') else order
        self.check_field(self.model, order_field, fn)
        return order

    def check_string(self, request, string):
        if request.method == 'GET':
                string = string.replace('+', ' ')
        string = string.strip()
        if not string:
            raise AttributeError
        return string

    def check_page(self, request, page):
        return int(page)

    def check_parameters(self, request, *args, **kwargs):
        _get = lambda val, default=None: \
        kwargs.get(val) or request.POST.get(val) or default

        errors = self.error_messages
        for parameter, default, error in self.parameters:
            checker = getattr(self, 'check_' + parameter)
            try:
                val = checker(request, _get(parameter, default))
                setattr(self, parameter, val)
            except:
                raise Http404(errors[error])