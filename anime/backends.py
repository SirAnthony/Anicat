
from django.contrib.auth.backends import ModelBackend
from django.contrib.auth.models import User

class EmailLoginBackend(ModelBackend):
    def authenticate(self, username=None, password=None):
        try:
            user = User.objects.get(email=username.lower())
            if user.check_password(password):
                return user
        except (User.DoesNotExist, User.MultipleObjectsReturned):
            pass
        return None
