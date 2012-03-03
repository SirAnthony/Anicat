
import re
from hashlib import sha1
from django.conf import settings
from anime.utils.config import random_string


def is_iterator(obj):
    if isinstance(obj, (list, tuple)):
        return True
    try:
        iter(obj)
        return True
    except TypeError:
        return False


def safe_username(email):
    return re.sub(r"[^a-z]+", '-', email[:email.index('@')]).strip('-')


def username_for_email(email, max_length=30):
    h = sha1()
    email = email.lower()
    h.update(email)
    s = safe_username(email)
    return "%s-%s" % (s[:max_length - 8], h.hexdigest()[:7])


def new_user(sender, user, response, details, **kwargs):
    password = generate_password()
    user.set_password(password)
    if getattr(user, 'email', None):
        mail(user.email, {'username': user.username, 'password': password, 'openid': True},
                    'anime/user/welcome.txt', 'anime/user/registred_email.html')
    return True


def generate_password():
    return random_string([u'bcdfgklmnprstxz', u'aejioqvuwy',
                          u'BCDFGKLMNPRSTXZ', u'AEJIOQVUWY',
                          u'123456789', ur''''"{}()[]._-$#&'''], end=2)


def mail(to, data={}, subject_template_name='email_subject.txt',
        email_template_name='email.html',
        from_email=settings.DEFAULT_FROM_EMAIL):

    from django.core.mail import send_mail
    from django.template import loader

    c = {'email': to}
    c.update(data)

    subject = loader.render_to_string(subject_template_name, c)
    # Email subject *must not* contain newlines
    subject = ''.join(subject.splitlines())
    email = loader.render_to_string(email_template_name, c)
    send_mail(subject, email, from_email, [to], fail_silently=True)
