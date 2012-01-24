
import re
from django.contrib.auth import authenticate
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.core.exceptions import ValidationError
from django import forms
from django.utils.translation import ugettext_lazy as _
from hashlib import sha1

def safe_username(email):
    return re.sub(r"[^a-z]+", '-', email[:email.index('@')]).strip('-')

def username_for_email(email, max_length=30):
    h = sha1()
    email = email.lower()
    h.update(email)
    s = safe_username(email)
    return "%s-%s" % (s[:max_length - 8], h.hexdigest()[:7])


class UserCreationFormMail(forms.ModelForm):
    error_messages = {
        'duplicate_email': _("This email is already in use."),
        'password_mismatch': _("The two password fields didn't match."),
    }

    email = forms.EmailField(label=_("E-mail address"))
    password1 = forms.CharField(label=_("Password"),
        widget=forms.PasswordInput)
    password2 = forms.CharField(label=_("Password confirmation"),
        widget=forms.PasswordInput,
        help_text = _("Enter the same password as above, for verification."))

    def __init__(self, *args, **kwargs):
        super(UserCreationFormMail, self).__init__(*args, prefix='register', **kwargs)

    def clean_email(self):
        email = self.cleaned_data['email']
        users = User.objects.filter(email=email)
        if users.count() > 0:
            raise forms.ValidationError(self.error_messages['duplicate_email'])
        return email

    def clean_password2(self):
        password1 = self.cleaned_data.get("password1", "")
        password2 = self.cleaned_data["password2"]
        if password1 != password2:
            raise forms.ValidationError(
                self.error_messages['password_mismatch'])
        return password2

    def save(self, commit=True):
        user = super(UserCreationFormMail, self).save(commit=False)
        user.set_password(self.cleaned_data["password1"])
        user.username = username_for_email(self.cleaned_data["email"])
        user.is_active = False
        if commit:
            user.save()
        return user

    class Meta:
        model = User
        fields = ('email', )


class NotActiveAuthenticationForm(AuthenticationForm):

    def clean(self):
        username = self.cleaned_data.get('username')
        password = self.cleaned_data.get('password')
        if username and password:
            self.user_cache = authenticate(username=username, password=password)
            if self.user_cache is None:
                raise ValidationError(_("Please enter a correct username and password. Note that both fields are case-sensitive."))
        self.check_for_test_cookie()
        return self.cleaned_data
